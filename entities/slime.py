from .entity_baseclass import Enemy
from utils.vector import vec, magnitude, scale, sign, rectAdd
from pygame import image, Surface, SRCALPHA, Rect
from utils.gamescreen import GameScreen

class Slime(Enemy):
    def __init__(self, position, fileName="slime_sprite.png", offset=(0,0), maxSpeed=100, row = 0, nFrames = 1):
        super().__init__(position, fileName, offset, maxSpeed, row, nFrames)

        fileName = "slime_sprite.png"
        self.animateState = None
        self.actionState = None
        self.animate = True
        self.direction = "DOWN"     # ["UP", "DOWN"]

        self.collisionRect = Rect(7,8,int(self.getWidth() - 12),int(self.getHeight() - 15))
        self.awarenessRect = Rect(0,0,int(self.getWidth() * 7),int(self.getHeight() * 7))
        self.attackRect = Rect(0,0,int(self.getWidth() * 5),int(self.getHeight() * 5))

        self.seesRobot = False
        self.touchingEntity = False
        self.canAttack = False
        self.attackCooldown = 5

        # stats
        self.maxHealth = 50.0
        self.health = self.maxHealth
        self.attackPower = 10.0

        # movement
        self.velocity = vec(0,0)
        self.maxSpeed = maxSpeed
        self.speed = 50
        self.jumpSpeed = 100
        self.maxJumpSpeed = 1000
        self.jumpAcceleration = 4000

        self.counter = 0
    
    def setIdle(self):
        if self.animateState != "isIdle":
            self.setFPS(4)
            self.animateState = "isIdle"
            self.frame = 0
            self.nFrames = 6

        if self.direction == "DOWN":
            self.row = 0
        else:
            self.row = 1

    def setDying(self, seconds):
        if self.animateState != "isDying":
            self.animateState = "isDying"
            self.setFPS(4)
            self.frame = 0
            self.nFrames = 6
            self.isAlive = False

        if self.direction == "DOWN":
            self.row = 2
        else:
            self.row = 3

        if self.frame >= self.nFrames - 1:
            self.setDead(seconds)
            return

    def setAttacking(self):
        if self.attackCooldown > 0:
            self.canAttack = False
            self.setIdle()
            return
        if self.animateState == "isAttacking":
            return
        else:
            self.animateState = "isAttacking"
            self.setFPS(12)
            self.row = 4
            self.frame = 0
            self.nFrames = 16

    def setJump(self, seconds, robot):
        deadzone = 5   # pixels
        direction = robot.getPosition() - self.getPosition()
        
        if abs(direction[0]) < deadzone:
            direction[0] = 0
        if abs(direction[1]) < deadzone:
            direction[1] = 0
        
        direction = sign(direction)
        self.velocity = direction * self.jumpSpeed

        # handle diagonal speed normalization
        if magnitude(self.velocity) > self.jumpSpeed:
            self.velocity = scale(self.velocity, self.jumpSpeed)

        if self.frame < 4:
            self.velocity = vec(0,0)
        elif self.frame >= 4 and self.frame < 7: # jump up
            self.velocity[1] -= self.jumpAcceleration * seconds
            if self.velocity[1] < -self.maxJumpSpeed:
                self.velocity[1] = -self.maxJumpSpeed
        elif self.frame == 8:
            self.velocity[1] = 0
        elif self.frame >= 9 and self.frame < 12: # fall down
            self.velocity[1] += self.jumpAcceleration * seconds
            if self.velocity[1] > self.maxJumpSpeed:
                self.velocity[1] = self.maxJumpSpeed
        elif self.frame == 15:
            self.velocity[1] = 0
            self.actionState = "isIdle"
            self.attackCooldown = 2
 
    def update(self, seconds, robot):
        super().update(seconds)

        if not self.isAlive:
            return
        
        if self.isHurt:
            return

        if self.seesRobot:
            self.moving = True
            self.chase(robot)
        else:
            self.moving = False
            self.velocity = vec(0,0)

        if self.canAttack:
            self.setAttacking()
            self.setJump(seconds, robot)

        if self.attackCooldown > 0:
            self.attackCooldown -= seconds

        if self.animateState not in ["isAttacking", "isDying"]:
            self.setIdle()