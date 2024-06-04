from enum import Enum

class Elements(Enum):
    WALL = 0
    FLOOR = 1
    PLAYER = 2
    BOX = 3
    GOAL = 4
    BOX_ON_GOAL = 5
    PLAYER_ON_GOAL = 6

char_to_element = {
    '#': Elements.WALL,
    ' ': Elements.FLOOR,
    '@': Elements.PLAYER,
    '$': Elements.BOX,
    '.': Elements.GOAL,
    '*': Elements.BOX_ON_GOAL,
    '+': Elements.PLAYER_ON_GOAL
}

element_to_char = {
    0: '⬛',  # Wall
    1: '⬜',  # Empty space
    2: '🧍',  # Player
    3: '📦',  # Box
    4: '🔲',  # Storage location
    5: '⭐',  # Box on storage location
    6: '🟥'  # Player on storage location (red square)
}