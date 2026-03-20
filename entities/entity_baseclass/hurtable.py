from pygame.locals import Rect
from utils.vector import vec, rectAdd, magnitude, normalize
from .mobile import Mobile

"""Any creature that can move, collide, take damage, and die."""
# entities must have:
    # states (animation, action, direction, hurt, dying)
    # stats (health/max, attack)
    # movement (velocity, speed/max)
    # collision (world boundaries, other entities)

class Hurtable(Mobile):
    def __init__(self, position, fileName="", offset=(0,0), maxSpeed=500, row = 0, nFrames = 1):
        super().__init__(position, fileName, offset, maxSpeed, row, nFrames)

        self.animateState = None
        self.actionState = None
        self.direction = None
        self.animate = True
        self.equippable_offset = vec(0,0)
        self.hurtable = []

        self.collisionRect = Rect(0,0,int(self.getWidth()),int(self.getHeight()))

        self.touchingEntity = False
        self.isHurt = False
        self.isInvincible = False
        self.canAttack = False
        self.isAlive = True
        self.removeMe = False

        self.death_timer_max = 3
        self.death_timer = self.death_timer_max

        # stats
        self.maxHealth = 20.0
        self.health = self.maxHealth
        self.attackPower = 5.0
        self.attackCooldown = 5

        self.hurtTimerBase = 1.0
        self.hurtTimer = 1.0
        self.healthRegen = 0         # per second
        self.healthCooldown = 0      # seconds
        self.healthCooldownTimer = 0

        self.knockback = vec(0, 0)
        self.knockbackStrength = 225      # tweak this
        self.knockbackDecay = 900      # how fast it slows

        # movement attributes
        self.velocity = vec(0,0)
        self.maxSpeed = maxSpeed
        self.base_speed = 100
        self.speed = self.base_speed
        self.sprintMultiplier = 1.5
        self.acceleration = 1000

        self.counter = 0

    def getCollisionRect(self):
        return rectAdd(self.getPosition(), self.collisionRect)

    def setDying(self):
        self.isAlive = False
        self.setDead()

    def setDead(self):
        self.isAlive = False
        self.animate = False
        self.removeMe = True

    def getHurt(self, attack, attackerPos):
        if self.isInvincible or self.isHurt or not self.isAlive:
            return
        if self.health < 0:
            self.isAlive = False

        self.isHurt = True
        self.hurtTimer = self.hurtTimerBase
        self.health -= attack

        direction = self.getPosition() - attackerPos
        direction[1] *= 0.75
        direction = normalize(direction)
        self.knockback = direction * self.knockbackStrength
        
    def updateHurtState(self, seconds):
        if self.isHurt:
            self.hurtTimer -= seconds
            if self.hurtTimer <= 0:
                self.isHurt = False
                self.hurtTimer = self.hurtTimerBase
            self.healthCooldownTimer = 0

            if magnitude(self.knockback) > 0:
                self.velocity = self.knockback

                decayAmount = self.knockbackDecay * seconds
                kb_mag = magnitude(self.knockback)

                if kb_mag <= decayAmount:
                    self.knockback = vec(0, 0)
                else:
                    self.knockback -= normalize(self.knockback) * decayAmount

    def touchingCheck(self, bool):
        self.touchingEntity = bool

    def resolveCollision(self, e2):
        rect1 = self.getCollisionRect()
        rect2 = e2.getCollisionRect()

        collision = rect1.clip(rect2)

        if collision.width == 0 or collision.height == 0:
            return

        if collision.width < collision.height:
            # horizontal collision
            e2.velocity[0] = 0
            if rect2.centerx < rect1.centerx:
                e2.setPosition((rect1.left - e2.getWidth(), e2.getPosition()[1]))
            else:
                e2.setPosition((rect1.right, e2.getPosition()[1]))
        else:
            # vertical collision
            e2.velocity[1] = 0
            if rect2.centery < rect1.centery:
                e2.setPosition((e2.getPosition()[0], rect1.top - e2.getHeight()))
            else:
                e2.setPosition((e2.getPosition()[0], rect1.bottom))

    def handleEvent(self, event):
        return super().handleEvent(event)
    
    def update(self, seconds):
        if self.health <= 0 or not self.isAlive:
            if self.isHurt:
                self.updateHurtState(seconds)
                return
            self.velocity = vec(0,0)
            self.setDying()
            self.isHurt = False
            super().update(seconds)
            return

        self.updateHurtState(seconds)

        super().update(seconds)