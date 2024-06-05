import sys
import os
import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from game.GameElements import Elements

def check_deadlock(board):
    if len(board.valid_moves()) == 0:
        return True
    
    # TODO: add kernels that check for deadlocks
    return False