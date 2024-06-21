import pygame
from enum import Enum

# Define the game elements
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
    '+': Elements.PLAYER_ON_GOAL,
    'x': 'x',
    'o': 'o',
    'i': 'i',
    "-": '-',
    ">": '>',
    "ü": 'ü',
    "ö": 'ö',
    'q': 'q',
    'w': 'w',
    'e': 'e'
} 

pygame.init()

# Set the tile size
tile_size = 128

def load_and_scale_sprite(path, size):
    sprite = pygame.image.load(path)
    sprite = pygame.transform.scale(sprite, (size, size))
    return sprite

sprites = {
    Elements.WALL: load_and_scale_sprite('visualization/sprites/wall.png', tile_size),
    Elements.FLOOR: load_and_scale_sprite('visualization/sprites/floor.png', tile_size),
    Elements.PLAYER: load_and_scale_sprite('visualization/sprites/player.png', tile_size),
    Elements.BOX: load_and_scale_sprite('visualization/sprites/box.png', tile_size),
    Elements.GOAL: load_and_scale_sprite('visualization/sprites/goal.png', tile_size),
    Elements.BOX_ON_GOAL: load_and_scale_sprite('visualization/sprites/box_on_goal.png', tile_size),
    Elements.PLAYER_ON_GOAL: load_and_scale_sprite('visualization/sprites/player_on_goal.png', tile_size),
    'x': load_and_scale_sprite('visualization/sprites/player_interior.png', tile_size),
    'o': load_and_scale_sprite('visualization/sprites/floor_interior.png', tile_size),
    'i': load_and_scale_sprite('visualization/sprites/goal_interior.png', tile_size),
    '-': load_and_scale_sprite('visualization/sprites/arrow.png', tile_size),
    '>': load_and_scale_sprite('visualization/sprites/move_box.png', tile_size),
    'ö': load_and_scale_sprite('visualization/sprites/arrow_player.png', tile_size),
    'ü': load_and_scale_sprite('visualization/sprites/move_goal.png', tile_size),
    'q': load_and_scale_sprite('visualization/sprites/uparrow.png', tile_size),
    'w': load_and_scale_sprite('visualization/sprites/downarrow.png', tile_size),
    'e': load_and_scale_sprite('visualization/sprites/goal_box.png', tile_size)
}

board = [
"#########",
"#.     .#",
"#       #",
"#  #$#  #",
"#  $ $  #",
"#  #$#  #",
"#   @   #",
"#.     .#",
"#########"
]
board_width = len(board[0])
board_height = len(board)
screen_width = board_width * tile_size
screen_height = board_height * tile_size

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Sokoban')

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw the board
    for y in range(board_height):
        for x in range(board_width):
            char = board[y][x]
            screen.blit(sprites[char_to_element[char]], (x * tile_size, y * tile_size))

    pygame.display.flip()

pygame.quit()
