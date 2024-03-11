import numpy as np
import json
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from game import Game, ReverseGame
from tqdm import tqdm
import random

log_move_gred = [0,0,0,0,0]
log_move_rand = [0,0,0,0,0]

class ValueNetwork(nn.Module):
    def __init__(self, input_size=5, output_size=1):
        super(ValueNetwork, self).__init__()
        self.linear1 = nn.Linear(input_size, 512)
        self.linear2 = nn.Linear(512, 512)
        self.linear3 = nn.Linear(512, output_size)

    def forward(self, state):
        state = self.linear1(state)
        state = self.linear2(state)
        state = self.linear3(state)
        return state


class Agent():
    def __init__(self, input_size=5, learning_rate=0.01, alpha=0.98, gamma=0.99, epsilon=0.1, alpha_discount=0.98):
        self.alpha = alpha
        self.alpha_discount = alpha_discount
        self.input_size = input_size
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.model = ValueNetwork(input_size, 1)
        # Model, optimizer, and loss function
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.loss_fn = nn.MSELoss()

    def greedy_policy(self, state_value, env):
        move = None
        # TODO: this will fail as soon as we use batches
        options = {}
        legal_moves = env.legal_moves()
        if len(legal_moves) == 0:
          log_move_gred[4] = log_move_gred[4] + 1
          return None
        for action in legal_moves:
            next_state, reward, done = env.step(action, self.gamma)
            next_state_tensor = torch.tensor(next_state, dtype=torch.float32).unsqueeze(0)
            next_value = self.model(next_state_tensor)
            options[action] = next_value
        move = max(options, key=options.get)  # Exploit: action with the highest value
        if move == "w":
          log_move_gred[0] = log_move_gred[0]+1
        if move == "a":
          log_move_gred[1] = log_move_gred[1]+1
        if move == "s":
          log_move_gred[2] = log_move_gred[2]+1
        if move == "d":
          log_move_gred[3] = log_move_gred[3]+1
        return move

    def random_policy(self, env):
        legal_moves = env.legal_moves()
        if len(legal_moves) == 0:
          log_move_rand[4] = log_move_rand[4]+1
          return None
        move = np.random.choice(["w", "a", "s", "d"])
        if move == "w":
          log_move_rand[0] = log_move_rand[0]+1
        if move == "a":
          log_move_rand[1] = log_move_rand[1]+1
        if move == "s":
          log_move_rand[2] = log_move_rand[2]+1
        if move == "d":
          log_move_rand[3] = log_move_rand[3]+1
        return move

    def random_baseline(self, num_episodes, start=1, end=10):
        wins = 0
        hist=[]
        moves = []
        for episode in range(num_episodes):
            id = random.randint(start,end)
            env = ReverseGame(Game(level_id=id))
            if episode % 100 == 0:
              moves.append(env.player_position)
            _ , _ , done = env.state(self.gamma)
            # TODO: convert chars to numbers, then add embedding layer to network
            while not done:
                action = self.random_policy(env)  # Define or choose your action selection strategy
                if action is None: # agent is stuck and can't move
                  done = True
                  continue
                if episode % 100 == 0:
                  moves.append(action)
                next_state, reward, done = env.play(action, gamma=self.gamma)  # Take a step in the environment
                wins += reward
            hist = hist + [wins/(episode+1)]
        return wins, num_episodes, moves

    def train(self, num_episodes, start=0, end=155):
        wins = 0
        hist = []
        moves = []
        for episode in tqdm(range(num_episodes)):
            # print("-----")
            id = random.randint(start,end)
            env = ReverseGame(Game(level_id=id))
           
            state, _ , done = env.state(self.gamma)
            if episode % 100 == 0:
              moves.append(env.player_position)
            while not done:
                #env.disable_prints = False
                #env.print_board()
                #env.disable_prints = True
                state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
                value = self.model(state_tensor)

                action = self.greedy_policy(state, env)
                if action is None: # agent is stuck and can't move
                  done = True
                  continue
                if episode % 100 == 0:
                  moves.append(action)
                next_state, reward, done = env.step(action, gamma=self.gamma)
                wins += reward
                next_state_tensor = torch.tensor(next_state, dtype=torch.float32).unsqueeze(0)
                next_value = self.model(next_state_tensor)
                # TD(0) target
                target = value + self.alpha*(reward + self.gamma * next_value.detach() * (1 - int(done)) - value)

                # TD(0) error
                loss = self.loss_fn(value, target)
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()

                # off policy exploration
                if np.random.rand() < self.epsilon:
                  action = self.random_policy(env)
                  next_state, reward, done = env.play(action, gamma=self.gamma)
                else:
                  env.play(action, gamma=self.gamma)
                state = next_state
              
            self.alpha = self.alpha * self.alpha_discount
            hist = hist + [wins/(episode+1)]

        return wins, num_episodes, moves

if __name__ == "__main__":

    # Define the input size
    learning_rate = 0.01
    gamma = 0.8  # Discount factor

    # Initialize the agent
    agent = Agent(learning_rate=learning_rate, gamma=gamma)
    agent2 = Agent(learning_rate=learning_rate, gamma=gamma)
    agent3 = Agent(learning_rate=learning_rate, gamma=gamma)

    # Train the agent
    #wins1, tries1 = agent.train(num_episodes=100)  # Train for 1000 episodes
    wins2, tries2, moves2 = agent2.train(num_episodes=100, start=0, end=0)  # Train for 1000 episodes
    print(wins2, "|", wins2/tries2)
    wins3, tries3, moves3 = agent3.random_baseline(num_episodes=100, start=0, end=0)
    print(wins3, "|",wins3/tries3)
    # File path to store the JSON data
    file_path = "run.json"

    # Convert the list to a JSON-serializable format
    json_data = json.dumps(moves3)

    # Write the JSON data to the file
    with open(file_path, "w") as file:
        file.write(json_data)

    print([c / sum(log_move_gred) for c in log_move_gred])
    print([c / sum(log_move_rand) for c in log_move_rand])