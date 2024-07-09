import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from deadlock_detection.detect_deadlocks import check_deadlock
import game.Sokoban as Sokoban
import argparse

parser = argparse.ArgumentParser(description='Sokoban Solver', allow_abbrev=False)
parser.add_argument('--level_id', type=int, required=True, help='Level ID')
parser.add_argument('--folder', type=str, default="Microban/", help='foldername')
parser.add_argument('--num_iters', type=int, default=100000, help='Number of simulations in the MCTS')
parser.add_argument('--verbose', type=int, default=1, help='0 for no output, value between 0 and 3')
args = parser.parse_args()

board = Sokoban.SokobanBoard(level_id=args.level_id, folder=args.folder)
visited = set()
queue = [(board, [])]
num_iters = 0
num_states = 1
win=False
while queue and num_iters < args.num_iters and not win:
    current_board, current_path = queue.pop(0)
    for action in current_board.valid_moves():
        new_board = current_board.move(*action)
        if new_board not in visited:
            visited.add(new_board)
        if new_board.reward().get_type() == "WIN":
            if args.verbose==3:
                print("\n")
                board = Sokoban.SokobanBoard(level_id=args.level_id, folder=args.folder)
                print(board)
                for action in current_path + [action]:
                    board = board.move(*action)
                    print(board)
            print("WIN")
            win=True
            break
            
        if not check_deadlock(new_board):
            queue.append((new_board, current_path + [action]))
                
    if args.verbose>=2:
        print(f"Iteration: {num_iters}, number of states: {len(visited)}", end="\r")
    num_iters += 1