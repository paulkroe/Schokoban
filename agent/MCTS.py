import numpy as np
from graphviz import Digraph
from queue import Queue
import random
from copy import deepcopy

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import game.Sokoban as Sokoban

C_PUT = 16
D_PUT = 100

class Node():
    def __init__(self, parent, state, move):
        self.move = move
        self.state = state
        self.parent = parent
        self.children = {}
        self.q = 0
        self.n = 0
        self.reward = self.state.reward()
        self.max_value = self.reward
        self.sum_of_squares = self.reward.get_value()**2
        
    @property
    def u(self):
        if self.parent is None:
            return 0
        return C_PUT * np.sqrt(2*np.log(self.parent.n)) / (1 + self.n) + np.sqrt(self.sum_of_squares / (self.n + 1) - self.q**2 + D_PUT)
    
    @property
    def score(self):
        return self.q + self.u
    
    def update(self, value, max_value):
        self.q = (self.q * self.n + value) / (self.n + 1)
        self.n += 1
        self.sum_of_squares = self.sum_of_squares + value**2
        if self.max_value.get_value() < max_value.get_value():
            self.max_value = max_value
        if self.parent:
            self.parent.update(value, max_value)
            
    def expand_node(self, valid_moves, hashes):
        hashes_copy = deepcopy(hashes)
        for move in valid_moves:
            new_state = self.state.move(*move)
            if new_state.hash in hashes_copy:
                continue
            else:
                child_node = Node(state=new_state, parent=self, move=move)
                self.children[move] = child_node
                hashes_copy.append(new_state.hash)
                
        # important that this is not done in one loop
        for move in valid_moves:
            if move in self.children: # could be that child caused cycle and thus was not added
                if self.children[move].reward.get_type() == "LOSS":
                    assert self.children[move].should_remove()
                    self.children[move].remove()

    def select_child(self):
        if len(self.children) == 0:
            return None
        best_score = max(child.score for child in self.children.values())
        best_children = [child for child in self.children.values() if child.score == best_score]
        if len(best_children) == 0:
            print("best_score", best_score)
            print([child.score for child in self.children.values()])
            print("children", self.children)
            visualize(self)
            assert 0
        return random.choice(best_children) # break ties randomly

    def select_move(self):
        if len(self.children) == 0:
            return None
        else:
            best_value = max(child.max_value.get_value() for child in self.children.values())
            best_children = [child for child in self.children.values() if child.max_value.get_value() == best_value]
            return random.choice(best_children).move # break ties randomly
    
    def rollout(self, hashes):
        hashes_copy = deepcopy(hashes)
        state = self.state.copy()
        r = state.reward()
        while state.reward().get_type() == "STEP":
            state = state.move(*random.choice(state.valid_moves()))
            if state.hash in hashes_copy:
                break
            hashes_copy.append(state.hash)
            r = state.reward()
        return r
    
    def should_remove(self):
        if len(self.children) == 0 and not (self.reward.get_type() == "WIN"):
            return True
        
    def remove(self):
        assert len(self.children) == 0
        parent = self.parent
        if not parent is None:
            del parent.children[self.move]
            if parent.should_remove():
                parent.remove() 
        del self
    def __del__(self):
        pass
    
class MCTS():
    def __init__(self, sokobanboard):
        self.root = Node(parent=None, state=sokobanboard, move=None)
         
    def select_leaf(self, node, hashes):
        while len(node.children) != 0 and node.reward.get_type() == "STEP":
            node = node.select_child()
            if node is None:
                break
            hashes.append(node.state.hash)
        return node
    
    def expand(self, node, hashes):
        if node.reward.get_type() != "STEP":
            node.update(node.reward.get_value(), node.reward)   
        else:
            reward = node.rollout(hashes)
            node.update(reward.get_value(), reward)
            node.expand_node(node.state.valid_moves(), hashes)
                
    def run(self, simulations, visualize=False):
        
        for _ in range(simulations):
            hashes = [self.root.state.hash]
            node = self.select_leaf(self.root, hashes)
            if node is None:
                return None
            self.expand(node, hashes)
        if visualize:
            self.visualize()
            
        if self.root.max_value.get_type() == "WIN":
            moves = []
            node = self.root
            # if might be that after this loop node.state.reward().get_type() != "WIN" if the solution was discovered during rollout
            while len(node.children) != 0:
                move = node.select_move()
                moves.append(move)
                node = node.children[move]
        else:
            best_move = self.best_move
            if best_move is None:
                moves =  []
            else:
                moves = [self.best_move]
            
        return moves
    
    @property
    def best_move(self):
        return self.root.select_move()
    
    def visualize(self):
        visualize(self.root)
    
def visualize(node):
    dot = Digraph()
    q = Queue()
    
    q.put(node)
    
    while not q.empty():
        node = q.get()
        node_label = node.state.__repr__()+f"\nscore: {round(node.score, 3)},\n max_value: {node.max_value},\n n: {node.n},\n steps: {node.state.steps}\nreward: {node.reward}"
        shape = 'oval'
        color = 'black'
        if node.reward.get_type() == "WIN":
            node_label += f"\noutcome: {node.reward.get_type()}"
            shape = 'octagon'
            color = 'green'
        elif node.reward.get_type() == "LOSS":
            node_label += f",\noutcome: {node.reward.get_type()}"
            shape = 'rectangle'
            color = 'red'
        dot.node(str(node), label=node_label, shape=shape, color=color)
        
        for child in node.children.values():
            q.put(child)
            dot.edge(str(node), str(child), label=str(child.move))
    
    dot.render('mcts', format='pdf', cleanup=True)