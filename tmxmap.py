import pygame
from entities.entity_baseclass import Drawable
from os.path import join
from entities.entity_baseclass.animated import Animated
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
                    if tile:
                        self.map_surface.blit(
                            tile,
                            (x * self.tmx_map.tilewidth,
                            y * self.tmx_map.tileheight)
                        )
        
        GameScreen.WORLD_SIZE = vec(self.map_width, self.map_height)

        self.transitions = []

        if "Transitions" in self.tmx_map.layernames:
            layer = self.tmx_map.get_layer_by_name("Transitions")

            for obj in layer:
                rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)

                self.transitions.append({
                    "rect": rect,
                    "target": getattr(obj, "target_map", None),
                    "spawn": (
                        getattr(obj, "spawn_x", 0),
                        getattr(obj, "spawn_y", 0)
                    )
                })

        self.spawns = []

        if "Spawns" in self.tmx_map.layernames:
            layer = self.tmx_map.get_layer_by_name("Spawns")

            for obj in layer:
                spawn_type = obj.type

                self.spawns.append({
                    "type": obj.properties.get("accepted_types", ""),  # string like "brown_rock grey_rock" or "slime"
                    "spawn_chance": float(obj.properties.get("spawn_chance", 1.0)),
                    "pos": (obj.x, obj.y),
                    "size": (obj.width, obj.height)
                })

                #  {'type': 'slime', 'pos': (400,600)},

        self.animated_tiles = []

        if "Animated" in self.tmx_map.layernames:
            layer = self.tmx_map.get_layer_by_name("Animated")

            for tile in layer:
                # anim = Animated(
                #     position=(tile.x, tile.y),
                #     fileName=getattr(tile, "fileName", None),
                #     row = getattr(tile, "row", 0),
                #     nFrames=getattr(tile, "nFrames", 1)
                # )
                # anim.setFPS(getattr(tile, "fps", 8))
                # anim.animate = True

                # self.animated_tiles.append(anim)

                tile_w = self.tmx_map.tilewidth
                tile_h = self.tmx_map.tileheight

                cols = int(tile.width // tile_w)
                rows = int(tile.height // tile_h)

                for row_i in range(rows):
                    for col_i in range(cols):
                        x = tile.x + col_i * tile_w
                        y = tile.y + row_i * tile_h

                        anim = Animated(
                            position=(x, y + 1),  # slight offset to prevent weird gaps between tiles
                            fileName=tile.properties.get("fileName"),
                            row=tile.properties.get("row", 0),
                            nFrames=tile.properties.get("nFrames", 1)
                        )

                        anim.setFPS(tile.properties.get("fps", 8))
                        anim.animate = True

                        self.animated_tiles.append(anim)

                # anim.frame = random.randint(0, anim.nFrames - 1)       this could be fun for certain tiles...
    
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
    
    def check_transition(self, entity):
        for t in self.transitions:
            if entity.getCollisionRect().colliderect(t["rect"]):
                return t
        return None