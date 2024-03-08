from copy import deepcopy
from collections import deque
import random
from scipy.optimize import linear_sum_assignment

class Game:   

    def __init__(self, level_id=None, disable_prints=True):

        # Define the characters for each element in the game
        self.wall = '#'
        self.box = '$'
        self.goal = '.'
        self.player = '@'
        self.floor = ' '
        self.box_on_goal = '*'
        self.player_on_goal = '+'
        self.bedrock = ':'
        
        # Initialize the game board as a list of lists (2D array)
        self.level_id = level_id
        self.board = self.random_board() if self.level_id is None else Game.load_microban_level(self.level_id) # need to call base class method for inheritance to work later
        self.player_position = self.find_element(self.player)
 
        # Status of the game:
        self.disable_prints = disable_prints
        self.end = False
        self.turn = 0
        self.max_number_of_turns = 100
        self.reward = 0
        self.move_changed_smth = False
        self.number_of_boxes_on_goal = len(self.find_elements(self.box_on_goal))
        self.total_number_of_boxes = len(self.find_elements(self.box)) + self.number_of_boxes_on_goal

        # Status of the player:
        self.current_move = None
  
    def load_microban_level(level_id):
        # load microban level, levels are indexed from 1 to 155

        if level_id < 1 or level_id > 155:
            raise ValueError("Level ID must be between 1 and 155 for Microban levels.")
        
        with open(f"levels/microban.txt", "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if line.startswith(f"; {level_id}"):
                    j = i + 1
                    while not lines[j].startswith(";"):
                        j += 1
                    level = [list(lines[k][:-1]) for k in range(i+2,j-1)]
                    return level

    def play(self, moves=None, gamma=None):
        self.print_board()
        if moves is None:
            while(True):
                    print(f"{self.number_of_boxes_on_goal}/{self.total_number_of_boxes}")
                    self.input()
                    self.update_positions()
                    self.update_game_status()
                    self.log_game()
                    self.print_board()
                    self.turn += 1
        else:
            
            for move in moves:
                self.current_move = move
                self.update_positions()
                self.update_game_status()
                self.log_game()
                self.print_board()
                self.turn += 1
            return self.state(gamma=gamma)

    def input(self):
        while(True):
            user_input = input().strip().lower()
            if user_input in ["w", "a", "s", "d"]:
                self.current_move = user_input
                return
            else:
                print("Invalid input. Please enter 'w', 'a', 's', 'd'")
                return

    def print_board(self, board=None):
        if self.disable_prints:
            return
        
        if board is None:
            board = self.board

        for row in board:
            print("".join(row)) 

    def embed(self, level=None, by_value=False):
        # embed level into larger array of size 20*30 at a random position
        if level is None:
            level = self.board
        embedded = [[self.bedrock for _ in range(30)] for _ in range(20)]
        height = len(level)
        width = max([len(level[i]) for i in range(height)])

        x_offset = 20 - height
        y_offset = 30 - width

        x_offset = random.randint(0, x_offset-1)
        y_offset = random.randint(0, y_offset-1)

        for i in range(height):
            for j in range(len(level[i])):
                embedded[i+x_offset][j+y_offset] = level[i][j]
        if not by_value:
            self.board = embedded
            self.player_position = self.find_element(self.player)

        return embedded

    def find_element(self, element, board=None):
        if board is None:
            board = self.board
        """Find the position of a single element (e.g., the player)"""
        for x, row in enumerate(board):
            for y, char in enumerate(row):
                if char == element:
                    return [x, y]
        return None

    def find_elements(self, element, board=None):
        if board is None:
            board = self.board
        """Find positions of multiple elements (e.g., boxes)"""
        positions = []
        for x, row in enumerate(board):
            for y, char in enumerate(row):
                if char == element:
                    positions.append([x, y])
        return positions
    
    def convert(self, level):
        level = deepcopy(level)
        for i in range(len(level)):
            for j in range(len(level[i])):
                if level[i][j] == self.wall:
                    level[i][j] = 0
                elif level[i][j] == self.box:
                    level[i][j] = 1
                elif level[i][j] == self.goal:
                    level[i][j] = 2
                elif level[i][j] == self.player:
                    level[i][j] = 3
                elif level[i][j] == self.floor:
                    level[i][j] = 4
                elif level[i][j] == self.box_on_goal:
                    level[i][j] = 5
                elif level[i][j] == self.player_on_goal:
                    level[i][j] = 6
                elif level[i][j] == self.bedrock:
                    level[i][j] = 7
        return level

 
    def find_interior(self, level):
        level = deepcopy(level)
        height = len(level)
        width = max([len(level[i]) for i in range(height)])
        interior = [['#' for j in range(width)] for i in range(height)]
        
        # use breadth first search to find the interior
        queue = deque([self.find_element(self.box_on_goal, level)] if self.find_element(self.box_on_goal, level) else [self.find_element(self.box, level)]) # TODO: this will fail for 155 since there are boxes that are isolated
        while queue:
            x, y = queue.popleft()
            if interior[x][y] == '#':
                interior[x][y] = ' '
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    new_x, new_y = x + dx, y + dy
                    if 0 <= new_x < height and 0 <= new_y < width and level[new_x][new_y] in [self.floor, self.goal, self.box, self.box_on_goal, self.player, self.player_on_goal]:
                        if interior[new_x][new_y] == '#':
                            queue.append((new_x, new_y))
                            level[new_x][new_y] = ';' # mark as visited
        return interior

    def update_positions(self):
        next_player_position = self.adjacent_position(self.player_position)
        next_player_obstacle = self.board[next_player_position[0]][next_player_position[1]] # TODO: find clearner expression for this
        if next_player_obstacle == self.wall:
            return
        
        elif next_player_obstacle in [self.box, self.box_on_goal]:
            next_box_position = self.adjacent_position(next_player_position)
            next_box_obstacle = self.board[next_box_position[0]][next_box_position[1]]

            if next_box_obstacle == self.floor:
                self.board[next_box_position[0]][next_box_position[1]] = self.box
                self.board[next_player_position[0]][next_player_position[1]] = self.player_on_goal if self.board[next_player_position[0]][next_player_position[1]] == self.box_on_goal else self.player
                if self.board[next_player_position[0]][next_player_position[1]] == self.player_on_goal:
                    self.number_of_boxes_on_goal -= 1
                self.board[self.player_position[0]][self.player_position[1]] = self.goal if self.board[self.player_position[0]][self.player_position[1]] == self.player_on_goal else self.floor
                self.player_position = next_player_position
                self.move_changed_smth = True

            elif next_box_obstacle == self.goal:
                self.board[next_box_position[0]][next_box_position[1]] = self.box_on_goal
                self.board[next_player_position[0]][next_player_position[1]] = self.player_on_goal if self.board[next_player_position[0]][next_player_position[1]] == self.box_on_goal else self.player
                if self.board[next_player_position[0]][next_player_position[1]] == self.player_on_goal:
                    self.number_of_boxes_on_goal -= 1
                self.board[self.player_position[0]][self.player_position[1]] = self.goal if self.board[self.player_position[0]][self.player_position[1]] == self.player_on_goal else self.floor 
                self.player_position = next_player_position
                self.number_of_boxes_on_goal += 1
                self.move_changed_smth = True
            else:
                return

        elif next_player_obstacle == self.floor:
            self.board[self.player_position[0]][self.player_position[1]] = self.goal if self.board[self.player_position[0]][self.player_position[1]] == self.player_on_goal else self.floor
            self.board[next_player_position[0]][next_player_position[1]] = self.player
            self.player_position = next_player_position
            self.move_changed_smth = True

        elif next_player_obstacle == self.goal:
            self.board[self.player_position[0]][self.player_position[1]] = self.goal if self.board[self.player_position[0]][self.player_position[1]] == self.player_on_goal else self.floor 
            self.board[next_player_position[0]][next_player_position[1]] = self.player_on_goal
            self.player_position = next_player_position
            self.move_changed_smth = True
        else:
            print("ERROR")
            assert(0)

    def adjacent_position(self, position, move=None):
        if move is None:
            move = self.current_move
        new_position = position[:]
        if move == "w":
            new_position[0] -= 1
        elif move == "a":
            new_position[1] -= 1
        elif move == "s":
            new_position[0] += 1
        elif move == "d":
            new_position[1] += 1
        return new_position

    def update_game_status(self):
        if(self.move_changed_smth):
            if(self.number_of_boxes_on_goal == self.total_number_of_boxes):
                self.end=True
                if self.disable_prints == False:
                    print("WIN!")
        self.move_changed_smth = False
        if self.turn > self.max_number_of_turns:
            self.end = True
            if self.disable_prints == False:
                print("LOSE!")

    def step(self, action, gamma=1):
        board = deepcopy(self.board)
        player_position = deepcopy(self.player_position)
        number_of_boxes_on_goal = self.number_of_boxes_on_goal

        next_player_position = self.adjacent_position(player_position, action)
        next_player_obstacle = board[next_player_position[0]][next_player_position[1]] # TODO: find clearner expression for this
        
        if next_player_obstacle in [self.box, self.box_on_goal]:
            next_box_position = self.adjacent_position(next_player_position, action)
            next_box_obstacle = board[next_box_position[0]][next_box_position[1]]

            if next_box_obstacle == self.floor:
                board[next_box_position[0]][next_box_position[1]] = self.box
                board[next_player_position[0]][next_player_position[1]] = self.player_on_goal if board[next_player_position[0]][next_player_position[1]] == self.box_on_goal else self.player
                if board[next_player_position[0]][next_player_position[1]] == self.player_on_goal:
                    number_of_boxes_on_goal -= 1
                board[self.player_position[0]][player_position[1]] = self.goal if board[player_position[0]][player_position[1]] == self.player_on_goal else self.floor
                player_position = next_player_position

            elif next_box_obstacle == self.goal:
                board[next_box_position[0]][next_box_position[1]] = self.box_on_goal
                board[next_player_position[0]][next_player_position[1]] = self.player_on_goal if board[next_player_position[0]][next_player_position[1]] == self.box_on_goal else self.player
                if board[next_player_position[0]][next_player_position[1]] == self.player_on_goal:
                    number_of_boxes_on_goal -= 1
                board[player_position[0]][player_position[1]] = self.goal if board[player_position[0]][player_position[1]] == self.player_on_goal else self.floor 
                player_position = next_player_position
                number_of_boxes_on_goal += 1

        elif next_player_obstacle == self.floor:
            board[player_position[0]][player_position[1]] = self.goal if board[player_position[0]][player_position[1]] == self.player_on_goal else self.floor
            board[next_player_position[0]][next_player_position[1]] = self.player
            player_position = next_player_position

        elif next_player_obstacle == self.goal:
            board[player_position[0]][player_position[1]] = self.goal if board[player_position[0]][player_position[1]] == self.player_on_goal else self.floor 
            board[next_player_position[0]][next_player_position[1]] = self.player_on_goal
            player_position = next_player_position
        
        reward = 0
        end = 0
        if number_of_boxes_on_goal == self.total_number_of_boxes:
            reward = 10
            end = 1

        return [self.targets(board=board), self.distance(board=board), self.gamma1(gamma=gamma), self.gamma2(gamma=gamma, board=board), self.connectivity(board=board)], reward, end
   
    """
    compute features needed for the state feed into the RL agent
    """
    def targets(self, board=None):
        number_of_boxes_on_goal = len(self.find_elements(self.box_on_goal, board)) if board is not None else self.number_of_boxes_on_goal
        return number_of_boxes_on_goal / self.total_number_of_boxes
    
    def gamma1(self, gamma):
        return pow(gamma, self.total_number_of_boxes)

    def gamma2(self, gamma, board=None):
        number_of_boxes_on_goal = len(self.find_elements(self.box_on_goal, board)) if board is not None else self.number_of_boxes_on_goal
        return pow(gamma, self.total_number_of_boxes - number_of_boxes_on_goal)
   
    # TODO: get something more sophisticated here: taking into account the player movement when he goes from box to box
    # current idea: model problem as assignment problem (the assumption that the graph is bipartite fully connected might be violated for example:
    #   #######
    #   #.$@$.#
    #   ####### )
    # Nevertheless we use BFS to compute the pairwise distances (ignoring other boxes and the player, only worrying about the walls themselves) and then we use the Hungarian algorithm to solve the assignment problem

    def distance(self, board=None):
        if board is None:
            board = self.board
        cost_matrix = self.get_pairwise_distances(board)

        # using the Hungarian algorithm to solve the assignment problem
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        # Calculate the minimum cost based on the assignment
        min_cost = sum([cost_matrix[row_ind[i]][col_ind[i]] for i in range(len(row_ind))])
        # need to add a component that gives distance between player and next next box
        player_distance  = self.bfs(self.player_position, self.find_elements(self.box_on_goal, board=board), board=board)
        if len(player_distance) == 0:
            return min_cost
        return min_cost + min(player_distance.values())

    def get_pairwise_distances(self, board):
        box_positions = sorted(self.find_elements(self.box, board=board) + self.find_elements(self.box_on_goal, board=board))
        goal_positions = sorted(self.find_elements(self.goal, board=board) + self.find_elements(self.player_on_goal, board=board) + self.find_elements(self.box_on_goal, board=board))
        assert(len(box_positions) == len(goal_positions))
        size = len(box_positions)
        
        distances = [[0 for _ in range(size)] for _ in range(size)]
        for i in range(size):
            box_distances = self.bfs(box_positions[i], goal_positions, board=board)
            for j in range(size):
                distances[i][j] = box_distances[(goal_positions[j][0], goal_positions[j][1])]
        
        return distances
    
    def bfs(self, start, end, board):
        distance = {}
        reached_goals = set()
        queue = deque([start])
        height = len(board)
        width = max(len(row) for row in board)
        visited = [[False for _ in range(width)] for _ in range(height)]
        visited[start[0]][start[1]] = True
        
        step = 0
        while queue:
            for _ in range(len(queue)):
                x, y = queue.popleft()
                if [x, y] in end:
                    reached_goals.add((x, y))
                    distance[(x, y)] = step
                    if len(reached_goals) == len(end):
                        return distance
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    new_x, new_y = x + dx, y + dy
                    if 0 <= new_x < height and 0 <= new_y < width and not visited[new_x][new_y]:
                        if board[new_x][new_y] in [self.floor, self.goal, self.box, self.box_on_goal, self.player, self.player_on_goal]:
                            queue.append((new_x, new_y))
                            visited[new_x][new_y] = True
            step += 1
        return distance 

    def connectivity(self, board=None):
        if board is None:
            board = self.board
        connected_components = 0
        floor = self.find_elements(self.floor, board=board)
        height = len(self.board)
        width = max(len(row) for row in board)
        visited = [[0 for _ in range(width)] for _ in range(height)]
        for pos in floor:
            if visited[pos[0]][pos[1]] == 0:
                connected_components += 1
            queue = deque([pos])
            while queue:
                x, y = queue.popleft()
                visited[x][y] = 1
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    new_x, new_y = x + dx, y + dy
                    if not visited[new_x][new_y] and board[new_x][new_y] == self.floor:
                        queue.append((new_x, new_y))

        return connected_components # we want this to be normalized maybe this will do it, seems unlikely that board has more than 10 connected components?
        
    # POST: returns the state of the game
    def state(self, gamma=1):
        return [self.targets(), self.distance(), self.gamma1(gamma), self.gamma2(gamma), self.connectivity()], self.reward, self.end

    
if __name__ == "__main__":
    Wearhouse = Game(2, disable_prints=False)
    #Wearhouse.play()
    Wearhouse.print_board()
    box = Wearhouse.find_element(Wearhouse.box)
    # print(Wearhouse.bfs(box, Wearhouse.find_elements(Wearhouse.goal) + Wearhouse.find_elements(Wearhouse.player_on_goal) + Wearhouse.find_elements(Wearhouse.box_on_goal)))
    Wearhouse.get_pairwise_distances()
    Wearhouse.distance()
    print(Wearhouse.connectivity())