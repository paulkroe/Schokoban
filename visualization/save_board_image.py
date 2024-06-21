import pygame
from enum import Enum
import argparse
import numpy as np
import sys
import os
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# print current path
print(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

parser = argparse.ArgumentParser(description='Sokoban Solver')
parser.add_argument('--folder', type=str, default="Microban/", help='foldername')
parser.add_argument('--level_id', type=int, default=1, help='Level ID')
args = parser.parse_args()



def load_level(path):
    with open(path) as f:
        lines = f.readlines()
        height = len(lines)
        width = max(len(line) for line in lines) - 1 # remove newline
        level = np.ones((height, width), dtype=int)*Elements.WALL.value
        for i, line in enumerate(lines):
            for j, char in enumerate(line.replace('\n', '')):
                level[i, j] = char_to_element[char].value
                
        # fix left side:
        for row in level:
            for i in range(len(row)):
                if row[i] == Elements.FLOOR.value:
                    row[i] = Elements.WALL.value
                else:
                    break
        
    return level

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
    '+': Elements.PLAYER_ON_GOAL
}

pygame.init()

# Set the tile size
tile_size = 128

def load_and_scale_sprite(path, size):
    sprite = pygame.image.load(path)
    sprite = pygame.transform.scale(sprite, (size, size))
    return sprite

sprites = {
    Elements.WALL.value: load_and_scale_sprite('visualization/sprites/wall.png', tile_size),
    Elements.FLOOR.value: load_and_scale_sprite('visualization/sprites/floor.png', tile_size),
    Elements.PLAYER.value: load_and_scale_sprite('visualization/sprites/player.png', tile_size),
    Elements.BOX.value: load_and_scale_sprite('visualization/sprites/box.png', tile_size),
    Elements.GOAL.value: load_and_scale_sprite('visualization/sprites/goal.png', tile_size),
    Elements.BOX_ON_GOAL.value: load_and_scale_sprite('visualization/sprites/box_on_goal.png', tile_size),
    Elements.PLAYER_ON_GOAL.value: load_and_scale_sprite('visualization/sprites/player_on_goal.png', tile_size)
}

# load board
path = args.folder+"/level_"+str(args.level_id)+".txt"
board = load_level(path)

board_width = len(board[0])
board_height = len(board)
screen_width = board_width * tile_size
screen_height = board_height * tile_size

# Create a surface for the board
board_surface = pygame.Surface((screen_width, screen_height))

# Draw the board on the surface
for y in range(board_height):
    for x in range(board_width):
        char = board[y][x]
        sprite = sprites[char]
        board_surface.blit(sprite, (x * tile_size, y * tile_size))

# Save the board image
path = "visualization/" + args.folder+"/level_"+str(args.level_id)+".png"
pygame.image.save(board_surface, path)

pygame.quit()
