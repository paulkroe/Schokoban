import sys
import os
import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from game.GameElements import Elements, char_to_element
from game.ReverseSokoban import ReverseSokobanBoard
from queue import Queue
import argparse


def load_level(level_id, path):
    with open(path+f"/level_{level_id}.txt") as f:
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


def find_elements(level, elements):
    if isinstance(elements, int):
        pos = np.where(level == elements)
    else:
        pos = np.where(np.isin(level, elements))

    return list(zip(pos[0], pos[1]))

def clear(board):
    mask = (board.level == Elements.WALL.value).astype(int) * Elements.WALL.value
    interior = (board.level != Elements.WALL.value).astype(int) * Elements.FLOOR.value
    board.level = mask + interior

def mark(goal, positions, level_id, path):
    hashes = []
    for (dx, dy) in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
        board = ReverseSokobanBoard(level_id, folder=path)
        player = goal[0] + dx, goal[1] + dy
        if board.level[player] == Elements.WALL.value:
            continue
        else:
            # setup board
            clear(board)
            board.player = player
            board.level[player] = Elements.PLAYER.value
            board.level[goal] = Elements.BOX_ON_GOAL.value
            
            board.interior = sorted(board.find_interior(*board.player))
            board.box_positions = sorted(board.find_elements([Elements.BOX.value, Elements.BOX_ON_GOAL.value]))
            board.hash = board.get_hash()
            
            # bfs
            q = Queue()
            if not board.hash in hashes:
                hashes.append(board.hash)
                positions[board.find_elements([Elements.BOX.value, Elements.BOX_ON_GOAL.value])[0]] = 1
                q.put(board)
            
            while not q.empty():
                board = q.get()
                for move in board.valid_moves():
                    new_board = board.move(*move) # pull the boxes
                    if not new_board.hash in hashes:
                        hashes.append(new_board.hash)
                        positions[new_board.find_elements([Elements.BOX.value, Elements.BOX_ON_GOAL.value])[0]] = 1
                        q.put(new_board)
# save the np.array positions
def save_deadlocks(level_id, positions, path):
    file_path = "deadlock_detection/" + path + "/level_" + str(level_id) + ".npy"
    np.save(file_path, positions)

def compute_deadlocks(level_id, path, verbose=0):
    print("Computing deadlocks for level", level_id)
    level = load_level(level_id, path)
    
    goals = find_elements(level, [Elements.GOAL.value, Elements.BOX_ON_GOAL.value, Elements.PLAYER_ON_GOAL.value])
    
    positions = np.zeros(level.shape)
    for goal in goals:
        mark(goal, positions, level_id, path)
    
    if verbose:
        deadlocks = ReverseSokobanBoard(level_id, folder=path)
        clear(deadlocks)
        print(deadlocks)
        for i in range(level.shape[0]):
            for j in range(level.shape[1]):
                if positions[i, j]:
                    deadlocks.level[i, j] = Elements.BOX.value
        print(deadlocks) 
    save_deadlocks(level_id, positions, path)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sokoban Solver')
    parser.add_argument('--folder', type=str, default="Microban/", help='foldername')
    parser.add_argument('--level_id', type=int, default=-1, help='level id, if -1 then all levels are computed')
    args = parser.parse_args()
    files = os.listdir(args.folder)
    level_files = [file for file in files if file.startswith('level')]
    NUM_LEVELS = len(level_files)

    if args.level_id != -1:
        compute_deadlocks(args.level_id, args.folder, verbose=0)
    else:
        for i in range(1, NUM_LEVELS+1):
            compute_deadlocks(i, args.folder, verbose=0)