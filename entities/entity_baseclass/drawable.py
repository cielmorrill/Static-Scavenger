import pygame
from pygame import image, Surface, SRCALPHA
from os.path import join
from utils.spriteManager import SpriteManager
from utils.vector import rectAdd, vec, pyVec

class Drawable(object):

    CAMERA_OFFSET = vec(0,0)

    # full screen for game display based on monitor
    # display_info = pygame.display.Info()
    # SCREEN_WIDTH = display_info.current_w
    # SCREEN_HEIGHT = display_info.current_h
    

    def __init__(self, position=vec(0,0), fileName="", offset=None):
        self.fileName = fileName
        if fileName != "":
            sm = SpriteManager.getInstance()
            self.image = sm.getSprite(fileName, offset)
        
        self.position=vec(*position)
        self.flipped = [False, False]
        self.isHurt = False

        # self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.FULLSCREEN)
    
    def draw(self, drawSurface):
        # scaled_surface = pygame.transform.scale(
        #     drawSurface,
        #     self.screen.get_size()
        # )

        # could make more efficient in the future
        flippedImage = pygame.transform.flip(self.image, *self.flipped)
        if self.isHurt:
            hurt_image = flippedImage.copy()
            hurt_image.fill((255,0,0), special_flags=pygame.BLEND_RGBA_MULT)
            flippedImage = hurt_image
        drawSurface.blit(flippedImage, pyVec(self.position - Drawable.CAMERA_OFFSET))
         
    def getSize(self):
        return vec(*self.image.get_size())    
   
    def getWidth(self):
        return self.getSize()[0]
    
    def getHeight(self):
        return self.getSize()[1]

    def getPosition(self):
        return vec(*self.position)
    
    def setPosition(self, newPosition):
        self.position = vec(*newPosition)
    
    def handleEvent(self, event):
        pass
    
    def update(self, seconds):
        pass
      
    def getCollisionRect(self):
        return rectAdd(self.getPosition(), self.image.get_rect())
    
    def setCollisionRect(self, newRect):
        self.image = Surface((newRect.width, newRect.height), SRCALPHA)