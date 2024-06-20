from enum import Enum
import numpy as np
from queue import Queue
from copy import deepcopy

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from reward_functions.min_cost_matching import min_cost_matching
from game.GameElements import Elements, char_to_element, element_to_char
from deadlock_detection.detect_deadlocks import check_deadlock
from deadlock_detection.precompute_deadlocks import compute_deadlocks
from game.reward import Reward

MAX_STEP = 1000

# negative minimum cost perfect matching (Pushing the limits: New developments in single-agent search: Technical report) 

class SokobanBoard:
    
    def __init__(self, level_id, max_steps=MAX_STEP, deadlocks=None, folder=None):
        path = folder+"/level_"+str(level_id)+".txt"
        self.folder = folder
        self.level_id = level_id
        self.level = self.load_level(path) 
        self.player = self.find_elements([Elements.PLAYER.value, Elements.PLAYER_ON_GOAL.value])[0]
        self.steps = 0
        self.max_steps = max_steps
        
        self.interior = sorted(self.find_interior(*self.player))
        self.box_positions = sorted(self.find_elements([Elements.BOX.value, Elements.BOX_ON_GOAL.value]))
        self.hash = self.get_hash()
        
        self.deadlocks = deadlocks
        
        if self.deadlocks is None:
            file_path = "deadlock_detection/"+folder+"level_"+str(level_id)+".npy"
            if not os.path.isfile(file_path) or not (folder in ["Microban/", "Testsuite/"]):
                compute_deadlocks(level_id, folder, verbose=0)
            self.deadlocks = np.load(file_path)
    
    def get_hash(self):
        return str(self.interior) + str(self.box_positions)
    
    def load_level(self, path):
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
    
    def __repr__(self):
        return '\n'.join(''.join(element_to_char[int(elem)] for elem in row) for row in self.level)
    
    def find_elements(self, elements):
        if isinstance(elements, int):
            pos = np.where(self.level == elements)
        else:
            pos = np.where(np.isin(self.level, elements))

        return list(zip(pos[0], pos[1]))
    
    def find_interior(self, x, y):
        interior = [(x, y)]
        positions = Queue()
        positions.put((x, y))

        while not positions.empty():
            x, y = positions.get()
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_x, new_y = x + dx, y + dy
                if self.is_valid_move(new_x, new_y) and not (self.level[new_x, new_y] in [Elements.WALL.value, Elements.BOX.value, Elements.BOX_ON_GOAL.value]):
                    if (new_x, new_y) not in interior:
                        interior.append((new_x, new_y))
                        positions.put((new_x, new_y))

        return interior

    def is_valid_move(self, x, y):
        return 0 <= x < self.level.shape[0] and 0 <= y < self.level.shape[1]

    def valid_moves(self):
        box_positions = self.find_elements([Elements.BOX.value, Elements.BOX_ON_GOAL.value])
        valid_moves_ = set()
        interior = self.find_interior(*self.player)
        for (box_x, box_y) in box_positions:
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                player_x, player_y = box_x - dx, box_y - dy
                if (player_x, player_y) in interior:
                    valid_moves_.add(((player_x, player_y), (dx, dy), (box_x, box_y)))
        
        valid_moves = set()
        for player_pos, d, box_pos in valid_moves_:
            adj_x, adj_y = box_pos[0] + d[0], box_pos[1] + d[1]
            if not self.level[adj_x, adj_y] in [Elements.BOX.value, Elements.BOX_ON_GOAL.value, Elements.WALL.value]:
                valid_moves.add((*player_pos, *d))
       
        return list(valid_moves)

    def move(self, player_x, player_y, dx, dy):
        NUM_BOXES = len(self.find_elements([Elements.BOX.value, Elements.BOX_ON_GOAL.value]))
        NUM_GOALS = len(self.find_elements([Elements.GOAL.value, Elements.BOX_ON_GOAL.value, Elements.PLAYER_ON_GOAL.value]))
        
        new_level = self.level.copy()
        
        # remove player
        assert new_level[self.player] in [Elements.PLAYER.value, Elements.PLAYER_ON_GOAL.value]
        new_level[self.player] = Elements.FLOOR.value if new_level[self.player] == Elements.PLAYER.value else Elements.GOAL.value
        
        # move box
        new_box_x, new_box_y = player_x + 2*dx, player_y + 2*dy
        assert new_level[new_box_x, new_box_y] in [Elements.PLAYER.value, Elements.PLAYER_ON_GOAL.value, Elements.FLOOR.value, Elements.GOAL.value]
        new_level[new_box_x, new_box_y] = Elements.BOX.value if new_level[new_box_x, new_box_y] in [Elements.FLOOR.value, Elements.PLAYER.value] else Elements.BOX_ON_GOAL.value
        
        # move player
        new_player_x, new_player_y = player_x + dx, player_y + dy
        assert new_level[new_player_x, new_player_y] in [Elements.BOX.value, Elements.BOX_ON_GOAL.value]
        new_level[new_player_x, new_player_y] = Elements.PLAYER.value if new_level[new_player_x, new_player_y] == Elements.BOX.value else Elements.PLAYER_ON_GOAL.value
        
        new_board = self.construct(new_level, (new_player_x, new_player_y), self.steps + 1)
        
        NEW_NUM_BOXES = len(new_board.find_elements([Elements.BOX.value, Elements.BOX_ON_GOAL.value]))
        NEW_NUM_GOALS = len(new_board.find_elements([Elements.GOAL.value, Elements.BOX_ON_GOAL.value, Elements.PLAYER_ON_GOAL.value]))
        assert NUM_BOXES == NEW_NUM_BOXES
        assert NUM_GOALS == NEW_NUM_GOALS
        assert len(new_board.find_elements([Elements.PLAYER.value, Elements.PLAYER_ON_GOAL.value])) == 1
        return new_board
    
    def construct(self, level, player, steps):
        new_board = SokobanBoard(level_id=self.level_id, folder=self.folder, max_steps=self.max_steps, deadlocks=self.deadlocks) 
        new_board.level = level
        new_board.player = player
        new_board.steps = steps
        
        new_board.interior = sorted(new_board.find_interior(*new_board.player))
        new_board.box_positions = sorted(new_board.find_elements([Elements.BOX.value, Elements.BOX_ON_GOAL.value]))
        new_board.hash = new_board.get_hash()
        return new_board

    def copy(self):
        return self.construct(level=self.level.copy(), player=self.player, steps=self.steps)
         
    def mark(self):
        interior = self.find_interior(*self.player)
        level_copy = self.level.copy()
        for x, y in interior:
            level_copy[x, y] = Elements.PLAYER_ON_GOAL.value if level_copy[x, y] == Elements.GOAL.value else Elements.PLAYER.value
        print(SokobanBoard(level=level_copy, player=self.player))
        
    def reward(self):
        reward = -min_cost_matching(self)
        if len(self.find_elements(Elements.BOX.value)) == 0:
            return Reward(reward, "WIN")
        if check_deadlock(self) or self.steps > self.max_steps:
            return Reward(reward, "LOSS")
        else:
            return Reward(reward, "STEP")