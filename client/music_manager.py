from ursina import Entity
import client.data as g

class MusicManager(Entity):
    def __init__(self):
        super().__init__(ignore_paused=True)
        self._paused = False
        self._started = False
        self._first = True

    def start(self):
        """Démarre ou reprend la playlist."""
        if self._started:
            # Déjà démarrée : juste reprendre
            if self._paused and g.current_music:
                g.current_music.resume()
                self._paused = False
        else:
            # Première fois : démarrer depuis life_is_awesome
            self._started = True
            self._paused = False
            self._first = True
            g.current_music = g.life_is_awesome
            g.current_music.play()

    def pause_playlist(self):
        """Met la playlist en pause."""
        if self._started and not self._paused and g.current_music:
            g.current_music.pause()
            self._paused = True

    def update(self):
        if not self._started or self._paused:
            return

        if g.current_music and not g.current_music.playing:
            self._first = False
            g.play_random_music()