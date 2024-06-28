import numpy as np
from queue import Queue
import random
from copy import deepcopy

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import game.Sokoban as Sokoban

# constant balancing exploration and exploitation
C_PUT = 32 
D_PUT = 8

class Node():
    def __init__(self, parent, state, move):
        # board state represented by the node
        self.state = state
        # parent node
        self.parent = parent
        # move that led to the state of the node
        self.move = move
        # node children
        self.children = {}
        # average over all rollouts that passed through the node (value of the node)
        self.q = 0
        # number of rollouts that passed through the node (visit count)
        self.n = 0
        # reward associated with the state the node represents
        self.reward = self.state.reward()
        # maximum reward of the node's and descendants, used for extracting the solution
        self.max_value = self.reward
        # sum of squares of rewards, used for calculating the variance of the rewards
        self.sum_of_squares = self.reward.get_value()**2
        
    @property
    def u(self):
        if self.parent is None:
            return 0
        # exploration term in adjusted UCTS formula
        return C_PUT * np.sqrt(2*np.log(self.parent.n)) / (self.n) + np.sqrt(self.sum_of_squares / (self.n) - self.q**2 + D_PUT)
   
    # returns adjusted UCT score 
    @property
    def score(self):
        return self.q + self.u
    
    # recursively update the value of a node the value obtained from the last rollout 
    def update(self, value, max_value):
        self.q = (self.q * self.n + value) / (self.n + 1)
        self.n += 1
        self.sum_of_squares = self.sum_of_squares + value**2
        if self.max_value.get_value() < max_value.get_value():
            self.max_value = max_value
        if self.parent:
            self.parent.update(value, max_value)
            
    # expands a node by adding its children to the tree, unnecessary children are removed
    def expand_node(self, valid_moves, hashes):
        hashes_copy = deepcopy(hashes)
        for move in valid_moves:
            new_state = self.state.move(*move)
            # don't add child if the child was already encountered during the last rollout
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

    # selects the child node according to the UCT policy
    def select_child(self):
        if len(self.children) == 0:
            return None
        
        # if there is a unvisited node, visit that node first
        unvisited = [child for child in self.children.values() if child.n == 0]
        if len(unvisited) > 0:
            return random.choice(unvisited)
        
        best_score = max(child.score for child in self.children.values())
        best_children = [child for child in self.children.values() if child.score == best_score]
        return random.choice(best_children) # break ties randomly

    # selects the move that leads to the child node with the highest value, used for extracting the solution once found
    def select_move(self):
        if len(self.children) == 0:
            return None
        else:
            best_value = max(child.max_value.get_value() for child in self.children.values())
            best_children = [child for child in self.children.values() if child.max_value.get_value() == best_value]
            return random.choice(best_children).move # break ties randomly
    
    # returns rollout value of current node
    def rollout(self):
        return self.reward
    
    # checks if the node should be removed from the tree
    def should_remove(self):
        if len(self.children) == 0 and not (self.reward.get_type() == "WIN"):
            return True
        
    # recursively removes the node from the tree
    def remove(self):
        assert len(self.children) == 0
        parent = self.parent
        if not parent is None:
            del parent.children[self.move]
            if parent.should_remove():
                parent.remove() 
    
class MCTS():
    def __init__(self, sokobanboard):
        self.root = Node(parent=None, state=sokobanboard, move=None)
         
    # returns the leaf node selected during selection phase
    def select_leaf(self, node, hashes):
        while len(node.children) != 0 and node.reward.get_type() == "STEP":
            node = node.select_child()
            hashes.append(node.state.hash)
        return node
    
    # expansion phase
    def expand(self, node, hashes):
        node.expand_node(node.state.valid_moves(), hashes)
                
    # runs the MCTS algorithm for a given number of iterations
    def run(self, iterations, verbose=0):
        for i in range(iterations):
            if verbose > 0:
                print(f"Simulation: {i}", end="\r")
            hashes = [self.root.state.hash]
            
            # selection phase
            node = self.select_leaf(self.root, hashes)
            # rollout
            if node.n == 0:
                # random rollout
                reward = node.rollout()
                # backpropagate rollout value
                node.update(reward.get_value(), reward)
            # expansion phase
            else:
                # expand node
                self.expand(node, hashes)
                # it might be that all children have already been removed from the tree again and the node removed, for example if the child was a loss
                if len(node.children):
                # pick on chlid at random for simulation
                    node = random.choice(list(node.children.values()))
                    # rollout
                    reward = node.rollout()
                    # backpropagate rollout value
                    node.update(reward.get_value(), reward)
            if self.root.max_value.get_type() == "WIN":
                break
            
        if self.root.max_value.get_type() == "WIN":
            moves = []
            node = self.root
            # if might be that after this loop node.state.reward().get_type() != "WIN" if the solution was discovered during rollout
            while len(node.children) != 0:
                move = node.select_move()
                moves.append(move)
                node = node.children[move]           
            return moves