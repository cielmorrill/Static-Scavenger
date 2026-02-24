import pygame
from entities.entity_baseclass import Drawable
from os.path import join
from utils.gamescreen import GameScreen
from utils.vector import vec, pyVec
from pytmx import load_pygame

class TmxMap(object):
    _TMX_FOLDER = "tmx"

    def __init__(self, fileName="", position=vec(0,0), offset=None):
        self.position = position
        self.fileName = fileName
        self.offset = offset

        self.tmx_map = load_pygame(join(self._TMX_FOLDER, self.fileName)) 
        self.map_width = self.tmx_map.width * self.tmx_map.tilewidth
        self.map_height = self.tmx_map.height * self.tmx_map.tileheight
        self.map_surface = pygame.Surface((self.map_width, self.map_height), pygame.SRCALPHA)

        for layer in self.tmx_map.visible_layers:
            if hasattr(layer, "tiles"):
                for x, y, tile in layer.tiles():
                    self.map_surface.blit(
                        tile,
                        (x * self.tmx_map.tilewidth,
                        y * self.tmx_map.tileheight)
                    )
        
        GameScreen.WORLD_SIZE = vec(self.map_width, self.map_height)
    
    def draw(self, drawSurface):        
        drawSurface.blit(self.map_surface, pyVec(self.position - Drawable.CAMERA_OFFSET))
   
    def getWidth(self):
        return self.map_width
    
    def getHeight(self):
        return self.map_height

    def getPosition(self):
        return vec(*self.position)
    
    def setPosition(self, newPosition):
        self.position = vec(*newPosition)
    
    def handleEvent(self, event):
        pass
    
    def update(self, seconds):
        pass
      