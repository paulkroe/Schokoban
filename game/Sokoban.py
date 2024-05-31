from enum import Enum
import numpy as np
from queue import Queue

REWARD_WIN = 1
REWARD_STEP = 0
REWARD_LOSS = -1

MAX_STEP = 50

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

class SokobanBoard:
    
    def __init__(self, level_id=None, level=None, player=None, steps=None):
        if not level_id is None:
            self.level = self.load_level(level_id)
            self.player = self.find_elements([Elements.PLAYER.value, Elements.PLAYER_ON_GOAL.value])[0]
            self.steps = 0
        else:
            assert not level is None
            assert not player is None
            assert not steps is None
            self.level = level
            self.player = player
            self.steps = steps
            
        # TODO: make interior search more efficient
        self.interior = sorted(self.find_interior(*self.player))
        self.box_positions = sorted(self.find_elements([Elements.BOX.value, Elements.BOX_ON_GOAL.value]))
        self.hash = self.get_hash()
    
    def get_hash(self):
        return str(self.interior) + str(self.box_positions)
    
    def load_level(self, level_id):
        with open(f'levels/level_{level_id}.txt') as f:
            lines = f.readlines()
            height = len(lines)
            width = max(len(line) for line in lines) - 1 # remove newline
            level = np.ones((height, width), dtype=int)*Elements.WALL.value
            for i, line in enumerate(lines):
                for j, char in enumerate(line.replace('\n', '')):
                    level[i, j] = char_to_element[char].value
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
        
        new_board = SokobanBoard(level=new_level, player=(new_player_x, new_player_y), steps=self.steps+1)
        NEW_NUM_BOXES = len(new_board.find_elements([Elements.BOX.value, Elements.BOX_ON_GOAL.value]))
        NEW_NUM_GOALS = len(new_board.find_elements([Elements.GOAL.value, Elements.BOX_ON_GOAL.value, Elements.PLAYER_ON_GOAL.value]))
        assert NUM_BOXES == NEW_NUM_BOXES
        assert NUM_GOALS == NEW_NUM_GOALS
        assert len(new_board.find_elements([Elements.PLAYER.value, Elements.PLAYER_ON_GOAL.value])) == 1
        return new_board
    
    def copy(self):
        return SokobanBoard(level=self.level.copy(), player=self.player, steps=self.steps)
    
    def mark(self):
        interior = self.find_interior(*self.player)
        level_copy = self.level.copy()
        for x, y in interior:
            level_copy[x, y] = Elements.PLAYER_ON_GOAL.value if level_copy[x, y] == Elements.GOAL.value else Elements.PLAYER.value
        print(SokobanBoard(level=level_copy, player=self.player))
        
    def is_terminal(self):
        if len(self.find_elements(Elements.BOX.value)) == 0:
            return REWARD_WIN
        if self.check_deadlock():
            return REWARD_LOSS
        if len(self.valid_moves()) == 0:
            return REWARD_LOSS
        elif self.steps <= MAX_STEP:
            return REWARD_STEP
        else:
            return REWARD_LOSS
        
    def check_deadlock(self):
        if len(self.valid_moves()) == 0:
            return True
        boxes = self.find_elements([Elements.BOX.value, Elements.BOX_ON_GOAL.value])
        for box in boxes:
            if self.is_deadlocked(box):
                return True
        
        # TODO: add kernels that check for deadlocks
        return False
    
    def is_deadlocked(self, box):
        # if box is on goal deadlock does not matter
        if self.level[box] == Elements.BOX_ON_GOAL.value:
            return False
        
        for d1, d2 in zip([(0, 1), (1, 0), (0, -1), (-1, 0)], [(1, 0), (0, -1), (-1, 0), (0, 1)]):
            box_d1 = (box[0]+d1[0], box[1]+d1[1])
            box_d2 = (box[0]+d2[0], box[1]+d2[1])
            
            obs1 = self.level[box_d1]
            obs2 = self.level[box_d2]
            
            # box is surrounded by walls
            if obs1 == Elements.WALL.value and obs2 == Elements.WALL.value:
                return True

            

        return False
            

if __name__ == '__main__':
    game = SokobanBoard(0)
    while(True):
        print(game)
        print(game.valid_moves())
        input_ = input()
        input_ = list(map(int, input_.split()))
        print(input_)
        game = game.move(*input_)