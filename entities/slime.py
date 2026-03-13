from .entity_baseclass import Enemy
import pygame
from utils.vector import vec, magnitude, scale, sign
from pygame import image, Surface, SRCALPHA, Rect
from utils.gamescreen import GameScreen
from .entity_baseclass import Drawable

class Slime(Enemy):
    def __init__(self, position, fileName="slime_sprite.png", offset=(0,0), maxSpeed=100, row = 0, nFrames = 1):
        super().__init__(position, fileName, offset, maxSpeed, row, nFrames)

        fileName = "slime_sprite.png"
        self.animateState = None
        self.actionState = None
        self.animate = True
        self.direction = "DOWN"     # ["UP", "DOWN"]
        self.equippable_offset = vec(1, -3)

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
        self.jumpHeight = 0
        self.maxJumpHeight = 30
        self.jumpDirection = vec(0,0)

        self.counter = 0

    def getShadowPos(self):
        shadow_pos = self.position - Drawable.CAMERA_OFFSET

        # place shadow at entity feet
        shadow_pos[1] += self.getHeight() - self.shadow.get_height() - 1
        shadow_pos[0] += (self.getWidth() - self.shadow.get_width()) // 2

        return shadow_pos

    
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

    def setJump(self, robot):
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
        elif self.frame >= 4 and self.frame < 8:  # rising
            if not self.shadow:
                self.createShadow()
                self.isInvincible = True
            frame_float = self.frame + (self.getAnimationTimer() * self.getFPS())
            progress = (frame_float - 4) / 4
            self.jumpHeight = -self.maxJumpHeight * progress
        elif self.frame >= 8 and self.frame < 12:  # falling
            frame_float = self.frame + (self.getAnimationTimer() * self.getFPS())
            progress = (frame_float - 8) / 4
            self.jumpHeight = -self.maxJumpHeight * (1 - progress)
        elif self.frame == 13:
            self.isInvincible = False
            self.shadow = None
        elif self.frame == 15:
            self.jumpHeight = 0
            self.actionState = "isIdle"
            self.attackCooldown = 2

    def draw(self, drawSurface):
    # draw shadow at ground
        if self.shadow:
            scale = max(0.6, 1 - abs(self.jumpHeight) / self.maxJumpHeight)
            new_width = int(self.shadow.get_width() * scale)
            new_height = int(self.shadow.get_height() * scale)
            scaled_shadow = pygame.transform.scale(self.shadow, (new_width, new_height))

            shadow_pos = self.getShadowPos()

            # re-center scaled shadow
            shadow_pos[0] += (self.shadow.get_width() - new_width) - 1
            shadow_pos[1] += (self.shadow.get_height() - new_height) // 2
            drawSurface.blit(scaled_shadow, shadow_pos)

        # draw sprite higher
        draw_pos = self.position - Drawable.CAMERA_OFFSET
        draw_pos[1] += self.jumpHeight

        flippedImage = pygame.transform.flip(self.image, *self.flipped)
        if self.isHurt:
            hurt_image = flippedImage.copy()
            hurt_image.fill((255,0,0), special_flags=pygame.BLEND_RGBA_MULT)
            flippedImage = hurt_image
        drawSurface.blit(flippedImage, draw_pos)
 
    def update(self, seconds, robot, tmx_map):
        super().update(seconds, robot, tmx_map)

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
            self.setJump(robot)

        if self.attackCooldown > 0:
            self.attackCooldown -= seconds

        if self.animateState not in ["isAttacking", "isDying"]:
            self.setIdle()