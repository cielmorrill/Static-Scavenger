from .entity_baseclass import Entity
from pygame import Rect
from utils.vector import vec
from entities.explosion import Explosion

class Bomb_Rock(Entity):
    def __init__(self, position, fileName="bomb_rock.png", offset=(0,0), maxSpeed=0, row = 0, nFrames = 1):
        super().__init__(position, fileName, offset, maxSpeed, row, nFrames)

        self.animate = False
        self.moving = False
        self.frame  = 0
        self.setFPS(8)
        self.createShadow(width_scale=.95)

        self.collisionRect = Rect(4,8,int(self.getWidth() - 8),int(self.getHeight() - 12))

        self.isDamaged = False
        self.isAlive = True
        self.removeMe = False

        # stats
        self.maxHealth = 1000.0
        self.health = self.maxHealth

        self.counter = 0

    def getShadowPos(self):
        shadow_pos = super().getShadowPos()
        
        shadow_pos[1] -= 6

        return shadow_pos
    
    def getHurt(self, attack, attackerPos):
        if self.isInvincible or self.isDamaged or not self.isAlive:
            return

        self.isDamaged = True

    def updateHurtState(self, seconds):
        if self.isDamaged:
            self.animateState = "isHurt"
            self.animate = True
            self.nFrames = 5
            self.isInvincible = True
            self.isDamaged = False
        if self.frame >= 4:
            self.setExploding()

    def setExploding(self):
        if self.animateState != "isExploding":
            self.animateState = "isExploding"
            self.row = 1
            self.frame = 0
            self.nFrames = 2
            self.counter = 0
        if self.counter >= 3:
            self.callExplosion()
            self.removeMe = True

    def callExplosion(self):
        pos = vec(0,0)
        pos[0] = self.position[0] - self.getWidth()/2
        pos[1] = self.position[1] - self.getHeight()/2
        explosion = Explosion(pos)
        self.hurtable.append(explosion)

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
        
    def update(self, seconds, tmx_map):
        if self.animateState == "isExploding":
            self.setExploding()

        super().update(seconds, tmx_map)

        self.counter += seconds