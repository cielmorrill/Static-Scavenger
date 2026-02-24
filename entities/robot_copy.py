from pygame.locals import *
from utils.gamescreen import GameScreen
from utils.vector import vec, magnitude, scale
from .entity_baseclass import Entity
from .robot_head import Robot_Head

class Robot_JOINED(Entity):
    def __init__(self, position, fileName="robot_spritesheet.png", offset=(0,0), maxSpeed=500, row = 0, nFrames = 1):
        super().__init__(position, fileName, offset, maxSpeed, row, nFrames)

        self.fileName = "robot_spritesheet.png"
        
        self.direction = "DOWN"
        self.animateState = "isIdle"
        self.actionState = "isIdle"
        self.animate = True
        self.moving = False

        # stats
        self.maxHealth = 100.0
        self.health = self.maxHealth
        self.attackPower = 20.0

        self.isHurt = False
        self.hurtTimerBase = .5
        self.hurtTimer = .5
        self.healthRegen = 5      # per second
        self.healthCooldown = 5      # seconds
        self.healthCooldownTimer = 0

        # movement attributes
        self.base_speed = 100
        self.speed = self.base_speed
        self.sprintMultiplier = 1.5
        self.acceleration = 1000

        # stamina system
        self.maxStamina = 100
        self.stamina = self.maxStamina
        self.staminaRegen = 25      # per second
        self.staminaCooldown = 3      # seconds
        self.staminaCooldownTimer = 0
        self.sprintStaminaCost = 50 # per second

        self.keyMap = {
            K_UP    : False,
            K_DOWN  : False,
            K_RIGHT : False,
            K_LEFT  : False,
            K_LSHIFT: False,
            K_RSHIFT: False
        }

    
    # handle idle image based on direction
    def setIdle(self):
        if self.actionState != "isIdle":
            self.frame = 0
            self.nFrames = 1
            self.setFPS(4)
            self.actionState = "isIdle"

        if self.direction == "LR":
            self.row = 0
        elif self.direction == "DOWN":
            self.row = 2
        else:
            self.row = 1

    # handle setting walking animation based on direction
    def setWalking(self):
        if self.actionState != "isWalking":
            self.frame = 0
            self.nFrames = 8
            self.setFPS(8)
            self.actionState = "isWalking"
            self.animateState = "isWalking"
        if self.direction == "LR":
            self.row = 5
        elif self.direction == "DOWN":
            self.row = 4
        else:
            self.row = 3
            
    def isSprinting(self):
        return self.keyMap[K_LSHIFT] or self.keyMap[K_RSHIFT]
    
    def updateSprinting(self, seconds, moving):
        # handle stamina and sprinting
        self.speed = self.base_speed
        if self.isSprinting() and self.stamina > 0 and moving:
            self.setFPS(12)
            self.speed *= self.sprintMultiplier
            self.stamina -= self.sprintStaminaCost * seconds
            self.staminaCooldownTimer = 0
        else:
            if self.stamina < self.maxStamina:
                if self.staminaCooldownTimer < self.staminaCooldown:
                    self.staminaCooldownTimer += seconds
                else:
                    self.stamina += self.staminaRegen * seconds
        self.stamina = max(0, min(self.stamina, self.maxStamina))

    def handleEvent(self, event):
        if event.type in (KEYDOWN, KEYUP) and event.key in self.keyMap.keys():
            self.keyMap[event.key] = event.type == KEYDOWN

    def update(self, seconds):
        # handle movement input
        if self.keyMap[K_LEFT] or self.keyMap[K_RIGHT]:
            if self.keyMap[K_LEFT]:
                self.velocity[0] = -self.speed
                self.flipped[0] = True
                self.direction = "LR"
                self.moving = True
            else:
                self.velocity[0] = self.speed
                self.flipped[0] = False
                self.direction = "LR"
                self.moving = True
        else:
            self.velocity[0] = 0
        if self.keyMap[K_UP] or self.keyMap[K_DOWN]:
            if self.keyMap[K_UP]:
                self.velocity[1] = -self.speed
                self.direction = "UP"
                self.moving = True
            else:
                self.velocity[1] = self.speed
                self.direction = "DOWN"
                self.moving = True
        else:
            self.velocity[1] = 0

        if self.velocity[0] == 0 and self.velocity[1] == 0:
            self.moving = False
        
        # handle diagonal speed normalization
        if magnitude(self.velocity) > self.speed:
            self.velocity = scale(self.velocity, self.speed)

        # handle movement animations
        if self.moving:
            self.setWalking()
        else:
            self.setIdle()

        self.updateSprinting(seconds, self.moving)

        super().update(seconds)