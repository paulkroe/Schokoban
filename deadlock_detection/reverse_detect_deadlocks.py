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
    
    # TODO: add kernels that check for deadlocks
    return False

# checks if a box is in one of the precomputed deadlocks
def precomputed_deadlock(board):
    for box in board.find_elements([Elements.BOX.value]):
        if board.deadlocks[box[0], box[1]] == 0:
            return True
    return False

# checks if a box is pushed against a wall without a goal
# 4 sweeplines that check for boxes and goals from every direction
# returns true if a wall deadlock is detected
def wall_deadlock(board):
    for top in board.level:
        if not np.all(top == 0):
            num_boxes = np.count_nonzero((top == Elements.BOX.value))
            num_goals = np.count_nonzero((top == Elements.GOAL.value) | (top == Elements.PLAYER_ON_GOAL.value))
            if num_boxes < num_goals:
                return True
            break
    
    for bot in board.level[::-1]:
        if not np.all(bot == 0):
            num_boxes = np.count_nonzero((bot == Elements.BOX.value))
            num_goals = np.count_nonzero((bot == Elements.GOAL.value) | (bot == Elements.PLAYER_ON_GOAL.value))
            if num_boxes < num_goals:
                return True
            break
        
    for left in board.level.T:
        if not np.all(left == 0):
            num_boxes = np.count_nonzero((left == Elements.BOX.value))
            num_goals = np.count_nonzero((left == Elements.GOAL.value) | (left == Elements.PLAYER_ON_GOAL.value))
            if num_boxes < num_goals:
                return True
            break       

    for right in board.level.T[::-1]:
        if not np.all(right == 0):
            num_boxes = np.count_nonzero((right == Elements.BOX.value))
            num_goals = np.count_nonzero((right == Elements.GOAL.value) | (right == Elements.PLAYER_ON_GOAL.value))
            if num_boxes < num_goals:
                return True
            break
    
    return False