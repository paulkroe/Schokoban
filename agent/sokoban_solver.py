import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import game.Sokoban as Sokoban
from deadlock_detection.precompute_deadlocks import compute_deadlocks
from utils.est_search_space import count_boxes, calculate_tiles
from scipy.special import comb

class Solver():
    def __init__(self):
        pass
    
    def print(self, string, verbose):
        if verbose >= 3:
            print(string)            
    
    def solve(self, level_id, folder, num_iters, verbose=0, mode="schoko"):
        if mode == "schoko":
            import agent.MCTS as MCTS
        else:
            import agent.MCTS_vanilla as MCTS
        
        file_path = "deadlock_detection/"+folder+"level_"+str(level_id)+".npy"
        
        if not os.path.isfile(file_path) or not (folder in ["Microban/", "Testsuite/"]):
            compute_deadlocks(level_id, folder, verbose=0)
            

        if verbose >= 2:
            path = folder + f"level_{level_id}.txt"
            n, b = count_boxes(path)
            path = f"deadlock_detection/" + folder + f"level_{level_id}.npy"
            p = calculate_tiles(path)
            print("Estimated Search Space Size: ", int(comb(p, b)*(n-b)))
            
        self.print("Solving Sokoban", verbose)
        
        board = Sokoban.SokobanBoard(level_id=level_id, folder=folder)
    
        self.print(board, verbose)
        tree = MCTS.MCTS(board)
        moves = tree.run(num_iters, verbose=verbose)
        if not moves is None:
            for move in moves:
                board = board.move(*move)
                if board.reward().get_type() != "STEP":  
                    self.print("==========", verbose)
                    self.print(board, verbose)
                    self.print(board.reward().get_type(), verbose)
                    outcome = board.reward().get_type()
                    if outcome == "WIN":
                        assert len(board.find_elements(Sokoban.Elements.BOX.value)) == 0       
                    return board.reward().get_type()
                self.print("==========", verbose)
                self.print(board, verbose)
            
        return "LOSS"