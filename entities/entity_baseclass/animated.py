import pygame
from os.path import join
from .drawable import Drawable
from utils.spriteManager import *
from utils.vector import *

class Animated(Drawable):
    def __init__(self, position=vec(0,0), fileName="", offset=None, row = 0, nFrames = 1):
        super().__init__(position, fileName, offset)

        self.fileName = fileName
        self.animationTimer = 0
        self.frame = 0
        self.animate = None
        self.base_fps = 8
        self.framePerSecond = self.base_fps

        self.row = row
        self.nFrames = nFrames # change depending on the animation sheet being used
        self.FSManimated = None

    def getFPS(self):
        return self.framePerSecond
    
    def setFPS(self, fps):
        self.framePerSecond = fps

    def resetFPS(self):
        self.framePerSecond = self.base_fps

    def getAnimationTimer(self):
        return self.animationTimer

    def update(self, seconds):
        if self.FSManimated:
            self.FSManimated.enter()

        # if self.animate:
        if not self.animate:
            return
        
        self.animationTimer += seconds

        if self.animationTimer >= 1 / self.framePerSecond:
            self.frame += 1
            self.frame %= self.nFrames
            self.animationTimer -= 1 / self.framePerSecond
            self.image = SpriteManager.getInstance().getSprite(self.fileName, (self.row, self.frame))