from .item import Item
from utils.vector import vec 

class Equippable(Item):
    def __init__(self, position, fileName="", offset=(0,0), row = 0, nFrames = 1):
        super().__init__(position, fileName, offset, row, nFrames)

        self.equipSlot = None
        self.equippable_offset = vec(0,0)

    def setEquip(self, entity, equippable_offset = 0):
        self.equippable_offset += equippable_offset
        self.owner = entity
        self.isEquipped = True
        self.direction = self.owner.direction
        # no code with equipslot yet but could add code here to change player stats based on equip slot

    def setUnequip(self):
        self.isEquipped = False

    def update(self):
        if self.isEquipped:
            self.setPosition(self.owner.getPosition())
            self.direction = self.owner.direction
            self.flipped = self.owner.flipped