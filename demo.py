import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import agent.sokoban_solver as sokoban_solver
import argparse
import random
random.seed(0)

parser = argparse.ArgumentParser(description='Sokoban Solver')
parser.add_argument('--level_id', type=int, help='Level ID')
parser.add_argument('--pre', type=str, default=None, help='prefix filename')
parser.add_argument('--num_sims', default=1600, type=int, help='Number of simulations in the MCTS')
parser.add_argument('--max_steps', type=int, default=100, help='Maximum number of steps to solve the level')
parser.add_argument('--verbose', type=int, default=1, help='0 for no output, 1 for output')
args = parser.parse_args()

solver = sokoban_solver.Solver()
solver.solve(args.level_id, args.pre, args.num_sims, args.max_steps, args.verbose)
    