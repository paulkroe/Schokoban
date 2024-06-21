import sys
import os
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import agent.sokoban_solver as sokoban_solver
import argparse
import csv
from tqdm import tqdm

parser = argparse.ArgumentParser(description='Sokoban Solver')
parser.add_argument('--num_iters', default=1000, type=int, help='Number of simulations in the MCTS')
parser.add_argument('--folder', type=str, default="Microban/", help='foldername')
parser.add_argument('--max_steps', type=int, default=100, help='Maximum number of steps to solve the level')
parser.add_argument('--verbose', type=int, default=0, help='0 for no output, number between 0 and 3')
parser.add_argument('--mode', type=str, default="afterstates", help='afterstates for using afterstates, vanilla for not using afterstates')
parser.add_argument('--seed', type=int, default=None, help='Random Seed')
args = parser.parse_args()

if args.seed:
    random.seed(args.seed)

files = os.listdir(args.folder)
level_files = [file for file in files if file.startswith('level')]
NUM_LEVELS = len(level_files)

outcomes = [None for _ in range(NUM_LEVELS)]

for level_id in tqdm(range(NUM_LEVELS)):
    solver = sokoban_solver.Solver()
    outcome = solver.solve(level_id+1, args.folder, args.num_iters, args.max_steps, args.verbose, args.mode)
    outcomes[level_id] = 1 if outcome == "WIN" else 0
print(f"Soleved {sum(outcomes)} out of {NUM_LEVELS} levels with {args.num_iters} Simulations.")