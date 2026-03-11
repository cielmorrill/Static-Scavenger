from .equippable import Equippable
from utils.spriteManager import SpriteManager

class Cowboy_Hat(Equippable):
    def __init__(self, position, fileName="cowboy_hat.png", offset=(0,0), row = 0, nFrames = 1):
        super().__init__(position, fileName, offset, row, nFrames)

        self.equipSlot = "head" # or whatever

    def update(self):
        super().update()
        self.position[1] -= 7
        if self.isEquipped:
            if self.direction == "LR":
                self.row = 1
                self.image = SpriteManager.getInstance().getSprite(self.fileName, (self.row, self.frame))
            elif self.direction == "UP":
                self.row = 2
                self.image = SpriteManager.getInstance().getSprite(self.fileName, (self.row, self.frame))
            else:
                self.row = 3
                self.image = SpriteManager.getInstance().getSprite(self.fileName, (self.row, self.frame))