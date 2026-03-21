"""
A Singleton Sprite Manager class
Author: Liz Matthews, 7/21/2023

Provides on-demand loading of images for a pygame program.
Will load entire sprite sheets if given an offset.

"""

from pygame import image, Surface, Rect, SRCALPHA
from pygame.transform import scale_by
from os.path import join
from .vector import vec, pyVec

class SpriteManager(object):
    """A singleton factory class to create and store sprites on demand.
    Do not directly instantiate this class! Use SpriteManager.getInstance()."""
    
    # The singleton instance variable
    _INSTANCE = None
    
    @classmethod
    def getInstance(cls):
        """Used to obtain the singleton instance"""
        if cls._INSTANCE == None:
            cls._INSTANCE = cls()
        
        return cls._INSTANCE
    






    # Folder in which images are stored
    _IMAGE_FOLDER = "sprites"
    
    ### PROPERTIES TO CHANGE TO ADD NEW IMAGES ###
    
    # Static information about the sprite sizes of particular image sheets.
    _SPRITE_SIZES = {
        "robot_body.png": vec(32, 16),
        "robot_arms.png": vec(64, 32),
        "ore.png"       : vec(16,16),
        "big_brown_rock.png": vec(48, 48),
        "explosion.png": vec(64, 64)
    }
    
    # A default sprite size
    _DEFAULT_SPRITE = vec(32, 32)
    
    # If images need to be rescaled
    _SCALES = {
        # Can also be two dimensional, ex: vec(2, 3)
    }
    
    # A list of images that require to be loaded with transparency
    _TRANSPARENCY = ["robot_body.png",
                     "robot_head.png",
                     "robot_arms.png",
                     "slime_sprite.png",
                     "brown_rock.png",
                     "grey_rock.png",
                     "ore.png",
                     "cowboy_hat.png",
                     "big_brown_rock.png",
                     "bomb_rock.png",
                     "explosion.png",
                     "treasure_chest_bottom.png",
                     "treasure_chest_lid.png"]
    
    # A list of images that require to be loaded with a color key
    _COLOR_KEY = [""] # ex "kirby.png"
    




    def __init__(self):
        """Creation of the SpriteManager, sets up storage for surface.
        Can only be called once."""
        if self._INSTANCE != None:
            raise RuntimeError("Cannot create more than one instance of the SpriteManager.")
        
        # Stores the surfaces indexed based on file name
        self._surfaces = {}

        self._fullSurfaces = {}
    
    def __getitem__(self, key):
        return self.getSprite(key)
    
    def getSize(self, fileName):
        spriteSize = self._SPRITE_SIZES.get(fileName,
                                            self._DEFAULT_SPRITE)

        scale = self._SCALES.get(fileName, 
                                 1)
        return pyVec(spriteSize * scale)
    
    def getSprite(self, fileName, offset=None):
        # If this sprite has not already been loaded, load the image from memory
        if fileName not in self._surfaces.keys():
            self._loadImage(fileName, offset)
          
        
        # If the offset is arbitrary, flyweight load the rect offset
        if type(offset) == Rect or (type(offset) in [list, tuple] \
                                    and len(offset) == 4):
            if type(offset) != Rect:
                offset = Rect(offset)
                
            if tuple(offset) not in self._surfaces[fileName]:
                self._surfaces[fileName][tuple(offset)] = self._loadRect(fileName,
                                                               self._surfaces[fileName]["full"],
                                                               offset)
            return self._surfaces[fileName][tuple(offset)]
        
        # If this is an image sheet, return the correctly offset sub surface
        elif type(offset) in [list, tuple] and len(offset) == 2:
            return self._surfaces[fileName][offset[0]][offset[1]] 
        
        # Otherwise, return the sheet created
        return self._surfaces[fileName]
 
    def _loadImage(self, fileName, offset=None):
        # Load the full image      
        fullImage = self._loadFull(fileName)
        
        fullImage = scale_by(fullImage,
                             self._SCALES.get(fileName,
                             1))
        
        
        # If the image to be loaded is an image sheet, split it up based on the sprite size
        if type(offset) in [list, tuple] and len(offset) == 2:
            self._loadSpriteSheet(fileName, fullImage)
        
        # If the image is an arbitrary offset set up a dictionary and store the full image
        elif type(offset) == Rect or (type(offset) in [list, tuple] \
                                      and len(offset) == 4):
            self._surfaces[fileName] = {}
            self._surfaces[fileName]["full"] = fullImage
           
        # If there is no offset store the entire image
        elif offset == None:
            self._surfaces[fileName] = fullImage
           
            # If we need to set the color key
            self._applyColorKey(fileName, fullImage)
        
        else:
            raise TypeError(f"Offset must be of type Rect, List, Tuple, or None. Length of List/Tuple must be 2 for spriteSheet offset or 4 for arbitrary rect.")
 
    def _loadFull(self, fileName):
        fullImage = image.load(join(self._IMAGE_FOLDER, fileName))
       
        # Detect if a transparency is needed
        fullImage = self._applyTransparency(fileName, fullImage)
        
        return fullImage
 
    def _loadRect(self, fileName, fullImage, rect):
        sprite = self._applyTransparency(fileName, rect=rect)
           
        sprite.blit(fullImage, (0,0), rect)
        
        self._applyColorKey(fileName, sprite)
        
        return sprite
    
    def _loadSpriteSheet(self, fileName, fullImage):
        self._surfaces[fileName] = []
        
        # Try to get the sprite size, use the default size if it is not stored
        spriteSize = self.getSize(fileName)
        
        # See how big the sprite sheet is
        sheetDimensions = fullImage.get_size()
        
        # Iterate over the entire sheet, increment by the sprite size
        for y in range(0, sheetDimensions[1], spriteSize[1]):
            self._surfaces[fileName].append([])
            for x in range(0, sheetDimensions[0], spriteSize[0]):
                # Add the sprite to the end of the current row
                self._surfaces[fileName][-1].append(self._loadRect(fileName,
                                                         fullImage,
                                                         Rect((x,y),
                                                               spriteSize)))
         
               
    def _applyColorKey(self, fileName, surface):
        if fileName in self._COLOR_KEY:
            surface.set_colorkey(surface.get_at((0,0)))

    def _applyTransparency(self, fileName, img=None, rect=None):
        if fileName in self._TRANSPARENCY:
            if img:
                returnImage = img.convert_alpha()
            else:
                returnImage = Surface(rect.size, SRCALPHA, 32)
        else:
            if img:
                returnImage = img.convert()
            else:
                returnImage = Surface(rect.size)
                
        return returnImage
