from turtle import speed
from .animated import *
from utils.vector import vec, magnitude, scale
from pygame.locals import *

class Mobile(Animated):
    def __init__(self, position, fileName="", offset=None, maxSpeed=500, row = 0, nFrames = 1):
        super().__init__(position, fileName, offset, row, nFrames)
        self.velocity = vec(0,0)
        self.maxSpeed = maxSpeed
    
    def update(self, seconds):
        super().update(seconds)
        if magnitude(self.velocity) > self.maxSpeed:
            self.velocity = scale(self.velocity, self.maxSpeed)

        self.position += self.velocity * seconds
