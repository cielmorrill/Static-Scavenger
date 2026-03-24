import pygame
from engine import GameEngine
from utils.soundManager import SoundManager
from UI.menu import EventMenu
from utils.vector import vec, pyVec
from utils.gamescreen import *

def main():
    #Initialize the module

    pygame.init()
    pygame.font.init()

    pygame.joystick.init()

    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()

    #Get the screen 
    screen = pygame.display.set_mode(pyVec(GameScreen.UPSCALED))
    drawSurface = pygame.Surface(pyVec(GameScreen.RESOLUTION))

    gameEngine = GameEngine()
    state = "menu"

    mainMenu = EventMenu("background.png", fontName="default8")

    mainMenu.addOption(
        "start",
        "Press 1 to Start Game",
        GameScreen.RESOLUTION // 2 - vec(0,50),
        lambda x: x.type == pygame.KEYDOWN and x.key == pygame.K_1,
        center="both"
    )

    mainMenu.addOption(
        "exit",
        "Press 2 to Exit Game",
        GameScreen.RESOLUTION // 2 + vec(0,50),
        lambda x: x.type == pygame.KEYDOWN and x.key == pygame.K_2,
        center="both"
    )

    deathMenu = EventMenu("background.png", fontName="default8")

    deathMenu.addOption(
        "continue",
        "Press 1 to Continue",
        GameScreen.RESOLUTION // 2 - vec(0,50),
        lambda x: x.type == pygame.KEYDOWN and x.key == pygame.K_1,
        center="both"
    )

    deathMenu.addOption(
        "quit",
        "Press 2 to Quit to Menu",
        GameScreen.RESOLUTION // 2 + vec(0,50),
        lambda x: x.type == pygame.KEYDOWN and x.key == pygame.K_2,
        center="both"
    )
    
    gameClock = pygame.time.Clock()
    
    RUNNING = True

    sm = SoundManager.getInstance()
    sm.playBGM("Pookatori and Friends.mp3")
    
    while RUNNING:
        # DRAW
        if state == "menu":
            mainMenu.draw(drawSurface)
        elif state == "game":
            gameEngine.draw(drawSurface)
        elif state == "inventory":
            gameEngine.draw(drawSurface)
            pass
        elif state == "death":
            gameEngine.draw(drawSurface)
            deathMenu.draw(drawSurface)

        pygame.transform.scale(drawSurface,
                            pyVec(GameScreen.UPSCALED),
                            screen)

        pygame.display.flip()

        # EVENT HANDLING
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                RUNNING = False

            elif state == "menu":
                choice = mainMenu.handleEvent(event)

                if choice == "start":
                    state = "game"
                elif choice == "exit":
                    RUNNING = False

            elif state == "game":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_i:
                    state = "inventory"
                else:
                    gameEngine.handleEvent(event)

            elif state == "inventory":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_i:
                    state = "game"
                else:
                    pass
            
            elif state == "death":
                choice = deathMenu.handleEvent(event)

                if choice == "continue":
                    gameEngine = GameEngine()
                    state = "game"

                elif choice == "quit":
                    state = "menu"

        # UPDATE
        gameClock.tick(60)
        seconds = gameClock.get_time() / 1000

        if state in ["game", "death"]:
            gameEngine.update(seconds)
            if state == "game" and gameEngine.gameover:
                state = "death"
    
    pygame.quit()


if __name__ == '__main__':
    main()