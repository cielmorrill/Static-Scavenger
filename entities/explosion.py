from .entity_baseclass import Hurtable
from pygame import Rect

class Explosion(Hurtable):
    def __init__(self, position, fileName="explosion.png", offset=(0,0), maxSpeed=0, row = 0, nFrames = 5):
        super().__init__(position, fileName, offset, maxSpeed, row, nFrames)

        self.animate = True
        self.moving = False
        self.isInvincible = True
        self.removeMe = False
        self.row = 0
        self.frame  = 0
        self.setFPS(8)

        self.attackPower = 50

        self.collisionRect = Rect(0,0,int(self.getWidth()),int(self.getHeight()))

    def update(self, seconds):
        super().update(seconds)

        if self.frame >= self.nFrames - 1:
            self.removeMe = True
