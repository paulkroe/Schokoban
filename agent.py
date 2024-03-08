import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from game import Game
from reverse_game import ReverseGame
from tqdm import tqdm
import random

# TODO: the problem here is that the levels differ in size, so the input size will differ.
# the current solution is to just use the dimension of the largest level and pad the smaller levels with special values (don't think it is a good idea to use walls to pad)
# probably the location of the padding makes a very big difference (i.e. neurons on the top left have seen much more examples than neurons on the bottom right)
# in the current solution in most of the training each neuron only sees bedrock. should fix this
class ValueNetwork(nn.Module):
    def __init__(self, input_size=5, output_size=1):
        super(ValueNetwork, self).__init__()
        self.linear = nn.Linear(input_size, output_size)

    def forward(self, state):
        state = self.linear(state)
        return state

# Hyperparameters
        # input_size = <size_of_state_vector>  # Depends on the environment
        # learning_rate = 0.01
        # gamma = 0.99  # Discount factor

class Agent():
    def __init__(self, input_size=5, learning_rate=0.01, gamma=0.99, epsilon=0.2):
        self.input_size = input_size
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.model = ValueNetwork(input_size, 1)
        # Model, optimizer, and loss function
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        self.loss_fn = nn.MSELoss()

    def epsilon_greedy_policy(self, state_value, env, discount=1):
        if np.random.rand() < self.epsilon/discount:
            return np.random.choice(["w", "a", "s", "d"])  # Explore: random action
        else:
            # TODO: this will fail as soon as we use batches
            options = {}
            for action in ["w", "a", "s", "d"]:
                next_state, reward, done = env.step(action, self.gamma)
                next_state_tensor = torch.tensor(next_state, dtype=torch.float32).unsqueeze(0)
                next_value = self.model(next_state_tensor)
                options[action] = next_value
            return max(options, key=options.get)  # Exploit: action with the highest value

    def random_policy(self):
        return np.random.choice(["w", "a", "s", "d"])

    def random_baseline(self, num_episodes):
        wins = 0
        hist=[]
        for episode in range(num_episodes):
            
            env = ReverseGame(Game(level_id=3))
            _ , _ , done = env.state(self.gamma)
            # TODO: convert chars to numbers, then add embedding layer to network
            while not done:
                action = self.random_policy()  # Define or choose your action selection strategy
                next_state, reward, done = env.play(action, gamma=self.gamma)  # Take a step in the environment
                wins += reward/10
            hist = hist + [wins/(episode+1)]
        return wins, num_episodes

    def train(self, num_episodes):
        wins = 0
        losses = []
        hist = []
        for episode in tqdm(range(num_episodes)):
            env = ReverseGame(Game(level_id=3))
            state, _ , done = env.state(self.gamma)

            while not done:
                # print(state)
                state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0)  # Convert state to tensor and add batch dimension
                value = self.model(state_tensor)  # Estimate the value of the current state

                action = self.epsilon_greedy_policy(state, env, discount=(episode/100+1))  # Define or choose your action selection strategy
                next_state, reward, done = env.play(action, gamma=self.gamma)  # Take a step in the environment
                wins += reward/10
                next_state_tensor = torch.tensor(next_state, dtype=torch.float32).unsqueeze(0)
                next_value = self.model(next_state_tensor)  # Estimate value of next state
                # TD(0) target
                target = reward + (self.gamma * next_value * (1 - int(done)))  # Adjust target for terminal states

                # TD(0) error
                loss = self.loss_fn(value, target.detach())
                losses.append(loss)

                # Backpropagation
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
                state = next_state  # Move to the next state
            hist = hist + [wins/(episode+1)]
        print(len([loss.detach().numpy() for loss in losses if loss != 0]))

        return wins, num_episodes
if __name__ == "__main__":

    # Define the input size
    learning_rate = 0.05
    gamma = 0.99  # Discount factor

    # Initialize the agent
    agent = Agent(learning_rate=learning_rate, gamma=gamma)
    agent2 = Agent(learning_rate=learning_rate, gamma=gamma)
    agent3 = Agent(learning_rate=learning_rate, gamma=gamma)

    # Train the agent
    #wins1, tries1 = agent.train(num_episodes=100)  # Train for 1000 episodes
    wins2, tries2 = agent2.train(num_episodes=1000)  # Train for 1000 episodes
    print(wins2, "|", wins2/tries2)
    wins3, tries3 = agent3.random_baseline(num_episodes=100)  # Train for 1000 episodes
    print(wins3, "|",wins3/tries3)