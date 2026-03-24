from pygame.locals import Rect
from entities.objects_or_items.treasure_chest_lid import Treasure_Chest_Lid
from utils.soundManager import SoundManager
from utils.vector import vec, rectAdd
from ..entity_baseclass.entity import Entity
from utils.spriteManager import SpriteManager

class Treasure_Chest(Entity):
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
    
    def resolveCollision(self, e2):
        rect1 = self.getCollisionRect()
        rect2 = e2.getCollisionRect()

        collision = rect1.clip(rect2)

        if collision.width == 0 or collision.height == 0:
            return

        if collision.width < collision.height:
            # horizontal collision
            e2.velocity[0] = 0
            if rect2.centerx < rect1.centerx:
                e2.setPosition((rect1.left - e2.getWidth(), e2.getPosition()[1]))
            else:
                e2.setPosition((rect1.right, e2.getPosition()[1]))
        else:
            # vertical collision
            e2.velocity[1] = 0
            if rect2.centery < rect1.centery:
                e2.setPosition((e2.getPosition()[0], rect1.top - e2.getHeight()))
            else:
                e2.setPosition((e2.getPosition()[0], rect1.bottom))

    def draw(self, drawSurface):
        super().draw(drawSurface)
        self.lid.draw(drawSurface)

    def update(self, seconds, tmx_map):
        super().update(seconds, tmx_map)
        self.lid.update(seconds, tmx_map)