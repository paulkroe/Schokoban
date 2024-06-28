# Schokoban

## Introduction

This repository contains a Sokoban solver called Schokoban developed as part of my Bachelor thesis at ETH Zurich. The solver utilizes single-player Monte Carlo tree search (MCTS). It's important to note that while state-of-the-art Sokoban solvers typically employ different algorithms, this project explores the adaptation of the MCTS algorithm to Sokoban. A notable advancement in this solver is its method for managing redundant states in the Monte Carlo Tree Search, which substantially improves performance over traditional approaches.

## Project Objective

The primary aim of this thesis was not to develop the most performant Sokoban Solver but to explore the effectiveness of the MCTS algorithm within the context of Sokoban. The research focused on identifying and refining strategies that best adapt MCTS to the challenges presented by Sokoban puzzles.

Despite the experimental focus on MCTS, maintaining the solver's practical usability was essential. Thus, a significant goal was to ensure the solver's capability to successfully handle most levels in David W. Skinner's renowned [Microban III level collection](http://www.abelmartin.com/rj/sokobanJS/Skinner/David%20W.%20Skinner%20-%20Sokoban.htm).

However, the development process also required testing the algorithm's performance on less complex puzzles. For this purpose, simpler levels available [here](https://www.cbc.ca/kids/games/play/sokoban) were utilized.

## Installation and Setup
Follow these steps to install and set up the solver:
#### Clone Repository 
```
git clone https://github.com/paulkroe/SokobanSolver.git
```
#### Set up Environment
Move to the SokobanSolver directory and set up a virtual environment.
For Linux and MacOS:
```
cd SokobanSolver
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```
For Windows:
```
cd SokobanSolver
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
```
#### Usage
Now from within the SokobanSolver folder the solver can be used. For example:
```
python3 demo.py --folder=Microban/ --level_id=1 --mode=schoko --num_iters=1000 --verbose=3
```
Other examples can be found below.

#### Deactivate
Afterwards the environment can be deactivated using:
```
deactivate
```
## Usage
For testing the solver on a single level useing demo.py is most convenient. 
demo.py takes the following arguments:
- `--folder`: the folder containing the levels, e.g. `Microban/`, `Testsuite/`, or `CustomLevels/`
- `--level_id`: the index of the level in the folder
- `--num_iters`: the number of iterations of the MCTS
- `--mode`: the mode of the solver, either `schoko` or `vanilla`, generally `schoko` performs better
- `--verbose`: the verbosity of the output, 0 for no output, 3 for detailed output
- `--seed`: fix the random seed for reproducibility

For solving the first level in the Mircoban III collection one might use:
```
python3 demo.py --folder=Microban/ --level_id=1 --mode=schoko --num_iters=1000 --verbose=3
```
For testing the solver on a whole level collection use experiments.py.
experiments.py takes the same arguments as demo.py.
For testing the solver on the Microban III collection one might use:
```
python3 experiments/experiments.py --folder=Microban/ --num_iters=1000 --mode=schoko --verbose=0 --seed=42
```
## Run Schokoban on custom levels
The algorithms in this thesis can be tested on any Sokoban level. The easiest way to do so is to create a new level file in the CustomLevels folder. The level file should be a text file the following format:
```
    #####
    #   #
    #$  #
  ###  $##
  #  $ $ #
### # ## ##  ######
#   # ## #####  ..#
# $  $          ..#
##### ### #@##  ..#
    #     #########
    #######
```
The level file should only contain the following characters:
- `#` for walls
- `.` for targets
- `@` for the player
- `$` for boxes
- ` ` for empty spaces
- `*` for boxes on targets
- `+` for player on target

The level file should be saved in the CustomLevels folder as level_1.txt. The level can then be run by running the following command:
```
python3 demo.py --folder=CustomLevels/ --level_id=1 --mode=schoko --num_iters=10000 --verbose=3
```
For solving more involved levels it might be necessary to increase the number of iterations or the maximum number of steps.

## Results

| Number of Iterations | 25 | 50 | 100 | 1000 | 2000 | 5000 | 10000 | 100000 |
|----------------------|----|----|-----|------|------|------|-------|--------|
| Vanilla MCTS         | 4  | 5  | 6   | 7    | 5    | 6    | 17    | 50     |
| Schokoban            | 6  | 20 | 41  | 60   | 60   | 60   | 60    | 60     |

The table above shows the number of levels solved by the vanilla MCTS and Schokoban solvers for different numbers of iterations. The results are based on the 60 levels in the Testsuite.