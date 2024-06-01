import numpy as np
import sys
import os
from tqdm import tqdm
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import game.Sokoban as Sokoban
import agent.MCTS as MCTS

LEVEL_ID = 3

board = Sokoban.SokobanBoard(level_id=LEVEL_ID)
print(board)
for i in range(100):
    tree = MCTS.MCTS(board)
    move = tree.run(6000, visualize=False)
    if move is None:
        break
    board = board.move(*move)
    if board.is_terminal() == Sokoban.REWARD_WIN:
        print("==========")
        print(board)
        print("WIN")        
        break
    if board.is_terminal() == Sokoban.REWARD_LOSS:
        print("==========")
        print(board)
        print("LOSS")
        break
    print("==========")
    print(board)
    