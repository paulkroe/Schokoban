import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import game.Sokoban as Sokoban
import agent.MCTS as MCTS

tree = MCTS.MCTS(level_id=0)
move = tree.run(10)
print(move)