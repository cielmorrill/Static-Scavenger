from enum import Enum, auto
from statemachine import StateMachine, State

class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

class Abstract_SM(StateMachine):
    """Base class for all states."""
    def __init__(self, obj):
        self.obj = obj
        super().__init__()

    def enter(self):
        """Called once when entering state."""
        pass

    def exit(self):
        """Called once when leaving state."""
        pass

    def update(self, seconds = 0):
        """Called every frame."""
        pass

    def handle_input(self, input):
        """Handle input and return a new state if needed."""
        return None
    
    def __eq__(self, other):
        """Equality for ease of access. Can be used
        with other StateMachines of the same class or
        with strings which match the current_state.id"""
        
        if type(self) == type(other):
            return self.current_state.id == other.current_state.id
        else:
            return self.current_state.id == other
        