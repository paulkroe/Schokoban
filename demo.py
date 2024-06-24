import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import agent.sokoban_solver as sokoban_solver
import argparse
import random

random.seed(0)

parser = argparse.ArgumentParser(description='Sokoban Solver', allow_abbrev=False)
parser.add_argument('--level_id', type=int, required=True, help='Level ID')
parser.add_argument('--folder', type=str, default="Microban/", help='foldername')
parser.add_argument('--num_iters', type=int, default=100000, help='Number of simulations in the MCTS')
parser.add_argument('--max_steps', type=int, default=100, help='Maximum number of steps to solve the level')
parser.add_argument('--verbose', type=int, default=1, help='0 for no output, value between 0 and 3')
parser.add_argument('--mode', type=str, default="schoko", help='schoko for using schokoban, vanilla for using vanilla mcts')
parser.add_argument('--seed', type=int, default=None, help='Random Seed')
args = parser.parse_args()

if args.seed:
    random.seed(args.seed)

solver = sokoban_solver.Solver()
outcome = solver.solve(args.level_id, args.folder, args.num_iters, args.max_steps, args.verbose, args.mode)
if args.verbose in [0,1]:
    print("                                                                            ", end="\r")
    print(outcome)