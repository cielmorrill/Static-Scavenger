import pygame
from entities.entity_baseclass.drawable import Drawable
from entities.robot import Robot
from utils.gamescreen import GameScreen
from utils.vector import vec
from tmxmap import TmxMap
from entities.slime import Slime

class GameEngine(object):
    def __init__(self):   
        self.tmx_map = TmxMap(fileName= "cave_walled_2.0.tmx")
     
        self.robot = Robot((400,400))
        shifted_pos = self.robot.getPosition()[1] + self.robot.getHeight() + GameScreen.MENU_BARRIER
        self.robot.setPosition((400, shifted_pos))
        
        self.slime = Slime((400,600))

        self.passive_entities = []

        self.enemies = []
        self.enemies.append(self.slime)

    def draw(self, drawSurface):
        self.tmx_map.draw(drawSurface)

        for p in self.passive_entities:
            p.draw(drawSurface)

        for e in self.enemies:
            e.draw(drawSurface)

        self.robot.draw(drawSurface)
                
        # show collision
        # pygame.draw.rect(drawSurface, (255, 0, 0), self.slime.getCollisionRect())
        # for rect in self.robot.getCollisionRect():
        #     pygame.draw.rect(drawSurface, (255, 0, 0), rect)
        # pygame.draw.rect(drawSurface, (255, 0, 0), self.robot.arms.getAttackRect())

        # draw health meter
        pygame.draw.rect(drawSurface, (255, 255, 255), pygame.Rect(8,4,104,14))
        pygame.draw.rect(drawSurface, (70,70,70), pygame.Rect(10,6,100,10))
        # scale the width of the stamina meter based on current stamina
        scaledWidth = int((self.robot.health / self.robot.maxHealth) * 100)
        if scaledWidth < 0:
            scaledWidth = 0
        pygame.draw.rect(drawSurface,(253, 218, 13), pygame.Rect(10,6,scaledWidth,10))

        # draw stamina meter
        pygame.draw.rect(drawSurface, (255, 255, 255), pygame.Rect(8,22,104,14))
        pygame.draw.rect(drawSurface, (70,70,70), pygame.Rect(10,24,100,10))
        # scale the width of the stamina meter based on current stamina
        scaledWidth = int((self.robot.stamina / self.robot.maxStamina) * 100)
        if scaledWidth < 0:
            scaledWidth = 0
        pygame.draw.rect(drawSurface,(89, 232, 235), pygame.Rect(10,24,scaledWidth,10))
            
    def handleEvent(self, event):    
        self.robot.handleEvent(event)

        for p in self.passive_entities:
            p.handleEvent(event)

        for e in self.enemies:
            e.handleEvent(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = vec(*event.pos) / GameScreen.SCALE
            newSlime = Slime(pos)
            self.enemies.append(newSlime)
    
    def update(self, seconds):
        self.robot.update(seconds, self.tmx_map)

        if not self.robot.isAlive:
            self.enemies.clear()
            return
        
        for e in self.enemies[:]:
            if e.removeMe:
                self.enemies.remove(e)

        # check for enemy collision with robot & robot attack collision w/ enemies
        for e in self.enemies:
            for rect in self.robot.getCollisionRect():
                collision = e.getCollisionRect().clip(rect)

                if collision.width != 0 and collision.height != 0 and e.isAlive:
                    # ROBOT GETS HURT
                    # flash red, knockback, temporary invulnerability, health decrease
                    if not self.robot.isHurt and self.robot.isAlive:
                        self.robot.getHurt(e.attackPower, e.getPosition())
                else:
                    e.touchingCheck(False)
            if self.robot.actionState == "isAttacking":
                collision = e.getCollisionRect().clip(self.robot.arms.getAttackRect())
                if collision.width != 0 and collision.height != 0 and e.isAlive:
                    # ENEMY GETS HURT
                    # flash red, knockback, temporary invulnerability, health decrease
                    if not e.isHurt and e.isAlive:
                        e.getHurt(self.robot.attackPower, self.robot.getPosition())

        # check for entity collision with robot
        for p in self.passive_entities:
            for rect in self.robot.getCollisionRect():
                collision = p.getCollisionRect().clip(rect)
                if collision.width != 0 and collision.height != 0 and p.isAlive:
                    p.resolveCollision(self.robot)
            
        # enemy check for robot in awareness range
        for e in self.enemies:
            for rect in self.robot.getCollisionRect():
                collision = e.getAwarenessRect().clip(rect)
                if collision.width != 0 and collision.height != 0 and self.robot.isAlive:
                    e.robotAwareness(True)
                else:
                    e.robotAwareness(False)

        # enemy check for robot in attack range
        for e in self.enemies:
            for rect in self.robot.getCollisionRect():
                collision = e.getAttackRect().clip(rect)
                if collision.width != 0 and collision.height != 0 and self.robot.isAlive:
                    e.attackCheck(True)
                else:
                    e.attackCheck(False)

        # check for enemy-enemy collision
        for i in range(len(self.enemies)):
            for j in range(i + 1, len(self.enemies)):
                e1 = self.enemies[i]
                e2 = self.enemies[j]

                collision = e1.getCollisionRect().clip(e2.getCollisionRect())
                if collision.width != 0 and collision.height != 0 and e1.isAlive and e2.isAlive:
                    e1.resolveCollision(e2)

        # check for passive entity-passive entity collision
        for i in range(len(self.passive_entities)):
            for j in range(i + 1, len(self.passive_entities)):
                e1 = self.passive_entities[i]
                e2 = self.passive_entities[j]

                collision = e1.getCollisionRect().clip(e2.getCollisionRect() and e1.isAlive and e2.isAlive)
                if collision.width != 0 and collision.height != 0:
                    e1.resolveCollision(e2)

        for e in self.enemies:
            e.update(seconds, self.robot, self.tmx_map)

        for p in self.passive_entities:
            p.update(seconds, self.tmx_map)

        # CAMERA
        Drawable.CAMERA_OFFSET = self.robot.getPosition() + (self.robot.getSize() / 2) - GameScreen.RESOLUTION / 2
        for i in range(2):
            Drawable.CAMERA_OFFSET[i] = max(0, 
                                            min(Drawable.CAMERA_OFFSET[i], GameScreen.WORLD_SIZE[i] - GameScreen.RESOLUTION[i]))