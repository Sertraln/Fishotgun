from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import CardMaker, Vec3,WindowProperties

class HarePoonApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        # Load the environment model.

        self.center_mouse()

        cm = CardMaker("plane")
        cm.setFrame(-1, 1, -1, 1)  # taille du plan (gauche, droite, bas, haut)

        plane = self.render.attachNewNode(cm.generate())
        plane.setPos(0, 5, 0)       # position dans la scène
        plane.setHpr(0, -90, 0)     # rotation pour qu’il soit horizontal (face vers le haut)
        plane.setScale(2)           # mise à l’échelle

        # Optionnel : ajout d’une couleur
        plane.setColor(0.5, 0.8, 0.5, 1)
        plane.setTwoSided(True)
        player = self.loader.loadModel("models/box")
        player.reparent_to(self.render)
        player.setPos(0,5,0)
        player.setColor(0.2,0.6,0.9, 1)
        player.setScale(1,1,2)
        
        self.cam.setPos(0, -1, 5)
        self.cam.lookAt(plane) 
        # Apply scale and position transforms on the model.
        self.taskMgr.add(self.cameraRotation,"RotationControlTask")
        self.taskMgr.add(self.movement,"positionControlTask")

    def center_mouse(self):
        props = WindowProperties()
        props.set_cursor_hidden(True)
        props.setMouseMode(WindowProperties.M_relative)
        self.win.requestProperties(props)

    def cameraRotation(self, task):
        if self.mouseWatcherNode.hasMouse():
            x = self.mouseWatcherNode.getMouseX()
            y = self.mouseWatcherNode.getMouseY()
            xRot = x * 6.0
            yRot = y * 6.0
            print(f"Mouse pos: {x}, {y}")
            self.camera.set_hpr(xRot, yRot,0)

        return Task.cont

    def movement(self,task):
        return Task.cont



app = HarePoonApp()
app.run()
