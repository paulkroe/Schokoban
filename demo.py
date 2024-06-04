import numpy as np
import sys
import os
from tqdm import tqdm
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import game.Sokoban as Sokoban
import agent.MCTS as MCTS

LEVEL_ID = 4

board = Sokoban.SokobanBoard(level_id=LEVEL_ID)
print(board)
for i in range(100):
    tree = MCTS.MCTS(board)
    move = tree.run(10, visualize=True)
    if move is None:
        break
    board = board.move(*move)
    if board.reward().get_type() != "STEP":  
        print("==========")
        print(board)
        print(board.reward().get_type())        
        break
    print("==========")
    print(board)
    