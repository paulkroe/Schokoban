import sys
import os
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import agent.sokoban_solver as sokoban_solver
import argparse

random.seed(0)

parser = argparse.ArgumentParser(description='Sokoban Solver')
parser.add_argument('--num_sims', default=1600, type=int, help='Number of simulations in the MCTS')
parser.add_argument('--max_steps', type=int, default=100, help='Maximum number of steps to solve the level')
parser.add_argument('--verbose', type=int, default=0, help='0 for no output, 1 for output')
parser.add_argument('--mode', type=str, default="afterstates", help='afterstates for using afterstates, vanilla for not using afterstates')
args = parser.parse_args()

folder_path = 'Testsuite/'
files = os.listdir(folder_path)
level_files = [file for file in files if file.startswith('level')]
NUM_LEVELS = len(level_files)

outcomes = [None for _ in range(NUM_LEVELS)]

for level_id in range(NUM_LEVELS):
    solver = sokoban_solver.Solver()
    outcome = solver.solve(level_id+1, folder_path, args.num_sims, args.max_steps, args.verbose, args.mode)
    print("                                                            ", end="\r")
    print(f"Level {level_id+1}: {outcome}.")
    outcomes[level_id] = 1 if outcome == "WIN" else 0

print(f"Soleved {sum(outcomes)} out of {NUM_LEVELS} levels.")
'''
python3 Testsuite/solve_levels.py --num_sim=5000 --max_steps=50 --verbose=0
python3 Testsuite/solve_levels.py --num_sim=5000 --max_steps=50 --verbose=0 
'''