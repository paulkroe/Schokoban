import sys
import os
import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from game.GameElements import Elements, char_to_element, element_to_char
from scipy.special import comb
import csv


def find_elements(elements, level):
        if isinstance(elements, int):
            pos = np.where(level == elements)
        else:
            pos = np.where(np.isin(level, elements))

        return list(zip(pos[0], pos[1]))

def count_boxes(path):
    # open txt file and count the number of boxes
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
    
    # count boxes
    box_positions = find_elements([Elements.BOX.value, Elements.BOX_ON_GOAL.value], level)
    tiles = find_elements([Elements.GOAL.value, Elements.BOX.value, Elements.PLAYER_ON_GOAL, Elements.PLAYER.value, Elements.FLOOR.value, Elements.BOX_ON_GOAL.value], level)
    return len(tiles), len(box_positions)

def calculate_tiles(path):
    # open txt file and count the number of boxes
    board = np.load(path)
    # return number of ones in board
    return np.sum(board)

# calculate search space complexity for kids levels
folder_path = 'kids_levels/'
files = os.listdir(folder_path)
level_files = [file for file in files if file.startswith('level')]
NUM_LEVELS = len(level_files)

comp = []
for i in range(1, NUM_LEVELS+1):
    
    path = f"kids_levels/level_{i}.txt"
    n, b = count_boxes(path)
    path = f"deadlock_detection/kids/level_{i}.npy"
    p = calculate_tiles(path) # number of tiles that don't immediately lead to deadlocks
    comp.append([n, int(p), b, int(comb(p, b)*(n-b))])
 
# save results as csv
with open('utils/kids_search_space_comp.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['tiles', 'non freezing tiles', 'stones', 'search space size'])
    for values in comp:
        writer.writerow(values)
  

# calculate search space complexity for Mircoban levels
folder_path = 'levels/'
files = os.listdir(folder_path)
level_files = [file for file in files if file.startswith('level')]
NUM_LEVELS = len(level_files)

comp = []
for i in range(1, NUM_LEVELS+1):
    
    path = f"levels/level_{i}.txt"
    n, b = count_boxes(path)
    path = f"deadlock_detection/Microban/level_{i}.npy"
    p = calculate_tiles(path) # number of tiles that don't immediately lead to deadlocks
    comp.append([n, int(p), b, int(comb(p, b)*(n-b))])

# save results as csv
with open('utils/Microban_search_space_comp.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['tiles', 'non freezing tiles', 'stones', 'search space size'])
    for values in comp:
        writer.writerow(values)