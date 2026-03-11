from pygame.locals import *
from utils.vector import vec, magnitude
from .entity_baseclass import Entity
import random

class Robot_Head(Entity):
    def __init__(self, body, fileName="robot_head.png", offset=(0, 0), maxSpeed=500, row=0, nFrames=1):
        super().__init__(body.getPosition(), fileName, offset, maxSpeed, row, nFrames)
        self.fileName = "robot_head.png"

        self.collisionRect = None

        self.body = body
        self.head_offset = vec(0, 0)  # base offset from body
        self.hitbox = Rect(7,0,int(self.getWidth() - 14),int(self.getHeight()))

        self.deathVelocity = vec(0, 0)
        self.deathTarget = None
  
        self.blinkCounter = 5
        self.twitchCounter = 10
        self.lowHealthCounter = 2

        self.bobPattern = [0, 1, 2, 1]
        self.bobIndex = 0
        self.bobTimer = 0
        self.bobSpeed = 0.1  # seconds per step

        self.maxLagDistance = 500
        self.speed = 100

        self.actionState = "isIdle"
        self.animateState = "isIdle"

        self.animations = {
            "isIdle": {
                "nFrames": 1,
                "FPS": 8,
                "rows": {
                    "LR_moving": 3,
                    "LR_idle": 0,
                    "DOWN": 7,
                    "UP": 6
                }
            },
            "isBlinking": {
                "nFrames": 2,
                "FPS": 8,
                "rows": {
                    "LR_moving": 3,
                    "LR_idle": 0,
                    "DOWN": 7,
                    "UP": 6
                }
            },
            "isTwitching": {
                "nFrames": 4,
                "FPS" : 8,
                "rows": {
                    "LR_moving": 5,
                    "LR_idle": 1,
                    "DOWN": 8,
                    "UP": 6
                }
            },
            "isFlashingEyes": {
                "nFrames": 4,
                "FPS": 8,
                "rows": {
                    "LR_moving": 4,
                    "LR_idle": 2,
                    "DOWN": 9,
                    "UP": 6
                }
            },
            "isAttacking": {
                "nFrames": 8,
                "FPS": 12,
                "rows": {
                    "LR_moving": 13,
                    "LR_idle": 13,
                    "DOWN": 15,
                    "UP": 14
                }
            }
        }

    def setIdle(self):
        self.frame = 0
        self.nFrames = 1
        self.setFPS(8)
        self.animateState = "isIdle"

        if self.body.direction == "LR" and self.body.moving:
            self.flipped = self.body.flipped
            self.row = 3
            self.head_offset = vec(0, -14) 
            if self.flipped[0]:
                self.head_offset[0] = -self.head_offset[0]
        elif self.body.direction == "LR":
            self.flipped = self.body.flipped
            self.row = 0
            self.head_offset = vec(0, -15) 
        elif self.body.direction == "DOWN":
            self.row = 7
            self.head_offset = vec(0, -14)
        else:
            self.row = 6
            self.head_offset = vec(0, -13) 
    
    def setAttacking(self):
        if self.animateState != "isAttacking":
            self.frame = 0
            self.nFrames = 8
            self.animateState = "isAttacking"
            self.setFPS(12)

        if self.body.direction == "LR":
            self.flipped = self.body.flipped
            self.row = 13
            self.head_offset = vec(0, -15)
        elif self.body.direction == "DOWN":
            self.row = 15
            self.head_offset = vec(0, -14)
        else:
            self.row = 14
            self.head_offset = vec(0, -15)

    def setHeadAnimation(self, name):
        anim = self.animations[name]

        if self.animateState != name:
            self.frame = 0
            self.nFrames = anim["nFrames"]
            self.animateState = name
            self.setFPS(anim["FPS"])

        rows = anim["rows"]

        if self.body.direction == "LR" and self.body.moving:
            self.flipped = self.body.flipped
            self.row = rows["LR_moving"]
            self.head_offset = vec(0, -14)
            if self.flipped[0]:
                self.head_offset[0] = -self.head_offset[0]
        elif self.body.direction == "LR":
            self.flipped = self.body.flipped
            self.row = rows["LR_idle"]
            self.head_offset = vec(0, -15)
        elif self.body.direction == "DOWN":
            self.row = rows["DOWN"]
            self.head_offset = vec(0, -14)
        else:
            self.row = rows["UP"]
            self.head_offset = vec(0, -13)

    def chooseAnimation(self, seconds):
        # highest priority
        if not self.body.isAlive:
            self.animateState = "isDying"
            return
        
        if self.body.actionState == "isAttacking":
            self.setAttacking()
            return

        # if currently playing a temporary animation, let it finish
        if self.animateState in ["isBlinking", "isTwitching", "isFlashingEyes"]:
            anim = self.animations[self.animateState]
            if self.frame >= anim["nFrames"] - 1:
                self.setIdle()
            return

        # --- only reach here if effectively idle ---

        self.blinkCounter -= seconds
        if self.blinkCounter <= 0 and self.body.health > (self.body.maxHealth * .25):
            self.setHeadAnimation("isBlinking")
            self.blinkCounter = 6 # adjust for blinks/seconds
            return

        self.twitchCounter -= seconds
        if self.twitchCounter <= 0 and self.body.health > (self.body.maxHealth * .25):
            self.setHeadAnimation("isTwitching")
            self.twitchCounter = random.randint(3, 15) # adjust for twitch animation chance
            return
        
        self.lowHealthCounter -= seconds
        if self.body.health <= (self.body.maxHealth * .25):
            if self.lowHealthCounter <= 0:
                self.setHeadAnimation("isFlashingEyes")
                self.lowHealthCounter = 2 # adjust for flashes/seconds
                return

        # Default state
        self.animateState = "isIdle"

    def applyAnimation(self, seconds):
        if self.animateState == "isIdle":
            self.setIdle()

        elif self.animateState == "isBlinking":
            self.setHeadAnimation("isBlinking")

        elif self.animateState == "isTwitching":
            self.setHeadAnimation("isTwitching")

        elif self.animateState == "isFlashingEyes":
            self.setHeadAnimation("isFlashingEyes")

        elif self.animateState == "isAttacking":
            self.setAttacking()

        elif self.animateState == "isDying":
            self.setDying(seconds)

    def setDying(self, seconds):
        if not self.isAlive:
            self.setDead(seconds)
            return
    
        if self.actionState != "isDying":
            self.frame = 0
            self.nFrames = 10
            self.setFPS(8)
            self.actionState = "isDying"
            self.animateState = "isDying"
            self.head_offset = vec(0, -14)

            direction = vec(round(random.uniform(-1.2, 1.2), 2), round(random.uniform(.6, 1.5), 2))
            self.deathVelocity = direction * 200
            self.deathTarget = self.getPosition() + direction * 40
        self.row = 11

        self.position += self.deathVelocity * seconds
        self.deathVelocity *= 0.9

        # bounce when reaching target distance
        if magnitude(self.position - self.deathTarget) < 5:
            self.deathVelocity *= 0.5
            self.deathTarget = self.position  # only bounce once

        # stop tiny motion
        if magnitude(self.deathVelocity) < 10:
            self.deathVelocity = vec(0,0)

        if self.frame >= self.nFrames - 1:
            self.setDead(seconds)
            self.isAlive = False
            return
    
    def setDead(self, seconds):
        if self.actionState != "isDead":
            self.frame = 0
            self.nFrames = 2
            self.setFPS(8)
            self.actionState = "isDead"
            self.animateState = "isDead"
            self.head_offset = vec(0, -14)
        self.row = 12

    def update(self, seconds, tmx_map):
        super().update(seconds, tmx_map)

        if self.body.health <= 0:
            self.setDying(seconds)
            return
        
        self.chooseAnimation(seconds)
        self.applyAnimation(seconds)

        # head bobbing animation
        if self.body.moving and self.body.actionState != "isAttacking":
            self.bobTimer += seconds
            if self.bobTimer >= self.bobSpeed:
                self.bobTimer = 0
                self.bobIndex = (self.bobIndex + 1) % len(self.bobPattern)

            self.bobAmount = self.bobPattern[self.body.frame % 4]
        else:
            self.bobIndex = 0
            self.bobTimer = 0
            self.bobAmount = 0

        # where head will be if not lagging
        targetPos = (
            self.body.getPosition()[0] + self.head_offset[0],
            self.body.getPosition()[1] + self.head_offset[1] + self.bobAmount
        )

        # # lagging code
        # currentPos = self.getPosition()
        # dx = targetPos[0] - currentPos[0]
        # dy = targetPos[1] - currentPos[1]
        # distance = magnitude(vec(dx, dy))
        # deadzone = 5   # pixels

        # # clamp max lag distance
        # if distance > self.maxLagDistance:
        #     dx = dx / distance * self.maxLagDistance
        #     dy = dy / distance * self.maxLagDistance
        #     newX = targetPos[0] - dx
        #     newY = targetPos[1] - dy
        # else:
        #     newX = currentPos[0] + dx * self.speed * seconds
        #     newY = currentPos[1] + dy * self.speed * seconds

        # if abs(dx) < deadzone:
        #     newX = targetPos[0]
        # if abs(dy) < deadzone:
        #     newY = targetPos[1]

        self.setPosition(vec(targetPos[0], targetPos[1]))

        self.isHurt = self.body.isHurt
        self.direction = self.body.direction