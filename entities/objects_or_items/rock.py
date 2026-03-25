from pygame.locals import Rect
from utils.soundManager import SoundManager
from utils.vector import vec, rectAdd
from ..entity_baseclass.object_class import Object_Class
from utils.spriteManager import SpriteManager

"""Rocks."""
# rocks must have:
    # states (animation, action, direction, hurt, dying)
    # stats (health/max, attack)
    # collision (world boundaries, other entities)

class Rock(Object_Class):
    def __init__(self, position, fileName="", offset=(0,0), maxSpeed=0, row = 0, nFrames = 1):
        super().__init__(position, fileName, offset, maxSpeed, row, nFrames)

        self.animate = False
        self.frame  = 0
        self.createShadow(width_scale=.95)

        self.collisionRect = Rect(4,8,int(self.getWidth() - 8),int(self.getHeight() - 12))

        self.isDamaged = False
        self.isAlive = True
        self.removeMe = False

        # stats
        self.maxHealth = 100.0
        self.health = self.maxHealth
        self.hurtTimerBase = 1.0
        self.hurtTimer = 1.0

        self.counter = 0

    def getShadowPos(self):
        shadow_pos = super().getShadowPos()
        
        shadow_pos[1] -= 6

        return shadow_pos

    def setDying(self, seconds):
        self.row = 4
        self.image = SpriteManager.getInstance().getSprite(self.fileName, (self.row, self.frame))
        sm = SoundManager.getInstance()
        sm.playSFX("rock_destroy.mp3")
        super().setDying(seconds)

    def getHurt(self, attack, attackerPos):
        super().getHurt(attack, attackerPos)
        sm = SoundManager.getInstance()
        sm.playSFX("rock_hit.wav")
        
    def updateHurtState(self, seconds):
        super().updateHurtState(seconds)

        # update damage frame
        health_ratio = self.health / self.maxHealth
        row = min(int((1 - health_ratio) * 4), 3)
        if self.health <= 0:
                row = 4
        self.row = row
        self.image = SpriteManager.getInstance().getSprite(self.fileName, (self.row, self.frame))