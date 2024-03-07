import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from game import Game
from reverse_game import ReverseGame

# TODO: the problem here is that the levels differ in size, so the input size will differ.
# the current solution is to just use the dimension of the largest level and pad the smaller levels with special values (don't think it is a good idea to use walls to pad)
# probably the location of the padding makes a very big difference (i.e. neurons on the top left have seen much more examples than neurons on the bottom right)
class ValueNetwork(nn.Module):
    def __init__(self, input_size, output_size):
        super(ValueNetwork, self).__init__()
        # Simple linear layer to represent the value function
        self.embedding = nn.Embedding(num_embeddings=7, embedding_dim=3)
        self.conv = nn.Conv2d(in_channels=3, out_channels=1, kernel_size=2, stride=1, padding=0) # TODO: output size depends on input size
        self.linear = nn.Linear(input_size, output_size)

    def forward(self, state):
        state = self.embedding(state)
        # [batch_dim, height, width, channels] -> [batch_dim, channels, height, width]
        state = state.permute(0, 3, 1, 2)
        state = self.conv(state)
        # [batch_dim, channels, height, width] -> [batch_dim, height, width]
        state = state.view(state.size(0), -1)
        state = self.linear(state)
        return state

# Hyperparameters
        # input_size = <size_of_state_vector>  # Depends on the environment
        # learning_rate = 0.01
        # gamma = 0.99  # Discount factor

class Agent():
    def __init__(self, input_size, learning_rate=0.01, gamma=0.99, epsilon=0.1):
        
        self.input_size = input_size
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.model = ValueNetwork(input_size, 1)
        # Model, optimizer, and loss function
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        self.loss_fn = nn.MSELoss()
    

    def epsilon_greedy_policy(self, state_value, env):
        if np.random.rand() < self.epsilon:
            return np.random.choice(["w", "a", "s", "d"])  # Explore: random action
        else:
            # TODO: this will fail as soon as we use batches
            options = {}
            for action in ["w", "a", "s", "d"]:
                next_state, reward, done = env.step(action)
                next_state_tensor = torch.tensor(next_state, dtype=torch.int32).unsqueeze(0)
                next_value = self.model(next_state_tensor)
                options[action] = next_value
            return max(options, key=options.get)  # Exploit: action with the highest value

    def train(self, num_episodes):
        wins = 0
        tries = 0
        for episode in range(num_episodes):
            tries += 1
            # use microban level 3

            env = ReverseGame(Game(level_id=3))
            state, _ , done = env.state()
            # TODO: convert chars to numbers, then add embedding layer to network
            while not done:
                state_tensor = torch.tensor(state, dtype=torch.int32).unsqueeze(0)  # Convert state to tensor and add batch dimension
                value = self.model(state_tensor)  # Estimate the value of the current state
                
                action = self.epsilon_greedy_policy(state, env)  # Define or choose your action selection strategy
                next_state, reward, done = env.play(action)  # Take a step in the environment
                wins += reward/10
                if reward != 0:
                    assert(done)
                next_state_tensor = torch.tensor(next_state, dtype=torch.int32).unsqueeze(0)
                next_value = self.model(next_state_tensor)  # Estimate value of next state
                # TD(0) target
                target = reward + (self.gamma * next_value * (1 - int(done)))  # Adjust target for terminal states
                
                # TD(0) error
                loss = self.loss_fn(value, target.detach())
                
                # Backpropagation
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
                state = next_state  # Move to the next state
        return wins, tries

    

if __name__ == "__main__":
    # Define the input size
    input_size = 40  # TODO: Define the size of the state vector
    learning_rate = 0.01
    gamma = 0.99  # Discount factor

    # Initialize the agent
    agent = Agent(input_size, learning_rate, gamma)
    agent2 = Agent(input_size, learning_rate, gamma)
    agent3 = Agent(input_size, learning_rate, gamma)

    # Train the agent
    #wins1, tries1 = agent.train(num_episodes=100)  # Train for 1000 episodes
    #wins2, tries2 = agent2.train(num_episodes=1000)  # Train for 1000 episodes
    wins3, tries3 = agent3.train(num_episodes=10000)  # Train for 1000 episodes
    print(wins3/tries3)

    # 0.066 50 0.03 100 0.066 1000 0.18 5000 0.16