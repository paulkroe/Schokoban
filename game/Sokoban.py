from enum import Enum
import numpy as np
from queue import Queue

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

element_to_char = {0: '#',
                    1: ' ',
                    2: '@',
                    3: '$',
                    4: '.',
                    5: '*',
                    6: '+'}

class SokobanBoard:
    
    def __init__(self, level_id=None, level=None, player=None):
        if not level_id is None:
            self.level = self.load_level(level_id)
            self.player = self.find_elements([Elements.PLAYER.value, Elements.PLAYER_ON_GOAL.value])[0]
        else:
            assert not level is None
            assert not player is None
            self.level = level
            self.player = player
        
    def load_level(self, level_id):
        with open(f'levels/{level_id}.txt') as f:
            lines = f.readlines()
            height = len(lines)
            width = max(len(line) for line in lines)
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
        interior = []
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
                valid_moves.add((player_pos, d, box_pos))
       
        return valid_moves

    def move(self, player_x, player_y, dx, dy):
        assert (self.level[player_x+dx, player_y+dy] in [Elements.BOX.value, Elements.BOX_ON_GOAL.value])
        
        new_level = self.level.copy()
        new_level[self.player] = Elements.FLOOR.value if self.level[self.player] == Elements.PLAYER.value else Elements.GOAL.value
       
        box_x, box_y = player_x + dx, player_y + dy
        new_level[box_x, box_y] = Elements.PLAYER.value if self.level[box_x, box_y] == Elements.BOX.value else Elements.PLAYER_ON_GOAL.value
        
        new_box_x, new_box_y = box_x + dx, box_y + dy
        new_level[new_box_x, new_box_y] = Elements.BOX.value if self.level[new_box_x, new_box_y] == Elements.FLOOR.value else Elements.BOX_ON_GOAL.value
        
        return SokobanBoard(level=new_level, player=(box_x, box_y))
    
    def mark(self):
        interior = self.find_interior(*self.player)
        level_copy = self.level.copy()
        for x, y in interior:
            level_copy[x, y] = Elements.PLAYER_ON_GOAL.value if level_copy[x, y] == Elements.GOAL.value else Elements.PLAYER.value
        print(SokobanBoard(level=level_copy, player=self.player))
          
game = SokobanBoard('level_1')
while(True):
    print(game)
    print(game.valid_moves())
    input_ = input()
    input_ = list(map(int, input_.split()))
    print(input_)
    game = game.move(*input_)