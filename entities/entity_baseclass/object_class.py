from pygame.locals import Rect
from utils.gamescreen import GameScreen
from utils.vector import vec, rectAdd
from .mobile import Mobile

"""Any creature that can move, collide, take damage, and die."""
# entities must have:
    # states (animation, action, direction, hurt, dying)
    # stats (health/max, attack)
    # movement (velocity, speed/max)
    # collision (world boundaries, other entities)

class Object_Class(Mobile):
    def __init__(self, position, fileName="", offset=(0,0), maxSpeed=500, row = 0, nFrames = 1):
        super().__init__(position, fileName, offset, maxSpeed, row, nFrames)

        self.animateState = None
        self.actionState = None
        self.direction = None
        self.animate = False
        self.moving = False
        self.frame = 0
        self.hurtable = []

        self.collisionRect = Rect(0,0,int(self.getWidth()),int(self.getHeight()))

        self.isDamaged = False
        self.isInvincible = False
        self.canAttack = False
        self.isAlive = True
        self.removeMe = False

        self.death_timer_max = 3
        self.death_timer = self.death_timer_max

        # stats
        self.maxHealth = 20.0
        self.health = self.maxHealth

        self.hurtTimerBase = 1.0
        self.hurtTimer = 1.0
        self.healthRegen = 0         # per second
        self.healthCooldown = 0      # seconds
        self.healthCooldownTimer = 0

        self.counter = 0

    def getCollisionRect(self):
        return rectAdd(self.getPosition(), self.collisionRect)

    def setDying(self, seconds):
        self.isAlive = False
        self.shadow = None
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
        if self.isInvincible or self.isDamaged or not self.isAlive:
            return

        self.isDamaged = True
        self.hurtTimer = self.hurtTimerBase
        self.health -= attack
        
    def updateHurtState(self, seconds):
        if self.isDamaged:
            self.hurtTimer -= seconds
            if self.hurtTimer <= 0:
                self.isDamaged = False
                self.hurtTimer = self.hurtTimerBase
            self.healthCooldownTimer = 0

    def regenHealth(self, seconds):
        if self.health < self.maxHealth:
                if self.healthCooldownTimer < self.healthCooldown:
                    self.healthCooldownTimer += seconds
                else:
                    self.health += self.healthRegen * seconds
        self.health = max(0, min(self.health, self.maxHealth))

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

    def resolveTileCollision(self, tmx_map):
        blocked_rects = tmx_map.getBlockedTileRects(self)

        x, y = self.getPosition()
        width = self.getWidth()
        height = self.getHeight()

        for tile in blocked_rects:
            x_percent = abs((x - tile.x) / tile.width)
            y_percent = abs((y - tile.y) / tile.height)
            if x_percent > y_percent:
                # LEFT side of tile
                if x + width > tile.left and x < tile.left:
                    x = tile.left - width
                    self.velocity[0] = 0
                # RIGHT side of tile
                if x < tile.right and x + width > tile.right:
                    x = tile.right
                    self.velocity[0] = 0
            else:
                # TOP side of tile
                if y + height > tile.top and y < tile.top:
                    y = tile.top - height
                    self.velocity[1] = 0
                # BOTTOM side of tile
                if y < tile.bottom and y + height > tile.bottom:
                    y = tile.bottom
                    self.velocity[1] = 0

        self.setPosition((x, y))

    def handleEvent(self, event):
        return super().handleEvent(event)
    
    def update(self, seconds, tmx_map):
        if self.health <= 0 or not self.isAlive:
            if self.isDamaged:
                self.isDamaged = False
            self.velocity = vec(0,0)
            self.setDying(seconds)
            self.isDamaged = False
            super().update(seconds)
            return

        self.updateHurtState(seconds)
        self.regenHealth(seconds)

        super().update(seconds)
    
        self.clampWorldBoundary()
        self.resolveTileCollision(tmx_map)