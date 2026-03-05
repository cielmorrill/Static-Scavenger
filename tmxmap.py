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
        self.collision_layer = self.tmx_map.get_layer_by_name("Collision")

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

    def is_blocked(self, world_x, world_y):
        tile_x = int(world_x // self.tmx_map.tilewidth)
        tile_y = int(world_y // self.tmx_map.tileheight)

        if tile_x < 0 or tile_y < 0:
            return True
        if tile_x >= self.tmx_map.width or tile_y >= self.tmx_map.height:
            return True

        tile = self.collision_layer.data[tile_y][tile_x]

        return tile != 0

    def getBlockedTileRects(self, entity):
        """
        Returns pygame.Rects for blocked tiles overlapping the entity
        using position/width/height (same logic style as world boundaries).
        """

        tile_w = self.tmx_map.tilewidth
        tile_h = self.tmx_map.tileheight

        x, y = entity.getPosition()
        width = entity.getWidth()
        height = entity.getHeight()

        left_tile = int(x // tile_w)
        right_tile = int((x + width) // tile_w)
        top_tile = int(y // tile_h)
        bottom_tile = int((y + height) // tile_h)

        blocked_rects = []

        for ty in range(top_tile, bottom_tile + 1):
            for tx in range(left_tile, right_tile + 1):

                world_x = tx * tile_w
                world_y = ty * tile_h

                if self.is_blocked(world_x, world_y):
                    blocked_rects.append(
                        pygame.Rect(world_x, world_y, tile_w, tile_h)
                    )

        return blocked_rects
    
    # def spawn(self):
    #     x = random.randint(0, map_width)
    #     y = random.randint(0, map_height)

    #     if not game_map.is_blocked(x, y):
    #         break