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
        self.collisionRect = Rect(0,0, self.getWidth(), self.getHeight())
        self.hitbox = Rect(7,1,int(self.getWidth() - 6),int(self.getHeight() - 4))
        self.attackRect = Rect(-5,-20,int(self.getWidth() + 10),int(self.getHeight() + 30))
        self.createShadow()
        
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
        self.attackCooldown = .2
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

        self.joyMap = {
            "UP": False,
            "DOWN": False,
            "LEFT": False,
            "RIGHT": False,
            "SPRINT": False,
            "ATTACK": False
        }

    def getCollisionRect(self):
        return rectAdd(self.getPosition(), self.collisionRect)
    
    def getAttackRect(self):
        return rectAdd(self.getPosition(), self.attackRect)
    
    def getHitboxes(self):
        body_rect = rectAdd(self.getPosition(), self.hitbox)
        head_rect = rectAdd(self.head.getPosition(), self.head.hitbox)
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
        return self.keyMap[K_LSHIFT] or self.keyMap[K_RSHIFT] or self.joyMap["SPRINT"]
    
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

    def pickup(self, item):
        item.onPickup(self)
        self.inventory.append(item)

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

        if event.type in (JOYBUTTONDOWN, JOYBUTTONUP) and event.button in self.joyMap.keys():
            self.joyMap[event.button] = event.type == JOYBUTTONDOWN

        if event.type == JOYHATMOTION:
            x, y = event.value

            self.joyMap["LEFT"] = x == -1
            self.joyMap["RIGHT"] = x == 1
            self.joyMap["UP"] = y == 1
            self.joyMap["DOWN"] = y == -1

        if event.type == JOYBUTTONDOWN:
            if event.button == 0:  # BOTTOM BUTTON
                self.joyMap["ATTACK"] = True
            if event.button == 2:  # LEFT BUTTON
                self.joyMap["SPRINT"] = True

        if event.type == JOYBUTTONUP:
            if event.button == 0:
                self.joyMap["ATTACK"] = False
            if event.button == 2:
                self.joyMap["SPRINT"] = False

        if event.type in (JOYBUTTONDOWN, JOYBUTTONUP, JOYHATMOTION):
            print(event)

        self.head.handleEvent(event)
        self.arms.handleEvent(event)

    def update(self, seconds, tmx_map):
        self.velocity = vec(0,0)
        self.moving = False

        if self.health <= 0 or not self.isAlive:
            self.velocity = vec(0,0)
            self.isHurt = False
            super().update(seconds, tmx_map)
            self.head.update(seconds, tmx_map)
            self.arms.update(seconds, tmx_map)
            self.setDying(seconds)
            return
                
        # handle movement input KEYBOARD
        if self.keyMap[K_LEFT] or self.keyMap[K_RIGHT] or self.joyMap["LEFT"] or self.joyMap["RIGHT"]:
            if self.keyMap[K_LEFT] or self.joyMap["LEFT"]:
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
        if self.keyMap[K_UP] or self.keyMap[K_DOWN] or self.joyMap["UP"] or self.joyMap["DOWN"]:
            if self.keyMap[K_UP] or self.joyMap["UP"]:
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
        elif self.keyMap[K_SPACE] and self.attackCooldownTimer <= 0 or self.joyMap["ATTACK"] and self.attackCooldownTimer <= 0:
            self.setAttacking()
        else:
            if self.moving:
                self.setWalking()
            else:
                self.setIdle()

        self.updateSprinting(seconds, self.moving)

        if self.attackCooldownTimer > 0:
            self.attackCooldownTimer -= seconds

        super().update(seconds, tmx_map)

        self.head.update(seconds, tmx_map)
        self.arms.update(seconds, tmx_map)
