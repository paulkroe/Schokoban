import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import agent.MCTS as MCTS
import game.Sokoban as Sokoban

class Solver():
    def __init__(self):
        pass
    
    def print(self, string, verbose):
        if verbose == 1:
            print(string)            
    
    def solve(self, level_id, num_sims, max_steps, verbose=0):
        board = Sokoban.SokobanBoard(level_id=level_id, max_steps=max_steps)
        self.print(board, verbose)
        for _ in range(max_steps):
            tree = MCTS.MCTS(board)
            moves = tree.run(num_sims, visualize=False)
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