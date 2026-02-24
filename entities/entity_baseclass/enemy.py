from pygame.locals import *
from pygame import Rect
from utils.vector import vec, magnitude, scale, sign
from .entity import Entity

class Enemy(Entity):
    
    def __init__(self, position, fileName="", offset=..., maxSpeed=500, row=0, nFrames=1):
        super().__init__(position, fileName, offset, maxSpeed, row, nFrames)

        self.awarenessRect = Rect(0,0,int(self.getWidth()),int(self.getHeight()))
        self.attackRect = Rect(0,0,int(self.getWidth()),int(self.getHeight()))

        self.seesRobot = False

    def getAwarenessRect(self):
        rect = self.awarenessRect.copy()
        rect.center = self.getCollisionRect().center
        return rect

    def getAttackRect(self):
        rect = self.attackRect.copy()
        rect.center = self.getCollisionRect().center
        return rect

    def robotAwareness(self, bool):
        self.seesRobot = bool

    def attackCheck(self, bool):
        if self.animateState == "isAttacking":
            self.canAttack = True
        elif self.attackCooldown > 0:
            self.canAttack = False
        else:
            self.canAttack = bool

    def chase(self, obj):
        self.moving = True
        deadzone = 5   # pixels
        direction = obj.getPosition() - self.getPosition()
        distance = magnitude(direction)

        if distance == 0 or self.touchingEntity:
            self.velocity = vec(0, 0)
            return
        
        if abs(direction[0]) < deadzone:
            direction[0] = 0
        if abs(direction[1]) < deadzone:
            direction[1] = 0
        
        direction = sign(direction)
        self.velocity = direction * self.speed

        # handle diagonal speed normalization
        if magnitude(self.velocity) > self.speed:
            self.velocity = scale(self.velocity, self.speed)

    def player_killedBehavior(self, obj):
        if not obj.isAlive:
            self.moving = True
            direction = obj.getPosition() - self.getPosition()
            direction = sign(direction)
            self.velocity = -(direction) * self.speed

            # handle diagonal speed normalization
            if magnitude(self.velocity) > self.speed:
                self.velocity = scale(self.velocity, self.speed)

    def updateAI (self, seconds, target):
        pass

    def update(self, seconds):
        super().update(seconds)
        if self.isHurt:
            return
