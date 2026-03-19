"""
PROOF OF CONCEPT - Client Prediction + Server Reconciliation
=============================================================
Simule un serveur tournant à 20fps et un client à 60fps avec latence.

Visuel :
  - Carré BLANC  = position locale (client-side prediction)
  - Carré ROUGE  = position brute reçue du serveur (sans reconciliation)
  - Carré VERT   = position après reconciliation + lerp  ← c'est ce qu'on vise
  - HUD          = stats en temps réel (latence simulée, tick, écart)

Contrôles : Z/Q/S/D ou W/A/S/D pour bouger, ESC pour quitter.
"""

from panda3d.core import (
    TextNode, Vec3, Point3, CardMaker, NodePath,
    WindowProperties, KeyboardButton
)
from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from direct.task import Task
import collections
import time
import random

# ─────────────────────────────────────────────
#  CONSTANTES
# ─────────────────────────────────────────────
CLIENT_FPS        = 60          # fréquence de mise à jour du client
SERVER_FPS        = 20          # fréquence de tick serveur
SPEED             = 5.0         # unités/seconde
SIM_LATENCY_MS    = 120         # latence aller-retour simulée (ms)
LATENCY_JITTER_MS = 30          # variation aléatoire de latence (ms)
SNAP_THRESHOLD    = 1.5         # distance max avant snap brutal (anti-cheat)
LERP_FACTOR       = 0.25        # vitesse de correction douce (0-1)

# ─────────────────────────────────────────────
#  SIMULATION DU SERVEUR (même processus, thread fictif)
# ─────────────────────────────────────────────
class FakeServer:
    """
    Simule le serveur : reçoit des inputs numérotés,
    recalcule la position, répond avec un délai simulé.
    """
    def __init__(self):
        self.pos          = Vec3(0, 0, 0)
        self.tick         = 0
        self.inbox        = []   # [(deliver_time, input_packet), ...]
        self.outbox       = []   # [(deliver_time, response_packet), ...]

    def send_input(self, input_packet):
        """Client → Serveur : ajoute l'input avec délai simulé."""
        latency = (SIM_LATENCY_MS + random.uniform(-LATENCY_JITTER_MS, LATENCY_JITTER_MS)) / 1000
        deliver_at = time.time() + latency / 2   # aller seulement
        self.inbox.append((deliver_at, input_packet))

    def update(self, dt):
        """Appelé à 20fps : traite les inputs reçus et envoie les réponses."""
        now = time.time()

        # Traiter tous les paquets arrivés
        remaining = []
        for (deliver_at, pkt) in self.inbox:
            if now >= deliver_at:
                self._process_input(pkt)
            else:
                remaining.append((deliver_at, pkt))
        self.inbox = remaining

    def _process_input(self, pkt):
        """Applique l'input et prépare la réponse."""
        dt = pkt['dt']
        move = pkt['move']
        self.pos += Vec3(move.x * SPEED * dt,
                         move.y * SPEED * dt,
                         0)
        self.tick = pkt['tick']

        # Réponse avec délai retour
        latency = (SIM_LATENCY_MS + random.uniform(-LATENCY_JITTER_MS, LATENCY_JITTER_MS)) / 1000
        deliver_at = time.time() + latency / 2   # retour seulement
        response = {
            'server_pos'  : Vec3(self.pos),
            'last_tick'   : self.tick,
        }
        self.outbox.append((deliver_at, response))

    def receive_response(self):
        """Client tente de lire une réponse du serveur."""
        now = time.time()
        for i, (deliver_at, pkt) in enumerate(self.outbox):
            if now >= deliver_at:
                self.outbox.pop(i)
                return pkt
        return None


# ─────────────────────────────────────────────
#  APPLICATION PANDA3D
# ─────────────────────────────────────────────
class NetcodePOC(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        # Fenêtre
        wp = WindowProperties()
        wp.setTitle("Netcode POC - Prediction + Reconciliation")
        wp.setSize(900, 700)
        self.win.requestProperties(wp)

        # Caméra 2D top-down
        self.disableMouse()
        self.camera.setPos(0, -30, 12)
        self.camera.lookAt(0, 0, 0)

        # ── Serveur simulé ──
        self.server = FakeServer()

        # ── État client ──
        self.client_pos       = Vec3(0, 0, 0)   # position prédite localement
        self.reconciled_pos   = Vec3(0, 0, 0)   # position après reconciliation
        self.raw_server_pos   = Vec3(0, 0, 0)   # position brute serveur (sans replay)
        self.client_tick      = 0
        self.pending_inputs   = collections.deque()  # inputs non confirmés
        self.server_tick_acc  = 0.0              # accumulateur pour tick serveur

        # ── Touches ──
        self.keys = {'up': False, 'down': False, 'left': False, 'right': False}
        self.accept('w',        self._key, ['up',    True])
        self.accept('w-up',     self._key, ['up',    False])
        self.accept('z',        self._key, ['up',    True])
        self.accept('z-up',     self._key, ['up',    False])
        self.accept('s',        self._key, ['down',  True])
        self.accept('s-up',     self._key, ['down',  False])
        self.accept('a',        self._key, ['left',  True])
        self.accept('a-up',     self._key, ['left',  False])
        self.accept('q',        self._key, ['left',  True])
        self.accept('q-up',     self._key, ['left',  False])
        self.accept('d',        self._key, ['right', True])
        self.accept('d-up',     self._key, ['right', False])
        self.accept('escape',   self.userExit)

        # ── Visuels ──
        self._build_scene()
        self._build_hud()

        # ── Tâche principale ──
        self.taskMgr.add(self._update, 'main_update')

    # ──────────────────────────────────────────
    #  CONSTRUCTION DE LA SCÈNE
    # ──────────────────────────────────────────
    def _make_square(self, name, r, g, b, size=0.5):
        cm = CardMaker(name)
        h = size / 2
        cm.setFrame(-h, h, -h, h)
        node = self.render.attachNewNode(cm.generate())
        node.setColor(r, g, b, 1)
        node.setPos(0, 0, 0)
        return node

    def _build_scene(self):
        # Grille de fond
        for x in range(-10, 11):
            for y in range(-10, 11):
                tile = self._make_square(f'tile_{x}_{y}', 0.12, 0.12, 0.18, 0.98)
                tile.setPos(x, y, -0.01)

        # Les trois représentations du joueur
        self.node_raw    = self._make_square('raw',    0.9, 0.2, 0.2)  # rouge  = serveur brut
        self.node_recon  = self._make_square('recon',  0.2, 0.9, 0.3)  # vert   = reconcilié
        self.node_client = self._make_square('client', 0.95, 0.95, 0.95) # blanc = prédiction locale
        self.node_client.setScale(0.8)   # légèrement plus petit pour distinguer

    def _build_hud(self):
        def txt(msg, pos, scale=0.05, fg=(1,1,1,1)):
            return OnscreenText(text=msg, pos=pos, scale=scale,
                                fg=fg, align=TextNode.ALeft,
                                mayChange=True)

        self.hud_title   = txt("■ BLANC=local  ■ VERT=reconcilié  ■ ROUGE=serveur brut",
                                (-1.3, 0.92), scale=0.045)
        self.hud_latency = txt("Latence : ---",  (-1.3,  0.82))
        self.hud_tick    = txt("Tick    : ---",  (-1.3,  0.76))
        self.hud_pending = txt("Pending : ---",  (-1.3,  0.70))
        self.hud_gap     = txt("Écart   : ---",  (-1.3,  0.64))
        self.hud_hint    = txt("Z/Q/S/D pour bouger — ESC quitter",
                                (-1.3, -0.90), scale=0.04, fg=(0.6,0.6,0.6,1))

    # ──────────────────────────────────────────
    #  TOUCHES
    # ──────────────────────────────────────────
    def _key(self, action, state):
        self.keys[action] = state

    # ──────────────────────────────────────────
    #  BOUCLE PRINCIPALE
    # ──────────────────────────────────────────
    def _update(self, task):
        dt = globalClock.getDt()

        # ── 1. Construire le vecteur de mouvement ──
        move = Vec3(0, 0, 0)
        if self.keys['up']:    move.y += 1
        if self.keys['down']:  move.y -= 1
        if self.keys['left']:  move.x -= 1
        if self.keys['right']: move.x += 1
        if move.lengthSquared() > 0:
            move.normalize()

        # ── 2. Prédiction locale (60fps) ──
        self.client_tick += 1
        input_packet = {
            'tick': self.client_tick,
            'move': Vec3(move),
            'dt'  : dt,
        }
        self.client_pos += Vec3(move.x * SPEED * dt,
                                move.y * SPEED * dt,
                                0)
        self.pending_inputs.append(input_packet)

        # ── 3. Envoyer l'input au serveur ──
        self.server.send_input(input_packet)

        # ── 4. Tick serveur (20fps via accumulateur) ──
        self.server_tick_acc += dt
        server_dt = 1.0 / SERVER_FPS
        while self.server_tick_acc >= server_dt:
            self.server.update(server_dt)
            self.server_tick_acc -= server_dt

        # ── 5. Réconciliation : lire la réponse serveur ──
        response = self.server.receive_response()
        if response:
            self._reconcile(response)

        # ── 6. Mettre à jour les visuels ──
        self.node_client.setPos(self.client_pos.x,     self.client_pos.y,     0.02)
        self.node_raw.setPos(   self.raw_server_pos.x, self.raw_server_pos.y, 0.01)
        self.node_recon.setPos( self.reconciled_pos.x, self.reconciled_pos.y, 0.01)

        # ── 7. HUD ──
        gap = (self.reconciled_pos - self.client_pos).length()
        self.hud_latency.setText(f"Latence simulée : {SIM_LATENCY_MS} ± {LATENCY_JITTER_MS} ms")
        self.hud_tick.setText(   f"Tick client     : {self.client_tick}")
        self.hud_pending.setText(f"Inputs pending  : {len(self.pending_inputs)}")
        self.hud_gap.setText(    f"Écart local/rec : {gap:.4f} u")

        return Task.cont

    # ──────────────────────────────────────────
    #  RÉCONCILIATION
    # ──────────────────────────────────────────
    def _reconcile(self, response):
        """
        Reçoit la position confirmée par le serveur au tick T.
        1. Enregistre la pos brute (carré rouge).
        2. Rejoue tous les inputs non confirmés depuis cette pos.
        3. Applique lerp ou snap selon l'écart.
        """
        server_pos  = response['server_pos']
        last_tick   = response['last_tick']

        # Position brute pour la comparaison visuelle
        self.raw_server_pos = Vec3(server_pos)

        # Supprimer les inputs déjà traités par le serveur
        while self.pending_inputs and self.pending_inputs[0]['tick'] <= last_tick:
            self.pending_inputs.popleft()

        # Rejouer les inputs non confirmés à partir de la pos serveur
        replayed_pos = Vec3(server_pos)
        for pkt in self.pending_inputs:
            m  = pkt['move']
            dt = pkt['dt']
            replayed_pos += Vec3(m.x * SPEED * dt,
                                 m.y * SPEED * dt,
                                 0)

        # Comparer avec la position locale actuelle
        gap = (replayed_pos - self.client_pos).length()

        if gap > SNAP_THRESHOLD:
            # ⚠ Écart trop grand → snap brutal (cheat ou désync sévère)
            self.reconciled_pos = Vec3(replayed_pos)
            self.client_pos     = Vec3(replayed_pos)   # force aussi le local
            print(f"[SNAP] tick={last_tick}  gap={gap:.3f}  → téléportation forcée")
        else:
            # Micro-écart → correction douce par interpolation
            self.reconciled_pos = self.reconciled_pos + \
                                  (replayed_pos - self.reconciled_pos) * LERP_FACTOR


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == '__main__':
    app = NetcodePOC()
    app.run()