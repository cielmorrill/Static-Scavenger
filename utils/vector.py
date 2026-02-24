import numpy as np
from pygame import Rect

def vec(*args):
    """Quick function for making numpy array vectors."""
    return np.array((args)).astype(float)

def pyVec(v):
    return list(map(int, v))

def normalize(vector):
    """Normalize a numpy array."""
    mag = magnitude(vector)
    if mag == 0.0:
        return np.array([1] + [0] * (len(vector)-1)).astype(float)
    return vector / mag

def angleBetween(v1, v2):
    """Returns the angle in radians between vectors."""
    v1_u = normalize(v1)
    v2_u = normalize(v2)
    return np.arccos(np.dot(v1_u, v2_u))
   
def direction(vector):
    """Returns the direction of the vector."""
    return np.atan2(vector[1], vector[0])
    
def magnitude(vector):    
    """Give the magnitude of a vector."""
    return np.linalg.norm(vector)

def sign(vector):
    """returns 1 or -1"""
    return np.sign(vector)

def scale(vector, length):
   """Scales the magnitude of vec to the length.
      First normalizes then scales to appropriate size."""
   return normalize(vector) * length

def rectAdd(vector, rect):
   """Moves the pygame rect top left by vector.
      Returns a rect."""   
   newRect = Rect(rect.left + vector[0], rect.top + vector[1],
                  rect.width, rect.height)
   
   return newRect
   
