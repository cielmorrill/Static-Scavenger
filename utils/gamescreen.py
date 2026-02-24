from .vector import vec

class GameScreen():
    WIDTH = 400
    HEIGHT = 300
    SCALE = 3
    RESOLUTION = vec(WIDTH, HEIGHT)
    UPSCALED = (WIDTH * SCALE, HEIGHT * SCALE)

    WORLD_SIZE = vec(800,400)
    MENU_BARRIER = 35 # pixels

    EPSILON = 0.01

    GRAVITY = 800