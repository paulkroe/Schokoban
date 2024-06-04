# computes the minimum cost matching of the board. distances are computed using the manhattan distance between boxes and goals.
import numpy as np
import sys
import os
from scipy.optimize import linear_sum_assignment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.GameElements import Elements

def min_cost_matching(board):
    boxes = board.find_elements([Elements.BOX.value])
    goals = board.find_elements([Elements.GOAL.value, Elements.PLAYER_ON_GOAL.value])
    assert len(boxes) == len(goals)
    n = len(boxes)
    if n == 0:
        return 0
    dist_matrix = np.zeros((n, n))
    for i, box in enumerate(boxes):
        for j, goal in enumerate(goals):
            dist_matrix[i, j] = manhattan_distance(*box, *goal)
    row_ind, col_ind = linear_sum_assignment(dist_matrix)
    dist = dist_matrix[row_ind, col_ind].sum()
    return dist
    
def manhattan_distance(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)