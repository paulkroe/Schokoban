import sys
import os
import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from game.GameElements import Elements

def check_deadlock(board):
    if len(board.valid_moves()) == 0:
        return True
    
    if precomputed_deadlock(board):
        return True
     
    if locked(board):
        return True
    
    if wall_deadlock(board):
        return True
       
    # TODO: add kernels that check for deadlocks
    return False

# checks if a box is in one of the precomputed deadlocks
def precomputed_deadlock(board):
    for box in board.find_elements([Elements.BOX.value]):
        if board.deadlocks[box[0], box[1]] == 0:
            return True
    return False

class Box():
    def __init__(self, position):
        self.position = position
        self.vertical_checks = [0, 0]
        self.horizontal_checks = [0, 0]
        self.vertical_visited = False
        self.horizontal_visited = False
    
    @property
    def vertical_lock(self):
        return bool(sum(self.vertical_checks))
    
    @property
    def horizontal_lock(self):
        return bool(sum(self.horizontal_checks))
    
    def __repr__(self):
        return f"Box at {self.position}, vertical: {self.vertical_checks}, horizontal: {self.horizontal_checks}"
    
class Boxes():
    def __init__(self, box_dict, goal_list):
        self.box_dict = box_dict
        self.goal_list = goal_list
        
    def simple_checks(self, board):
        for box in self.box_dict.values():
            self.simple_vertical_lock(box, board)
            self.simple_horizontal_lock(box, board)
            
    def recursive_checks(self, board):
        for box in self.box_dict.values():
            # vertical checks
            if not box.vertical_lock:
                # box above
                if board.level[box.position[0]-1, box.position[1]] in [Elements.BOX.value, Elements.BOX_ON_GOAL.value]:
                    if self.box_dict[(box.position[0]-1, box.position[1])].horizontal_lock:
                        box.vertical_checks[1] = 1
                    elif self.recursive_horizontal_lock(self.box_dict[(box.position[0]-1, box.position[1])], board, [box.position]):
                        box.vertical_checks[1] = 1
            
            if not box.vertical_lock:
                # box below
                if board.level[box.position[0]+1, box.position[1]] in [Elements.BOX.value, Elements.BOX_ON_GOAL.value]:
                    if self.box_dict[(box.position[0]+1, box.position[1])].horizontal_lock:
                        box.vertical_checks[1] = 1
                    elif self.recursive_horizontal_lock(self.box_dict[(box.position[0]+1, box.position[1])], board, [box.position]):
                        box.vertical_checks[1] = 1 
            
            # horizontal checks 
            if not box.horizontal_lock:
                # box left
                if board.level[box.position[0], box.position[1]-1] in [Elements.BOX.value, Elements.BOX_ON_GOAL.value]:
                    if self.box_dict[(box.position[0], box.position[1]-1)].vertical_lock:
                        box.horizontal_checks[1] = 1
                    elif self.recursive_vertical_lock(self.box_dict[(box.position[0], box.position[1]-1)], board, [box.position]):
                        box.horizontal_checks[1] = 1

                # box right
                if board.level[box.position[0], box.position[1]+1] in [Elements.BOX.value, Elements.BOX_ON_GOAL.value]:
                    if self.box_dict[(box.position[0], box.position[1]+1)].vertical_lock:
                        box.horizontal_checks[1] = 1
                    elif self.recursive_vertical_lock(self.box_dict[(box.position[0], box.position[1]+1)], board, [box.position]):
                        box.horizontal_checks[1] = 1
                
    def deadlocked(self):
        for box in self.box_dict.values():
            if box.vertical_lock and box.horizontal_lock:
                if box.position not in self.goal_list:
                    return True
        return False
    
    def simple_vertical_lock(self, box, board):
        if board.level[box.position[0]-1, box.position[1]] == Elements.WALL.value or board.level[box.position[0]+1, box.position[1]] == Elements.WALL.value:
            box.vertical_checks[0] = 1

        if board.deadlocks[box.position[0]-1, box.position[1]] == 0 and board.deadlocks[box.position[0]+1, box.position[1]] == 0:
            box.vertical_checks[0] = 1

    def simple_horizontal_lock(self, box, board):
        if board.level[box.position[0], box.position[1]-1] == Elements.WALL.value or board.level[box.position[0], box.position[1]+1] == Elements.WALL.value:
            box.horizontal_checks[0] = 1

        if board.deadlocks[box.position[0], box.position[1]-1] == 0 and board.deadlocks[box.position[0], box.position[1]+1] == 0:
            box.horizontal_checks[0] = 1
            
    def recursive_vertical_lock(self, box, board, path):
        if box.vertical_lock:
            return True
        # box above
        if board.level[box.position[0]-1, box.position[1]] in [Elements.BOX.value, Elements.BOX_ON_GOAL.value]:
            #check if box is in path
            if (box.position[0]-1, box.position[1]) in path:
                return True
            if self.recursive_horizontal_lock(self.box_dict[(box.position[0]-1, box.position[1])], board, path + [box.position]):
                return True
        # box below
        if board.level[box.position[0]+1, box.position[1]] in [Elements.BOX.value, Elements.BOX_ON_GOAL.value]:
            #check if box is in path
            if (box.position[0]+1, box.position[1]) in path:
                return True
            if self.recursive_horizontal_lock(self.box_dict[(box.position[0]+1, box.position[1])], board, path + [box.position]):
                return True
        
        return False

    def recursive_horizontal_lock(self, box, board, path):
        if box.horizontal_lock:
            return True
        # box left
        if board.level[box.position[0], box.position[1]-1] in [Elements.BOX.value, Elements.BOX_ON_GOAL.value]:
            #check if box is in path
            if (box.position[0], box.position[1]-1) in path:
                return True
            if self.recursive_vertical_lock(self.box_dict[box.position[0], box.position[1]-1], board, path + [box.position]):
                return True
        # box right        
        if board.level[box.position[0], box.position[1]+1] in [Elements.BOX.value, Elements.BOX_ON_GOAL.value]:
            #check if box is in path
            if (box.position[0], box.position[1]+1) in path:
                return True
            if self.recursive_vertical_lock(self.box_dict[box.position[0], box.position[1]+1], board, path + [box.position]):
                return True
            
        return False 
    
def locked(board):
    boxes = board.find_elements([Elements.BOX.value, Elements.BOX_ON_GOAL.value])
    boxes = {box: Box(box) for box in boxes}
    goals = board.find_elements([Elements.GOAL.value, Elements.BOX_ON_GOAL.value, Elements.PLAYER_ON_GOAL.value])
    boxes = Boxes(boxes, goals)
    boxes.simple_checks(board)
    boxes.recursive_checks(board)
    return boxes.deadlocked()
 
# checks if a box is pushed against a wall without a goal
# 4 sweeplines that check for boxes and goals from every direction
# returns true if a wall deadlock is detected
def wall_deadlock(board):
    for top in board.level:
        if not np.all(top == 0):
            num_boxes = np.count_nonzero((top == Elements.BOX.value))
            num_goals = np.count_nonzero((top == Elements.GOAL.value) | (top == Elements.PLAYER_ON_GOAL.value))
            if num_boxes > num_goals:
                return True
            break
    
    for bot in board.level[::-1]:
        if not np.all(bot == 0):
            num_boxes = np.count_nonzero((bot == Elements.BOX.value))
            num_goals = np.count_nonzero((bot == Elements.GOAL.value) | (bot == Elements.PLAYER_ON_GOAL.value))
            if num_boxes > num_goals:
                return True
            break
        
    for left in board.level.T:
        if not np.all(left == 0):
            num_boxes = np.count_nonzero((left == Elements.BOX.value))
            num_goals = np.count_nonzero((left == Elements.GOAL.value) | (left == Elements.PLAYER_ON_GOAL.value))
            if num_boxes > num_goals:
                return True
            break       

    for right in board.level.T[::-1]:
        if not np.all(right == 0):
            num_boxes = np.count_nonzero((right == Elements.BOX.value))
            num_goals = np.count_nonzero((right == Elements.GOAL.value) | (right == Elements.PLAYER_ON_GOAL.value))
            if num_boxes > num_goals:
                return True
            break
    
    return False