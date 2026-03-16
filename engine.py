import pygame
import random
from entities.entity_baseclass.drawable import Drawable
from entities.robot import Robot
from utils.gamescreen import GameScreen
from utils.vector import vec, rectAdd
from tmxmap import TmxMap
from entities.slime import Slime
from entities.objects_or_items.rock import Rock
from entities.objects_or_items.cowboy_hat import Cowboy_Hat

class GameEngine(object):
    def __init__(self):   
        self.transition_cooldown = 0
        self.tmx_map = TmxMap(fileName= "test_mine_outside.tmx")
     
        self.robot = Robot((200,400))
        shifted_pos = self.robot.getPosition()[1] + self.robot.getHeight() + GameScreen.MENU_BARRIER
        self.robot.setPosition((200, shifted_pos))

        # self.hat = Cowboy_Hat((0,0))
        # self.hat.setPickup(self.robot.head)
        # self.hat.setEquip(self.robot.head, self.robot.head.equippable_offset)
        
        self.passive_entities = []

        self.enemies = []

        self.items = []
        # self.items.append(self.hat)

        self.spawn_entities()

    def spawn_entities(self):
        self.enemies.clear()
        self.passive_entities.clear()

        for spawn_area in self.tmx_map.spawns:
            x, y = spawn_area["pos"]
            w, h = spawn_area.get("size", (0,0))
            types = spawn_area["type"].split()  # split the accepted_types string
            spawn_chance = spawn_area.get("spawn_chance", 1.0)

            tile = self.tmx_map.tmx_map.tilewidth
            cols = int(w // tile)
            rows = int(h // tile)
            positions = []

            for row in range(rows):
                for col in range(cols):
                    px = x + col * tile
                    py = y + row * tile
                    positions.append((px, py))

            random.shuffle(positions)

            for spawn_x, spawn_y in positions:
                if random.random() <= spawn_chance:  # use the chance
                    chosen_type = random.choice(types)

                    # ENEMY SPAWNS

                    if chosen_type == "slime":
                        self.enemies.append(Slime((spawn_x, spawn_y)))

                    # PASSIVE ENTITY SPAWNS

                    elif chosen_type in ("brown_rock", "grey_rock"):
                        self.passive_entities.append(
                            Rock((spawn_x, spawn_y), f"{chosen_type}.png")
                        )

    def draw(self, drawSurface):
        self.tmx_map.draw(drawSurface)

        for p in self.passive_entities:
            p.draw(drawSurface)

        for e in self.enemies:
            e.draw(drawSurface)

        self.robot.draw(drawSurface)

        # self.ore.draw(drawSurface)

        for i in self.items:
            i.draw(drawSurface)
                
        # show collision
        # pygame.draw.rect(drawSurface, (255, 0, 0), rectAdd(-Drawable.CAMERA_OFFSET, self.robot.getCollisionRect()))

        # pygame.draw.rect(drawSurface, (255, 0, 0), rectAdd(-Drawable.CAMERA_OFFSET, self.rock.getCollisionRect()))

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

        for i in self.items:
            i.handleEvent(event)

    def update(self, seconds):
        self.robot.update(seconds, self.tmx_map)

        if not self.robot.isAlive:
            self.enemies.clear()
            return
        
        self.transition_cooldown -= seconds
        transition = self.tmx_map.check_transition(self.robot)

        # transition map & spawn entities
        if transition and transition["target"] and self.transition_cooldown <= 0:
            self.tmx_map = TmxMap(fileName=transition["target"])
            self.robot.setPosition(transition["spawn"])
            self.transition_cooldown = 1
            self.spawn_entities()
            return
                
        for e in self.enemies[:]:
            if e.removeMe:
                self.enemies.remove(e)

        for p in self.passive_entities[:]:
            if p.removeMe:
                self.passive_entities.remove(p)

        # check for enemy collision with robot & robot attack collision w/ enemies
        for e in self.enemies:
            collision = e.getCollisionRect().clip(self.robot.getCollisionRect())

            if collision.width != 0 and collision.height != 0 and e.isAlive:
                # ROBOT GETS HURT
                # flash red, knockback, temporary invulnerability, health decrease
                if not self.robot.isHurt and self.robot.isAlive:
                    self.robot.getHurt(e.attackPower, e.getPosition())
            else:
                e.touchingCheck(False)

            if self.robot.actionState == "isAttacking":
                collision = e.getCollisionRect().clip(self.robot.getAttackRect())
                if collision.width != 0 and collision.height != 0 and e.isAlive:
                    # ENEMY GETS HURT
                    # flash red, knockback, temporary invulnerability, health decrease
                    if not e.isHurt and e.isAlive:
                        e.getHurt(self.robot.attackPower, self.robot.getPosition())

        # check for entity collision with robot
        for p in self.passive_entities:
            collision = p.getCollisionRect().clip(self.robot.getCollisionRect())
            if collision.width != 0 and collision.height != 0 and p.isAlive:
                p.resolveCollision(self.robot)

            if self.robot.actionState == "isAttacking":
                collision = p.getCollisionRect().clip(self.robot.getAttackRect())
                if collision.width != 0 and collision.height != 0 and p.isAlive:
                    if not p.isDamaged and p.isAlive:
                        p.getHurt(self.robot.attackPower, self.robot.getPosition())
            
        # enemy check for robot in awareness range
        for e in self.enemies:
            collision = e.getAwarenessRect().clip(self.robot.getCollisionRect())
            if collision.width != 0 and collision.height != 0 and self.robot.isAlive:
                e.robotAwareness(True)
            else:
                e.robotAwareness(False)

        # enemy check for robot in attack range
        for e in self.enemies:
            collision = e.getAttackRect().clip(self.robot.getCollisionRect())
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

                collision = e1.getCollisionRect().clip(e2.getCollisionRect())
                if collision.width != 0 and collision.height != 0 and e1.isAlive and e2.isAlive:
                    e1.resolveCollision(e2)

        # check for enemy-passive entity collision
        for i in range(len(self.enemies)):
            for j in range(len(self.passive_entities)):
                e1 = self.enemies[i]
                e2 = self.passive_entities[j]

                collision = e1.getCollisionRect().clip(e2.getCollisionRect())
                if collision.width != 0 and collision.height != 0 and e1.isAlive and e2.isAlive:
                    e1.resolveCollision(e2)

        for e in self.enemies:
            e.update(seconds, self.robot, self.tmx_map)

        for p in self.passive_entities:
            p.update(seconds, self.tmx_map)

        for item in self.items:
            item.update()
            if self.robot.getCollisionRect().colliderect(item.getCollisionRect()) and item.canPickUp:
                self.robot.pickup(item)

        # CAMERA
        Drawable.CAMERA_OFFSET = self.robot.getPosition() + (self.robot.getSize() / 2) - GameScreen.RESOLUTION / 2
        for i in range(2):
            Drawable.CAMERA_OFFSET[i] = max(0, 
                                            min(Drawable.CAMERA_OFFSET[i], GameScreen.WORLD_SIZE[i] - GameScreen.RESOLUTION[i]))