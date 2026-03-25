from pygame.locals import Rect
from entities.objects_or_items.treasure_chest_lid import Treasure_Chest_Lid
from utils.soundManager import SoundManager
from ..entity_baseclass.object_class import Object_Class

class Treasure_Chest(Object_Class):
    def __init__(self, position, fileName="treasure_chest_bottom.png", offset=(0,0), maxSpeed=0, row = 0, nFrames = 1):
        super().__init__(position, fileName, offset, maxSpeed, row, nFrames)

        self.animate = False
        self.moving = False
        self.frame  = 0
        self.createShadow(width_scale=.95)

        self.lid = Treasure_Chest_Lid(self, self.position, "treasure_chest_lid.png", offset, maxSpeed, row, nFrames)

        self.collisionRect = Rect(4,8,int(self.getWidth()),int(self.getHeight()))

        self.isDamaged = False
        self.isInvincible = True
        self.removeMe = False

    def getShadowPos(self):
        shadow_pos = super().getShadowPos()
        
        shadow_pos[1] -= 6

        return shadow_pos

    def draw(self, drawSurface):
        super().draw(drawSurface)
        self.lid.draw(drawSurface)
    
    def handleEvent(self, event):
        super().handleEvent(event)
        self.lid.handleEvent(event)

    def update(self, seconds, tmx_map):
        super().update(seconds, tmx_map)
        self.lid.update(seconds, tmx_map)