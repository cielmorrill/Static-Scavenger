from pygame.locals import Rect
from utils.vector import vec, rectAdd
from ..entity_baseclass.entity import Entity
from utils.spriteManager import SpriteManager

"""Rocks."""
# rocks must have:
    # states (animation, action, direction, hurt, dying)
    # stats (health/max, attack)
    # collision (world boundaries, other entities)

class Big_Rock(Entity):
    def __init__(self, position, fileName="", offset=(0,0), maxSpeed=0, row = 0, nFrames = 1):
        super().__init__(position, fileName, offset, maxSpeed, row, nFrames)

        self.animate = False
        self.frame  = 0
        self.createShadow(width_scale=.95)

        self.collisionRect = Rect(4,4,int(self.getWidth() - 8),int(self.getHeight() - 8))

        self.isDamaged = False
        self.isAlive = True
        self.removeMe = False

        # stats
        self.maxHealth = 300.0
        self.health = self.maxHealth
        self.hurtTimerBase = 1.0
        self.hurtTimer = 1.0

        self.counter = 0

    def getCollisionRect(self):
        return rectAdd(self.getPosition(), self.collisionRect)

    def getShadowPos(self):
        shadow_pos = super().getShadowPos()
        
        shadow_pos[1] -= 6

        return shadow_pos

    def setDying(self, seconds):
        self.row = 4
        self.image = SpriteManager.getInstance().getSprite(self.fileName, (self.row, self.frame))
        self.isAlive = False
        self.shadow = None
        self.setDead(seconds)

    def setDead(self, seconds):
        self.isAlive = False
        self.animate = False
        if self.death_timer > 0:
            self.death_timer -= 1 * seconds

            fade_ratio = self.death_timer / self.death_timer_max
            alpha = int(255 * fade_ratio)
            alpha = max(0, min(255, alpha))

            self.image.set_alpha(alpha)
            return
        self.removeMe = True

    def getHurt(self, attack, attackerPos):
        if self.isInvincible or self.isDamaged or not self.isAlive:
            return

        self.isDamaged = True
        self.hurtTimer = self.hurtTimerBase
        self.health -= attack
        
    def updateHurtState(self, seconds):
        if self.isDamaged:
            self.hurtTimer -= seconds
            if self.hurtTimer <= 0:
                self.isDamaged = False
                self.hurtTimer = self.hurtTimerBase
            self.healthCooldownTimer = 0

        # update damage frame
        health_ratio = self.health / self.maxHealth
        row = min(int((1 - health_ratio) * 4), 3)
        if self.health <= 0:
                row = 4
        self.row = row
        self.image = SpriteManager.getInstance().getSprite(self.fileName, (self.row, self.frame))
        # print("rock row ", self.row)

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
        if self.health <= 0 or not self.isAlive:
            if self.isDamaged:
                self.isDamaged = False
            self.velocity = vec(0,0)
            self.setDying(seconds)
            self.isDamaged = False
            super().update(seconds, tmx_map)
            return
        # self.velocity = vec(0,0)
        self.updateHurtState(seconds)

        super().update(seconds, tmx_map)