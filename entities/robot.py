from pygame.locals import *
from utils.gamescreen import GameScreen
from utils.vector import vec, magnitude, scale, rectAdd
from .entity_baseclass import Entity
from .robot_head import Robot_Head
from .robot_arms import Robot_Arms

class Robot(Entity):
    def __init__(self, position, fileName="robot_body.png", offset=(0,0), maxSpeed=500, row = 0, nFrames = 1):
        super().__init__(position, fileName, offset, maxSpeed, row, nFrames)

        self.fileName = "robot_body.png"
        self.head = Robot_Head(self)
        self.arms = Robot_Arms(self)
        self.collisionRect = Rect(7,1,int(self.getWidth() - 6),int(self.getHeight() - 2))
        self.attackRect = self.arms.attackRect
        
        self.direction = "DOWN"
        self.animateState = "isIdle"
        self.actionState = "isIdle"
        self.animate = True
        self.moving = False
        self.weaponDrawn = False

        # stats
        self.maxHealth = 100.0
        self.health = self.maxHealth
        self.attackPower = 20.0
        self.attackCooldown = .5
        self.attackCooldownTimer = 0
        self.canAttack = True

        self.isHurt = False
        self.hurtTimerBase = .5
        self.hurtTimer = .5
        self.healthRegen = 5      # per second
        self.healthCooldown = 10      # seconds
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
            K_RSHIFT: False,
            K_SPACE : False
        }

    def getCollisionRect(self):
        body_rect = rectAdd(self.getPosition(), self.collisionRect)
        head_rect = rectAdd(self.head.getPosition(), self.head.collisionRect)
        return [body_rect, head_rect]
    
    # handle idle image based on direction
    def setIdle(self):
        if self.actionState != "isIdle":
            self.frame = 0
            self.nFrames = 1
            self.setFPS(8)
            self.actionState = "isIdle"
            self.animateState = "isIdle"

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

    def setAttacking(self):
        if self.attackCooldownTimer > 0:
            return
        if self.arms.weaponDrawn == False:
            self.arms.setUnsheatheSword() # this will need to be drawWeapon() with weapon checks later
            return
        if self.animateState != "isAttacking":
            self.frame = 0
            self.nFrames = 8
            self.setFPS(12)
            self.actionState = "isAttacking"
            self.animateState = "isAttacking"

        if self.frame >= self.nFrames - 1:
            self.setIdle()
            self.arms.setIdleWeaponDrawn()
            self.attackCooldownTimer = self.attackCooldown
            return
        
        self.moving = False
        if self.direction == "LR":
            if self.flipped:
                self.row = 8
            else:
                self.row = 9
        elif self.direction == "UP":
            self.row = 10
        else:
            self.row = 11

    def setDying(self, seconds):
        if self.actionState == "isDead":
            self.setDead(seconds)
            return
        if self.actionState != "isDying":
            self.frame = 0
            self.nFrames = 8
            self.setFPS(8)
            self.actionState = "isDying"
            self.animateState = "isDying"
            self.isAlive = False
        self.row = 6

        if self.frame >= self.nFrames - 1:
            self.setDead(seconds)
            self.isAlive = False
            return
    
    def setDead(self, seconds):
        if self.actionState != "isDead":
            self.frame = 0
            self.nFrames = 8
            self.setFPS(8)
            self.actionState = "isDead"
            self.animateState = "isDead"
        self.row = 7

        if self.frame >= self.nFrames - 1:
            pass

    def clampWorldBoundary(self):
        x, y = self.getPosition()
        width = self.getWidth()
        height = self.getHeight()

        # LEFT
        if x <= 0:
            x = 0
            self.velocity[0] = 0

        # RIGHT
        if x + width >= GameScreen.WORLD_SIZE[0]:
            x = GameScreen.WORLD_SIZE[0] - width
            self.velocity[0] = 0

        # TOP (account for head sitting above body)
        head_top = y - self.head.getHeight() / 2
        if head_top <= GameScreen.MENU_BARRIER:
            y = GameScreen.MENU_BARRIER + self.head.getHeight() / 2
            self.velocity[1] = 0

        # BOTTOM
        if y + height >= GameScreen.WORLD_SIZE[1]:
            y = GameScreen.WORLD_SIZE[1] - height
            self.velocity[1] = 0

        self.setPosition((x, y))

        # if self.getPosition()[0] - self.getWidth() <= 0:
        #     self.velocity[0] = 0
        #     self.setPosition((0, self.getPosition()[1] + self.getWidth()))

        # if self.getPosition()[1] - self.head.getHeight() <= GameScreen.MENU_BARRIER:
        #     self.velocity[1] = 0
        #     self.setPosition((self.getPosition()[0] + self.head.getHeight(), GameScreen.MENU_BARRIER))

        # if self.getPosition()[0] + self.getWidth() + 15 >= GameScreen.WORLD_SIZE[0]:
        #     self.velocity[0] = 0
        #     self.setPosition((GameScreen.WORLD_SIZE[0] - self.getWidth(), self.getPosition()[1]))
            
        # if self.getPosition()[1] + self.getHeight() >= GameScreen.WORLD_SIZE[1]:
        #     self.velocity[1] = 0
        #     self.setPosition((self.getPosition()[0], GameScreen.WORLD_SIZE[1] - self.getHeight()))

    def draw(self, drawSurface):
        if self.direction == "UP":
            super().draw(drawSurface)
            self.arms.draw(drawSurface)
            self.head.draw(drawSurface)
        else:
            super().draw(drawSurface)
            self.head.draw(drawSurface)
            self.arms.draw(drawSurface)


    def handleEvent(self, event):
        if not self.isAlive:
            return
        
        if event.type in (KEYDOWN, KEYUP) and event.key in self.keyMap.keys():
            self.keyMap[event.key] = event.type == KEYDOWN

        self.head.handleEvent(event)
        self.arms.handleEvent(event)

    def update(self, seconds):
        self.velocity = vec(0,0)
        self.moving = False

        if self.health <= 0 or not self.isAlive:
            self.velocity = vec(0,0)
            self.isHurt = False
            super().update(seconds)
            self.head.update(seconds)
            self.arms.update(seconds)
            self.setDying(seconds)
            return
                
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

        if self.actionState == "isAttacking":
            self.setAttacking()
            if not self.isHurt:
                self.velocity = vec(0,0)
                self.moving = False
        elif self.keyMap[K_SPACE] and self.attackCooldownTimer <= 0:
            self.setAttacking()
        else:
            if self.moving:
                self.setWalking()
            else:
                self.setIdle()

        self.updateSprinting(seconds, self.moving)

        if self.attackCooldownTimer > 0:
            self.attackCooldownTimer -= seconds

        super().update(seconds)

        self.head.update(seconds)
        self.arms.update(seconds)
