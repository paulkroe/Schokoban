import numpy as np
import math
from queue import Queue
import random

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# constant balancing exploration and exploitation
C_PUT = 8

class Node():
    def __init__(self, parent, state, move, depth):
        # depth of the node in the Monte Carlo Search Tree (MCST)
        self.depth = depth
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
        
    @property
    def u(self):
        if self.parent is None:
            return 0
        # exploration term in the UCT formula
        return C_PUT * np.sqrt(2*np.log(self.parent.n)) / (self.n)
    
    # returns UCT score
    @property
    def score(self):
        return self.q + self.u
   
    # recursively update the value of a node the value obtained from the last rollout 
    def update(self, value, max_value):
        self.q = (self.q * self.n + value) / (self.n + 1)
        self.n += 1
        if self.max_value.get_value() < max_value.get_value():
            self.max_value = max_value
        if self.parent:
            self.parent.update(value, max_value) 
    
    # recursively update the depth of a node
    def update_depth(self, depth):
        self.depth = depth
        self.state.steps = depth
        for child in self.children.values():
            child.update_depth(depth+1)
    
    # after moving a subtree to a new parent, recursively update the new parent and its ancestors
    def upgrade(self, n, value):
        self.n += n
        self.q = (self.q * (self.n-n) + value*n) / (self.n)
        if len(self.children) != 0:
            max_values = [child.max_value.get_value() for child in self.children.values()]
            best_value = max(max_values)
            for child in self.children.values():
                if child.max_value.get_value() == best_value:
                    child.max_value = child.max_value 
        else:
            self.max_value = self.reward
        if self.parent:
            self.parent.upgrade(n, value)
    
    # after moving a subtree to a new parent, recursively update the old parent and its ancestors
    def downgrade(self, n, value):
        self.n -= n
        self.q = (self.q * (self.n+n) - value*n) / (self.n)
        if len(self.children) != 0:
            max_values = [child.max_value.get_value() for child in self.children.values()]
            best_value = max(max_values)
            for child in self.children.values():
                if child.max_value.get_value() == best_value:
                    child.max_value = child.max_value
        else:
            self.max_value = self.reward
        if math.isnan(self.score):
            print(self.q)
            print(self.n)
            print(self.state)
            print("nan")
            assert 0
        
        if self.parent:
            self.parent.downgrade(n, value)
           
    # expands a node by adding its children to the tree, unnecessary children are removed, and the tree restructured if necessary
    def expand_node(self, valid_moves, mcts):
        for move in valid_moves:
            new_state = self.state.move(*move)
            new_hash = new_state.hash
            # child has not yet been added to the tree
            if not (new_hash in mcts.del_nodes or new_hash in mcts.nodes):
                child_node = Node(state=new_state, parent=self, move=move, depth=self.depth+1)
                self.children[move] = child_node
                mcts.nodes[new_hash] = child_node
            # child has already been added to the tree at a lower depth
            elif new_hash in mcts.nodes and self.depth+1 < mcts.nodes[new_hash].depth:
                self.children[move] = mcts.nodes[new_hash]
                del mcts.nodes[new_hash].parent.children[mcts.nodes[new_hash].move]
                # try to delete parent node if it has no children
                n = mcts.nodes[new_hash].n
                value = mcts.nodes[new_hash].q

                N = mcts.root.n
                V = mcts.root.q
                # downgrade old parent
                mcts.nodes[new_hash].parent.downgrade(n, value)
                
                if mcts.nodes[new_hash].parent.should_remove():
                    mcts.nodes[new_hash].parent.remove(mcts)
                
                mcts.nodes[new_hash].parent = self
                mcts.nodes[new_hash].move = move
             
                # recursively update the depth of the children
                mcts.nodes[new_hash].update_depth(self.depth+1)

                
                # upgrade new parent
                self.upgrade(n, value)
                
        # important that this is not done in one loop
        for move in valid_moves:
            if move in self.children: # could be that child caused cycle and thus was not added
                if self.children[move].reward.get_type() == "LOSS" or self.children[move] in mcts.del_nodes:
                    assert self.children[move].should_remove()
                    self.children[move].remove(mcts)
                    
        # it might be that during expansion no node was added, in this case delete the current node  
        if self.should_remove() and (not self.state.hash in mcts.del_nodes):
            self.remove(mcts)
        
    # selects the child node according to the UCT policy
    def select_child(self):
        
        # if there is a unvisited node, visit that node first
        unvisited = [child for child in self.children.values() if child.n == 0]
        if len(unvisited) > 0:
            return random.choice(unvisited)
       
        # otherwise select the child with the highest UCT score 
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
        return len(self.children) == 0 and not (self.max_value.get_type() == "WIN")
    
    # recursively removes the node from the tree
    def remove(self, mcts):
        mcts.del_nodes.add(self.state.hash)
        if self.state.hash == mcts.root.state.hash: # if the rot node is deleted, the level can't be solveds
            return
        del mcts.nodes[self.state.hash]
        assert len(self.children) == 0
        parent = self.parent
        if not parent is None:
            del parent.children[self.move]
            if parent.should_remove() or parent in mcts.del_nodes:
                parent.remove(mcts)
    
class MCTS():
    def __init__(self, sokobanboard):
        self.root = Node(parent=None, state=sokobanboard, move=None, depth=0)
        self.del_nodes = set()
        self.nodes = {self.root.state.hash: self.root}
    
    # returns the leaf node selected during selection phase
    def select_leaf(self, node):
        while len(node.children) != 0 and node.reward.get_type() == "STEP":
            node = node.select_child()
        return node
    
    # expansion phase
    def expand(self, node):
        node.expand_node(node.state.valid_moves(), self)
                
    # runs the MCTS algorithm for a given number of iterations
    def run(self, iterations, verbose=0):
        for i in range(iterations):
            if verbose:
                print(f"Simulation {i+1}, {len(self.nodes)} nodes, {len(self.del_nodes)} deleted nodes", end="\r")
            # selection phase
            node = self.select_leaf(self.root)
            # if all states have been explored and there is no solution, None will be returned during the selection phase
            if node is None:
                return None
            # rollout
            if node.n == 0:
                # random rollout
                reward = node.rollout()
                # backpropagate rollout value
                node.update(reward.get_value(), reward)
            # expansion phase
            else:
                # expand node
                self.expand(node)
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
            # extract solution
            while len(node.children) != 0:
                move = node.select_move()
                moves.append(move)
                node = node.children[move]
            assert node.reward.get_type() == "WIN"        
            return moves