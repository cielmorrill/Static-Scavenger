from pygame.locals import *
from utils.gamescreen import GameScreen
from utils.vector import vec, rectAdd, magnitude, normalize
from .mobile import Mobile

"""Any creature that can move, collide, take damage, and die."""
# entities must have:
    # states (animation, action, direction, hurt, dying)
    # stats (health/max, attack)
    # movement (velocity, speed/max)
    # collision (world boundaries, other entities)

class Entity(Mobile):
    def __init__(self, position, fileName="", offset=(0,0), maxSpeed=500, row = 0, nFrames = 1):
        super().__init__(position, fileName, offset, maxSpeed, row, nFrames)

        self.animateState = None
        self.actionState = None
        self.direction = None
        self.animate = True

        self.collisionRect = Rect(7,8,int(self.getWidth()),int(self.getHeight()))

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
        self.knockbackStrength = 180      # tweak this
        self.knockbackDecay = 900      # how fast it slows

        # movement attributes
        self.velocity = vec(0,0)
        self.maxSpeed = maxSpeed
        self.base_speed = 100
        self.speed = self.base_speed
        self.sprintMultiplier = 1.5
        self.acceleration = 1000

        # stamina system
        self.maxStamina = 100
        self.stamina = self.maxStamina
        self.staminaRegen = 0      # per second
        self.staminaCooldown = 0      # seconds
        self.staminaCooldownTimer = 0
        self.sprintStaminaCost = 0 # per second

        self.counter = 0

    def getCollisionRect(self):
        return rectAdd(self.getPosition(), self.collisionRect)

    def setIdle(self):
        pass

    def setWalking(self):
        pass

    def setDying(self, seconds):
        self.isAlive = False
        self.setDead(seconds)

    def setDead(self, seconds):
        self.isAlive = False
        self.animate = False
        if self.death_timer > 0:
            self.death_timer -= 1 * seconds

            fade_ratio = self.death_timer / self.death_timer_max
            alpha = int(255 * fade_ratio)
            alpha = max(0, min(255, alpha))

            self.image.set_alpha(alpha)
            return
        self.removeMe = True

    def getHurt(self, attack, attackerPos):
        if self.isInvincible:
            return

        if self.isHurt == False:
            self.isHurt = True
            self.health -= attack

            direction = self.getPosition() - attackerPos
            direction[1] *= 0.75
            direction = normalize(direction)
            self.knockback = direction * self.knockbackStrength
        else:
            return
        
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

            # maxVelocity = self.speed * 1.5
            # if magnitude(self.velocity) > maxVelocity:
            #     self.velocity = normalize(self.velocity) * maxVelocity

    def regenHealth(self, seconds):
        if self.health < self.maxHealth:
                if self.healthCooldownTimer < self.healthCooldown:
                    self.healthCooldownTimer += seconds
                else:
                    self.health += self.healthRegen * seconds
        self.health = max(0, min(self.health, self.maxHealth))

    def touchingCheck(self, bool):
        self.touchingEntity = bool

    def resolveCollision(self, e2):
        rect1 = self.getCollisionRect()
        rect2 = e2.getCollisionRect()

        overlap = rect1.clip(rect2)

        if overlap.width < overlap.height:
            # Horizontal resolution
            if rect1.centerx < rect2.centerx:
                self.setPosition((rect1.x - overlap.width / 2, rect1.y))
            else:
                self.setPosition((rect1.x + overlap.width / 2, rect1.y))
        else:
            # Vertical resolution
            if rect1.centery < rect2.centery:
                self.setPosition((rect1.x, rect1.y - overlap.height / 2))
            else:
                self.setPosition((rect1.x, rect1.y + overlap.height / 2))

    def clampWorldBoundary(self):
        if self.getPosition()[0] <= 0:
            self.velocity[0] = 0
            self.setPosition((0, self.getPosition()[1]))

        if self.getPosition()[1] <= GameScreen.MENU_BARRIER:
            self.velocity[1] = 0
            self.setPosition((self.getPosition()[0], GameScreen.MENU_BARRIER))

        if self.getPosition()[0] + self.getWidth() >= GameScreen.WORLD_SIZE[0]:
            self.velocity[0] = 0
            self.setPosition((GameScreen.WORLD_SIZE[0] - self.getWidth(), self.getPosition()[1]))
            
        if self.getPosition()[1] + self.getHeight() >= GameScreen.WORLD_SIZE[1]:
            self.velocity[1] = 0
            self.setPosition((self.getPosition()[0], GameScreen.WORLD_SIZE[1] - self.getHeight()))

    def handleEvent(self, event):
        return super().handleEvent(event)
    
    def update(self, seconds):
        if self.health <= 0 or not self.isAlive:
            if self.isHurt:
                self.updateHurtState(seconds)
                return
            self.velocity = vec(0,0)
            self.setDying(seconds)
            self.isHurt = False
            super().update(seconds)
            return

        self.updateHurtState(seconds)
        self.regenHealth(seconds)

        super().update(seconds)
    
        self.clampWorldBoundary()