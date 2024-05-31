import numpy as np
from graphviz import Digraph
from queue import Queue
import random

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import game.Sokoban as Sokoban
import agent.MCTS as MCTS

LEVEL_ID = 0
board = Sokoban.SokobanBoard(level_id=LEVEL_ID)
print(board)
for i in range(100):
    tree = MCTS.MCTS(board)
    move = tree.run(2500, visualize=False)
    if move is None:
        print("LOSS")
        break
    board = board.move(*move)
    print("---")
    print(board)
    if board.is_terminal() == Sokoban.REWARD_WIN:
        print("WIN")
        break
    if board.is_terminal() == Sokoban.REWARD_LOSS:
        print("LOSS")
        break