from random import random
from pygame.locals import Rect
from utils.soundManager import SoundManager
from utils.vector import magnitude, vec, rectAdd
from ..entity_baseclass.entity import Entity
from utils.spriteManager import SpriteManager

class Treasure_Chest_Lid(Entity):
    def __init__(self, body, position, fileName="treasure_chest_lid.png", offset=(0,0), maxSpeed=0, row = 0, nFrames = 1):
        super().__init__(position, fileName, offset, maxSpeed, row, nFrames)

        self.animate = False
        self.body = body
        self.frame  = self.body.frame

        self.collisionRect = Rect(4,8,int(self.getWidth()),int(self.getHeight()))

        self.isDamaged = False
        self.removeMe = False

        # stats
        self.maxHealth = 100.0
        self.health = self.maxHealth
        self.hurtTimerBase = 1.0
        self.hurtTimer = 1.0

        self.counter = 0

        self.deathTarget = None
        self.deathVelocity = None

    def setDying(self, seconds):
        super().setDying(seconds)
        self.moving = True
        direction = vec(round(random.uniform(-1.2, 1.2), 2), round(random.uniform(.6, 1.5), 2))
        self.deathVelocity = direction * 200
        self.deathTarget = self.getPosition() + direction * 40

        self.position += self.deathVelocity * seconds
        self.deathVelocity *= 0.9

        # bounce when reaching target distance
        if magnitude(self.position - self.deathTarget) < 5:
            self.deathVelocity *= 0.5
            self.deathTarget = self.position  # only bounce once

        # stop tiny motion
        if magnitude(self.deathVelocity) < 10:
            self.deathVelocity = vec(0,0)
            self.setDead(seconds)

    def setDead(self, seconds):
        self.isAlive = False
        self.animate = False
        self.removeMe = True

    def update(self, seconds, tmx_map):
        super().update(seconds, tmx_map)

        if self.body.health <= 0:
            self.setDying(seconds)
            return