from pygame.locals import Rect
from ..entity_baseclass.animated import Animated

# exist in the world
# can be drawn
# can be picked up

class Item(Animated):
    def __init__(self, position, fileName="", offset=(0,0), row = 0, nFrames = 1):
        super().__init__(position, fileName, offset, row, nFrames)

        self.canPickUp = False
        self.isEquipped = False
        self.collisionRect = Rect(0,0, self.getWidth(), self.getHeight())
        self.animate = False

        self.owner = None
        self.direction = None

    def setPickup(self, entity):
        self.owner = entity
        self.isEquipped = False

    def setDrop(self, position):
        self.owner = None
        self.setPosition(position)

    def update(self):
        pass