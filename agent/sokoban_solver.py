import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import agent.MCTS as MCTS
import game.Sokoban as Sokoban
import game.ReverseSokoban as ReverseSokoban

class Solver():
    def __init__(self):
        pass
    
    def print(self, string, verbose):
        if verbose == 1:
            print(string)            
    
    def solve(self, level_id, pre, rev, num_sims, max_steps, verbose=0):
        if not rev:
            self.print("Solving Sokoban", verbose)
            board = Sokoban.SokobanBoard(level_id=level_id, pre=pre, max_steps=max_steps)
            start_positions = [board.player]
        else:
            self.print("Solving Reverse Sokoban", verbose)
            board = ReverseSokoban.ReverseSokobanBoard(level_id=level_id, pre=pre, max_steps=max_steps)
            # remove player for calculating components 
            board.level[board.player] = Sokoban.Elements.FLOOR.value if board.level[board.player] == Sokoban.Elements.PLAYER.value else Sokoban.Elements.PLAYER_ON_GOAL.value
            components = board.find_components()
            start_positions = [comp[0] for comp in components]
            # add player
            board.player = start_positions[0]
            board.level[board.player] = Sokoban.Elements.PLAYER.value if board.level[board.player] == Sokoban.Elements.FLOOR.value else Sokoban.Elements.PLAYER_ON_GOAL.value
            
        for start_position in start_positions:
            # remove player
            board.level[board.player] = Sokoban.Elements.FLOOR.value if board.level[board.player] == Sokoban.Elements.PLAYER.value else Sokoban.Elements.PLAYER_ON_GOAL.value
            # add player
            board.player = start_position
            board.level[board.player] = Sokoban.Elements.PLAYER.value if board.level[board.player] == Sokoban.Elements.FLOOR.value else Sokoban.Elements.PLAYER_ON_GOAL.value
            
            
            self.print(board, verbose)
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