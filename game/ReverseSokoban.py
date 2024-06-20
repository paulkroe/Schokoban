from enum import Enum
import numpy as np
from queue import Queue

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from game.GameElements import Elements, char_to_element, element_to_char

MAX_STEP = 1000

class ReverseSokobanBoard:

    def __init__(self, level_id, max_steps=MAX_STEP, folder=None):
        path = folder+"/level_"+str(level_id)+".txt"
        self.level = self.load_level(path)
        self.level_id = level_id
        self.folder = folder
        components = self.find_components()
        # set player in larges connected component and store other connected components
        self.player = components[0][0]
        self.level[self.player] = Elements.PLAYER.value if self.level[self.player] == Elements.FLOOR.value else Elements.PLAYER_ON_GOAL.value
        self.steps = 0
        self.max_steps = max_steps

        self.interior = sorted(self.find_interior(*self.player))
        self.box_positions = sorted(self.find_elements([Elements.BOX.value, Elements.BOX_ON_GOAL.value]))
        self.hash = self.get_hash()

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

        # reverse level:
        # turn goals into boxes and boxes into goals
        # remove player
        boxes = self.find_elements([Elements.BOX.value], level)   
        goals = self.find_elements([Elements.GOAL.value], level)
        for x, y in boxes:
            level[x, y] = Elements.GOAL.value
        for x, y in goals:
            level[x, y] = Elements.BOX.value

        player = self.find_elements([Elements.PLAYER.value, Elements.PLAYER_ON_GOAL.value], level)[0]
        level[player] = Elements.FLOOR.value if level[player] == Elements.PLAYER.value else Elements.BOX.value 
        return level

    # find connected components (goals and floor tiles)
    def find_components(self):
        assert len(self.find_elements([Elements.PLAYER.value, Elements.PLAYER_ON_GOAL.value])) == 0
        components = []
        visited = np.zeros(self.level.shape, dtype=bool)
        visited[self.level == Elements.WALL.value] = 1
        visited[self.level == Elements.BOX.value] = 1
        visited[self.level == Elements.BOX_ON_GOAL.value] = 1

        while not np.all(visited):
            start = np.where(visited == 0)
            start = (start[0][0], start[1][0])

            positions = Queue()
            positions.put(start)
            component = [start]

            while not positions.empty():
                x, y = positions.get()
                visited[x, y] = 1
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    new_x, new_y = x + dx, y + dy
                    if self.is_valid_move(new_x, new_y) and not visited[new_x, new_y]:
                        positions.put((new_x, new_y))
                        component.append((new_x, new_y))

            components.append(component)
        return sorted(components, key=lambda x: len(x), reverse=True) 

    def __repr__(self):
        return '\n'.join(''.join(element_to_char[int(elem)] for elem in row) for row in self.level)

    def find_elements(self, elements, board=None):
        if board is None:
            board = self.level
        if isinstance(elements, int):
            pos = np.where(board == elements)
        else:
            pos = np.where(np.isin(board, elements))

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
                player_x, player_y = box_x + dx, box_y + dy
                if (player_x, player_y) in interior:
                    valid_moves_.add(((player_x, player_y), (dx, dy)))

        valid_moves = set()
        for player_pos, d in valid_moves_:
            adj_x, adj_y = player_pos[0] + d[0], player_pos[1] + d[1]
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
        new_box_x, new_box_y = player_x, player_y
        assert new_level[new_box_x, new_box_y] in [Elements.PLAYER.value, Elements.PLAYER_ON_GOAL.value, Elements.FLOOR.value, Elements.GOAL.value]
        new_level[new_box_x, new_box_y] = Elements.BOX.value if new_level[new_box_x, new_box_y] in [Elements.FLOOR.value, Elements.PLAYER.value] else Elements.BOX_ON_GOAL.value

        # remove old box
        box_x, box_y = player_x - dx, player_y - dy
        assert new_level[box_x, box_y] in [Elements.BOX.value, Elements.BOX_ON_GOAL.value]
        new_level[box_x, box_y] = Elements.FLOOR.value if new_level[box_x, box_y] == Elements.BOX.value else Elements.GOAL.value

        # move player
        new_player_x, new_player_y = player_x + dx, player_y + dy
        assert new_level[new_player_x, new_player_y] in [Elements.FLOOR.value, Elements.GOAL.value]
        new_level[new_player_x, new_player_y] = Elements.PLAYER.value if new_level[new_player_x, new_player_y] == Elements.FLOOR.value else Elements.PLAYER_ON_GOAL.value

        new_board = self.construct(new_level, (new_player_x, new_player_y), self.steps + 1)

        NEW_NUM_BOXES = len(new_board.find_elements([Elements.BOX.value, Elements.BOX_ON_GOAL.value]))
        NEW_NUM_GOALS = len(new_board.find_elements([Elements.GOAL.value, Elements.BOX_ON_GOAL.value, Elements.PLAYER_ON_GOAL.value]))
        if NUM_BOXES != NEW_NUM_BOXES or NUM_GOALS != NEW_NUM_GOALS:
            print(self)
            print(new_board)
        assert NUM_BOXES == NEW_NUM_BOXES
        assert NUM_GOALS == NEW_NUM_GOALS
        assert len(new_board.find_elements([Elements.PLAYER.value, Elements.PLAYER_ON_GOAL.value])) == 1
        return new_board

    def construct(self, level, player, steps):
        new_board = ReverseSokobanBoard(level_id=self.level_id, max_steps=self.max_steps, folder=self.folder)
        new_board.level = level
        new_board.player = player
        new_board.steps = steps

        new_board.interior = sorted(new_board.find_interior(*new_board.player))
        new_board.box_positions = sorted(new_board.find_elements([Elements.BOX.value, Elements.BOX_ON_GOAL.value]))
        new_board.hash = new_board.get_hash()


        return new_board

    def copy(self):
        return self.construct(level=self.level.copy(), player=self.player, steps=self.steps)