from pygame.locals import *
from utils.vector import vec, magnitude
from .entity_baseclass import Entity
import random

class Robot_Arms(Entity):
    def __init__(self, body, fileName="robot_arms.png", offset=(0, 0), maxSpeed=500, row=0, nFrames=1):
        super().__init__(body.getPosition(), fileName, offset, maxSpeed, row, nFrames)
        self.fileName = "robot_arms.png"

        self.body = body
        self.animate = True

        self.attackRect = Rect(0,0,int(self.getWidth() - 10),int(self.getHeight() + 10))
        self.collisionRect = Rect(0,0,int(self.getWidth() - 16),int(self.getHeight()))

        self.weaponDrawn = False
        self.sheatheCooldown = 10
        self.sheatheCounter = 10

        self.actionState = "isIdle"
        self.animateState = "isIdle"

    def getAttackRect(self):
        rect = self.attackRect.copy()
        rect.center = self.getCollisionRect().center
        return rect

    def setIdle(self):
        self.frame = 0
        self.nFrames = 1
        self.setFPS(8)
        self.animateState = "isIdle"
        self.actionState = "isIdle"

        if self.body.direction == "LR":
            self.flipped[0] = self.body.flipped[0]
            self.row = 1
        else:
            self.row = 0

    def setIdleWeaponDrawn(self):
        self.frame = 0
        self.nFrames = 1
        self.setFPS(8)
        self.animateState = "isIdleWeapon"
        self.actionState = "isIdleWeapon"

        if self.body.direction == "LR":
            self.flipped[0] = False
            self.row = 18
        elif self.body.direction == "UP":
            self.flipped[0] = False
            self.row = 17
        else:
            self.flipped[0] = False
            self.row = 16

    def setWalking(self):
        if self.animateState != "isWalking":
            self.frame = 0
            self.nFrames = 8
            self.setFPS(8)
            self.animateState = "isWalking"
            self.actionState = "isWalking"

        if self.body.direction == "LR":
            self.flipped[0] = self.body.flipped[0]
            self.row = 1
        else:
            self.row = 0

    def setWalkingWeapon(self):
        if self.animateState != "isWalkingWeapon":
            self.frame = 0
            self.nFrames = 8
            self.animateState = "isWalkingWeapon"
            self.actionState = "isWalkingWeapon"
            self.setFPS(8)

        if self.body.direction == "LR":
            self.flipped[0] = False
            self.row = 18
        elif self.body.direction == "UP":
            self.flipped[0] = False
            self.row = 17
        else:
            self.flipped[0] = False
            self.row = 16

    def setUnsheatheSword(self):
        if self.animateState != "isUnsheathingSword":
            self.frame = 0
            self.nFrames = 5
            self.setFPS(12)
            self.animateState = "isUnsheathingSword"
            self.actionState = "isUnsheathingSword"

        if self.frame >= self.nFrames - 1:
            self.weaponDrawn = True
            self.setIdleWeaponDrawn()

        self.sheatheCounter = self.sheatheCooldown

        if self.body.direction == "LR":
            if self.body.flipped[0]:
                self.flipped[0] = False
                self.row = 7
            else:
                self.flipped[0] = False
                self.row = 4
        elif self.body.direction == "UP":
            self.flipped[0] = False
            self.row = 10
        else:
            self.flipped[0] = False
            self.row = 13

    def setSheatheSword(self):
        if self.animateState != "isSheathingSword":
            self.frame = 0
            self.nFrames = 6
            self.setFPS(12)
            self.animateState = "isSheathingSword"
            self.actionState = "isSheathingSword"
        if self.frame >= self.nFrames - 1:
            self.weaponDrawn = False
            self.setIdle()
            return

        if self.body.direction == "LR":
            if self.body.flipped[0]:
                self.flipped[0] = False
                self.row = 9
            else:
                self.flipped[0] = False
                self.row = 6
        elif self.body.direction == "UP":
            self.flipped[0] = False
            self.row = 11
        else:
            self.flipped[0] = False
            self.row = 14

    def setAttacking(self):
        if not self.weaponDrawn:
            self.setUnsheatheSword()
            return
        if self.animateState != "isAttacking":
            self.frame = 0
            self.nFrames = 8
            self.animateState = "isAttacking"
            self.actionState = "isAttacking"
            self.setFPS(12)
        
        self.sheatheCounter = self.sheatheCooldown

        if self.frame >= self.nFrames - 1:
            self.setIdleWeaponDrawn()
            return

        if self.body.direction == "LR":
            if self.body.flipped[0]:
                self.flipped[0] = False
                self.row = 8
            else:
                self.flipped[0] = False
                self.row = 5
        elif self.body.direction == "UP":
            self.flipped[0] = False
            self.row = 12
        else:
            self.flipped[0] = False
            self.row = 15

    def setDying(self, seconds):
        if not self.isAlive:
            self.setDead(seconds)
            return
        
        if self.animateState != "isDying":
            self.frame = 0
            self.nFrames = 8
            self.animateState = "isDying"
            self.setFPS(8)

        self.row = 2

        if self.frame >= self.nFrames - 1:
            self.setDead(seconds)
            self.isAlive = False
            return
    
    def setDead(self, seconds):
        self.frame = 0
        self.row = 3
        self.nFrames = 1

    def update(self, seconds, tmx_map):
        super().update(seconds, tmx_map)

        if not self.body.isAlive or self.body.health <= 0:
            self.setDying(seconds)
            return

        if self.body.animateState == "isAttacking":
            self.setAttacking()
            return

        if self.body.moving and self.actionState not in ["isUnsheathingSword", "isSheathingSword", "isAttacking"]:
            if self.weaponDrawn:
                self.setWalkingWeapon()
            else:
                self.setWalking()
        elif self.actionState not in ["isUnsheathingSword", "isSheathingSword", "isAttacking"]:
            if self.weaponDrawn:
                self.setIdleWeaponDrawn()
            else:
                self.setIdle()

        if self.actionState == "isUnsheathingSword":
            self.setUnsheatheSword()
        if self.actionState == "isSheathingSword":
            self.setSheatheSword()

        if self.weaponDrawn:
            self.sheatheCounter -= 1 * seconds

        if self.sheatheCounter <= 0 and self.weaponDrawn and self.actionState not in ["isUnsheathingSword", "isAttacking"]:
            self.setSheatheSword()
            self.sheatheCounter = self.sheatheCooldown

        self.isHurt = self.body.isHurt

        bodyPos = self.body.getPosition()
        self.setPosition(vec(bodyPos[0] - 16, bodyPos[1] - 16))
        # hands sometimes get out of alignment when walking up/down. why?