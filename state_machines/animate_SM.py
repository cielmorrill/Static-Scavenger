from enum import Enum, auto
from .abstract_SM import Abstract_SM
from statemachine import StateMachine, State
from utils import magnitude, GameScreen, SpriteManager

class Animate_SM(Abstract_SM):
    """For anything that animates. Adds behavior on transitioning into a state to change animation."""
    def __init__(self, obj):
        super().__init__(obj)
        self.previous_state = None

    def on_enter_state(self):
        state = self.current_state.id
        if self.obj.row != self.obj.rowList[state]:
            self.obj.nFrames = self.obj.nFramesList[state]
            self.obj.frame = 0
            self.obj.row = self.obj.rowList[state]
            self.obj.framesPerSecond = self.obj.framesPerSecondList[state]
            self.obj.animationTimer = 0
            self.obj.image = SpriteManager.getInstance().getSprite(self.obj.fileName,
                                                                   (self.obj.frame, self.obj.row))
            
class Walking_SM(Animate_SM):
    """Two-state FSM for walking / stopping in
       a top-down environment."""
       
    # idle_LR = State(initial=True)
    # idle_U = State()
    # idle_D = State()

    # move_LR   = State()
    # move_U    = State()
    # move_D    = State()

    idle = State(initial = True)
    moving = State()

    updateState = (
    idle.to(moving, cond="hasVelocity") |
    moving.to(idle, cond="noVelocity") |
    idle.to.itself(internal=True) |
    moving.to.itself(internal=True)
    )

    update = (
    idle.to(moving, cond="hasVelocity") |
    moving.to(idle, cond="noVelocity")
    )

    def on_enter_state(self):
        super().on_enter_state()
        direction = self.obj.direction

        if self.current_state == self.moving:
            if direction == "LR":
                row_key = "move_LR"
            elif direction == "UP":
                row_key = "move_U"
            else:
                row_key = "move_D"
        else:
            if direction == "LR":
                row_key = "idle_LR"
            elif direction == "UP":
                row_key = "idle_U"
            else:
                row_key = "idle_D"

        self.obj.nFrames = self.obj.nFramesList[row_key]
        self.obj.frame = 0
        self.obj.row = self.obj.rowList[row_key]
        self.obj.framesPerSecond = self.obj.framesPerSecondList[row_key]
        self.obj.animationTimer = 0
        
    # def enter(self):
    #     if self.hasVelocity() and self != "moving":
    #         self.move()
    #     elif not self.hasVelocity() and self != "standing":
    #         self.stop()
    
    def hasVelocity(self):
        return magnitude(self.obj.velocity) > GameScreen.EPSILON
    
    def noVelocity(self):
        return not self.hasVelocity()
    

    def isLR(self):
        return self.obj.direction == "LR"
    
    def isUP(self):
        return self.obj.direction == "UP"
    
    def isDOWN(self):
        return self.obj.direction == "DOWN"
    

    def notLR(self):
        return not self.isLR()
    
    def notUP(self):
        return not self.isUP()
    
    def notDOWN(self):
        return not self.isDOWN()
    

    def canMoveLR(self):
        return self.hasVelocity() and self.isLR()
    
    def canMoveU(self):
        return self.hasVelocity() and self.isUP()
    
    def canMoveD(self):
        return self.hasVelocity() and self.isDOWN()
    

    def noMoveLR(self):
        return not self.canMoveLR()
    
    def noMoveU(self):
         return not self.canMoveU()
    
    def noMoveD(self):
         return not self.canMoveD()
    

#     idle_LR = State(initial=True)
#     idle_U = State()
#     idle_D = State()

#     move_LR   = State()
#     move_U    = State()
#     move_D    = State()

#     updateState = idle_LR.to(move_LR, cond = "canMoveLR") | \
#                             move_LR.to(idle_LR, cond = "noMoveLR") | \
#                             idle_LR.to.itself(internal = True) | \
#                             move_LR.to.itself(internal = True) | \
#                             idle_LR.to(idle_U, cond = "noMoveU") | \
#                             move_LR.to(idle_U, cond = "noMoveU") | \
#                             idle_LR.to(move_U, cond = "canMoveU") | \
#                             move_LR.to(move_U, cond = "canMoveU") | \
#                             idle_LR.to(idle_D, cond = "noMoveD") | \
#                             move_LR.to(idle_D, cond = "noMoveD") | \
#                             idle_LR.to(move_D, cond = "canMoveD") | \
#                             move_LR.to(move_D, cond = "canMoveD") | \
#                             idle_U.to(move_U, cond = "canMoveU") | \
#                             move_U.to(idle_U, cond = "noMoveU") | \
#                             idle_U.to.itself(internal = True) | \
#                             move_U.to.itself(internal = True) | \
#                             idle_U.to(idle_LR, cond = "noMoveLR") | \
#                             move_U.to(idle_LR, cond = "noMoveLR") | \
#                             idle_U.to(move_LR, cond = "canMoveLR") | \
#                             move_U.to(move_LR, cond = "canMoveLR") | \
#                             idle_U.to(idle_D, cond = "noMoveD") | \
#                             move_U.to(idle_D, cond = "noMoveD") | \
#                             idle_U.to(move_D, cond = "canMoveD") | \
#                             move_U.to(move_D, cond = "canMoveD") | \
#                             idle_D.to(move_D, cond = "canMoveD") | \
#                             move_D.to(idle_D, cond = "noMoveD") | \
#                             idle_D.to.itself(internal = True) | \
#                             move_D.to.itself(internal = True) | \
#                             idle_D.to(idle_U, cond = "noMoveU") | \
#                             move_D.to(idle_U, cond = "noMoveU") | \
#                             idle_D.to(move_U, cond = "canMoveU") | \
#                             move_D.to(move_U, cond = "canMoveU") | \
#                             idle_D.to(idle_LR, cond = "noMoveLR") | \
#                             move_D.to(idle_LR, cond = "noMoveLR") | \
#                             idle_D.to(move_LR, cond = "canMoveLR") | \
#                             move_D.to(move_LR, cond = "canMoveLR") 