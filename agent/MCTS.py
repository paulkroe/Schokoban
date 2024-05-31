import numpy as np
from graphviz import Digraph
from queue import Queue
import random

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import game.Sokoban as Sokoban

C_PUT = 1.5

class Node():
    def __init__(self, parent, state, move):
        self.move = move
        self.state = state
        self.parent = parent
        self.children = []
        self.q = 0
        self.n = 0
        self.is_terminal = self.state.is_terminal() # 100 for win, -1 for ongogin and -100 for loss
        self.max_value = self.is_terminal
        
    @property
    def u(self):
        if self.parent is None:
            return 0
        return C_PUT * np.sqrt(2*np.log(self.parent.n)) / (1 + self.n) # TODO add second term
    
    @property
    def score(self):
        return self.q + self.u
    
    def update(self, value, max_value):
        self.q = (self.q * self.n + value) / (self.n + 1)
        self.n += 1
        if self.max_value < max_value:
            self.max_val = max_value
        if self.parent:
            self.parent.update(value, max_value)
            
    def expand_node(self, valid_moves):      
        for move in valid_moves:
            new_state = self.state.move(*move)
            child_node = Node(state=new_state, parent=self, move=move)
            self.children.append(child_node)
    
    def select_child(self):
        best_score = max(child.score for child in self.children)
        best_children = [child for child in self.children if child.score == best_score]
        return random.choice(best_children) # break ties randomly

    def select_move(self): # TODO: this should be the highest rollout score
        
        best_value = max(child.max_value for child in self.children)
        best_children = [child for child in self.children if child.max_value == best_value]
        return random.choice(best_children).move # break ties randomly
    
    def rollout(self):
        state = self.state.copy()
        while state.is_terminal() == Sokoban.REWARD_STEP:
            state = state.move(*random.choice(state.valid_moves()))
        return state.is_terminal()
    
class MCTS():
    def __init__(self, level_id):
        self.root = Node(parent=None, state=Sokoban.SokobanBoard(level_id=level_id), move=None)
    
    def select_leaf(self, node):
        while len(node.children) != 0 and node.is_terminal == Sokoban.REWARD_STEP:
            node = node.select_child()
        return node
    
    def expand(self, node):
        if node.is_terminal != Sokoban.REWARD_STEP:
            node.update(node.is_terminal, node.is_terminal)
        else:
            value = node.rollout()
            node.update(value, value)
            node.expand_node(node.state.valid_moves())
    
    def run(self, simulations):
        for _ in range(simulations):
            node = self.select_leaf(self.root)
            self.expand(node)
        self.visualize()
        return self.best_move
    
    @property
    def best_move(self):
        return self.root.select_move()
    
    def visualize(self):
        dot = Digraph()
        q = Queue()
        
        q.put(self.root)
        
        while not q.empty():
            node = q.get()
            node_label = node.state.__repr__()+f"score: {round(node.score, 3)},\n n: {node.n},\n steps: {node.state.steps}"
            shape = 'oval'
            color = 'black'
            if node.is_terminal == Sokoban.REWARD_WIN:
                node_label += f"\noutcome: {node.is_terminal}"
                shape = 'octagon'
                color = 'green'
            elif node.is_terminal == Sokoban.REWARD_LOSS:
                node_label += f",\noutcome: {node.is_terminal}"
                shape = 'rectangle'
                color = 'red'
            dot.node(str(node), label=node_label, shape=shape, color=color)
            
            for child in node.children:
                q.put(child)
                dot.edge(str(node), str(child), label=str(child.move))
        
        dot.render('mcts', format='pdf', cleanup=True)