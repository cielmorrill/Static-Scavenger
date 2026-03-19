from utils.spriteManager import SpriteManager
from utils.vector import vec
from .drawable import Drawable

class Menu_Item(Drawable):
    def __init__(self, position=vec(0,0), fileName="", offset=None):
        super().__init__(position, fileName, offset)
        self.fileName = fileName
        if fileName != "":
            sm = SpriteManager.getInstance()
            self.image = sm.getSprite(fileName, offset)
        
        self.position=vec(*position)

    def draw(self, drawSurface):
        drawSurface.blit(self.image, self.position)