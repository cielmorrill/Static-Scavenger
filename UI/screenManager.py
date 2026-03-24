from FSMs import ScreenManagerFSM
from . import TextEntry, EventMenu
from gameObjects import GameEngine
from utils.vector import vec
from utils.gamescreen import GameScreen

from pygame.locals import *

class ScreenManager(object):
      
    def __init__(self):
        self.game = GameEngine()
        self.state = ScreenManagerFSM(self)
        self.pausedText = TextEntry(vec(0,0),
                                    "Paused")
        
        size = self.pausedText.getSize()
        midpoint = GameScreen.RESOLUTION // 2 - size
        self.pausedText.position = vec(*midpoint)
        
        self.mainMenu = EventMenu("background.png", 
                                  fontName="default8")
        self.mainMenu.addOption("start", 
                                "Start Game",
                                 GameScreen.RESOLUTION // 2 - vec(0,50),
                                 lambda x: None,
                                 center="both")
        self.mainMenu.addOption("exit", 
                                "Exit Game",
                                 GameScreen.RESOLUTION // 2 + vec(0,50),
                                 lambda x: None,
                                 center="both")
    
    
    def draw(self, drawSurf):
        if self.state.isInGame():
            self.game.draw(drawSurf)
        
            if self.state == "paused":
                self.pausedText.draw(drawSurf)
        
        elif self.state == "mainMenu":
            self.mainMenu.draw(drawSurf)
    
    def handleEvent(self, event):
        if self.state in ["game", "paused"]:
            if event.type == KEYDOWN and event.key == K_m:
                self.state.quitGame()
            elif event.type == KEYDOWN and event.key == K_p:
                self.state.pause()
                
            else:
                self.game.handleEvent(event)

        elif self.state == "mainMenu":
            choice = self.mainMenu.handleEvent(event)
            
            if choice == "start":
                self.state.startGame()
            elif choice == "exit":
                return "exit"
     
    
    def update(self, seconds):      
        if self.state == "game":
            self.game.update(seconds)
        elif self.state == "mainMenu":
            self.mainMenu.update(seconds)
    