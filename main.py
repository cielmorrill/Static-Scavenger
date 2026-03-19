import pygame
from engine import GameEngine
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
    
    gameClock = pygame.time.Clock()
    
    RUNNING = True
    
    while RUNNING:
        gameEngine.draw(drawSurface)
        
        pygame.transform.scale(drawSurface,
                               pyVec(GameScreen.UPSCALED),
                               screen)
     
        pygame.display.flip()
        
        # event handling, gets all event from the eventqueue
        for event in pygame.event.get():
            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                # change the value to False, to exit the main loop
                RUNNING = False
            else:
                gameEngine.handleEvent(event)
        
        gameClock.tick(60)
        seconds = gameClock.get_time() / 1000
        gameEngine.update(seconds)
    
    pygame.quit()


if __name__ == '__main__':
    main()