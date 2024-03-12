from copy import deepcopy
from collections import deque
import random
from scipy.optimize import linear_sum_assignment
from enum import Enum

class GameElements(Enum):
    WALL = '#'
    BOX = '$'
    GOAL = '.'
    PLAYER = '@'
    FLOOR = ' '
    BOX_ON_GOAL = '*'
    PLAYER_ON_GOAL = '+'
    BEDROCK = ':'

class Game:

    def __init__(self, level_id=None, disable_prints=True):

        # Initialize the game board as a list of lists (2D array)
        self.level_id = level_id
        self.board = self.random_board() if self.level_id is None else Game.load_microban_level(self.level_id)
        
        # Initialize the game elements
        self.player_position = self.find_element([GameElements.PLAYER.value, GameElements.PLAYER_ON_GOAL.value])
        self.box_positions = sorted(self.find_elements([GameElements.BOX.value, GameElements.BOX_ON_GOAL.value]))
        self.goal_positions = sorted(self.find_elements([GameElements.PLAYER_ON_GOAL.value, GameElements.BOX_ON_GOAL.value, GameElements.GOAL.value]))
        
        # Status of the game:
        self.disable_prints = disable_prints
        self.end = 0
        self.turn = 0
        self.max_number_of_turns = 100
        self.reward = 0
        self.current_move = None
  
    # POST: Returns the board of the Microban level with the given level_id. level_id == 0 corresponds to a dummy training level used for testing.
    def load_microban_level(level_id):

        if level_id < 0 or level_id > 155:
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
    
    # Main loop of the game. If the game is played via the command line interface no moves need to be passed as arguments.
    # If the game is played step by step by an agent for example, the moves need to be passed as arguments.
    # The gamma parameter is used to compute the features of the state that are fed into the RL agent.
    def play(self, moves=None, gamma=None):
        self.print_board()
        if moves is None:
            while(True):
                    self.turn+=1
                    print(f"{int(self.targets(self.box_positions) * len(self.box_positions))}/{len(self.box_positions)}")
                    self.input()
                    self.update_positions()
                    self.update_game_status()
                    self.print_board()
        else:
            assert(gamma != None)
            for move in moves:
                
                self.turn+=1                   
                self.current_move = move
                self.update_positions()
                self.update_game_status()
                self.print_board()
            return self.state(gamma=gamma)
        
    # POST: Returns a move in ['w', 'a', 's', 'd']
    def input(self):
        while(True):
            user_input = input().strip().lower()
            if user_input in ["w", "a", "s", "d"]:
                self.current_move = user_input
                return
            else:
                print("Invalid input. Please enter 'w', 'a', 's', 'd'")
                return

    # Prints the current state of the game board
    def print_board(self, board=None):
        if self.disable_prints:
            return
        if board is None:
            board = self.board
        for row in board:
            print("".join(row)) 
    
    # POST: Returns the position of the first occurrence of element on the board
    # Search starts from the top left corner of the board
    # If a list of elements is passed, the function returns the position of the first occurrence of any of the elements
    def find_element(self, element, board=None):
        if board is None:
            board = self.board

        if isinstance(element, list):
            for e in element:
                for x, row in enumerate(board):
                    for y, char in enumerate(row):
                        if char == e:
                            return [x, y]
        else:
            for x, row in enumerate(board):
                for y, char in enumerate(row):
                    if char == element:
                        return [x, y]
        return None


    # POST: Returns the positions of all occurrences of element on the board
    # Search starts from the top left corner of the board
    # If a list of elements is passed, the function returns the positions of all occurrences of all the elements
    def find_elements(self, element, board=None):
        if board is None:
            board = self.board

        positions = [
            [x, y]
            for x, row in enumerate(board)
            for y, char in enumerate(row)
            if (isinstance(element, list) and char in element) or char == element
        ]
        return positions
    
    # POST: uses bfs to return the interior of a given board.
    # For example, the interior of the following board:
    # #####::
    # #   ###
    # #.$@$.#
    # #######
    # is:
    # #####::
    # #   ###
    # #     #
    # #######
    def find_interior(self, board=None):
        if board is None:
            board = self.board
        board = deepcopy(board)
        height = len(board)
        width = max([len(board[i]) for i in range(height)])
        interior = [[GameElements.WALL.value for _ in range(width)] for _ in range(height)]
        
        # use breadth first search to find the interior
        queue = deque([self.player_position])
        while queue:
            x, y = queue.popleft()
            if interior[x][y] == GameElements.WALL.value:
                interior[x][y] = GameElements.FLOOR.value
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    new_x, new_y = x + dx, y + dy
                    if 0 <= new_x < height and 0 <= new_y < width and board[new_x][new_y] in [GameElements.FLOOR.value, GameElements.GOAL.value, GameElements.BOX.value, GameElements.BOX_ON_GOAL.value, GameElements.PLAYER.value, GameElements.PLAYER_ON_GOAL.value]:
                        if interior[new_x][new_y] == GameElements.WALL.value:
                            queue.append((new_x, new_y))
                            board[new_x][new_y] = ';' # mark as visited
                            
        for x in range(height):
            for y in range(width):
                if board[x][y] == GameElements.BEDROCK.value:
                    interior[x][y] = GameElements.BEDROCK.value
        return interior

    # POST: Draws the current Player and Box positions on the board
    def redraw_board(self, player_position=None, box_positions=None, board=None):
        if board is None:
            board = self.board
        if player_position is None:
            player_position = self.player_position
        if box_positions is None:
            box_positions = self.box_positions
            
        for goal_position in self.goal_positions:
            board[goal_position[0]][goal_position[1]] = GameElements.GOAL.value
    
        board[player_position[0]][player_position[1]] = GameElements.PLAYER_ON_GOAL.value if player_position in self.goal_positions else GameElements.PLAYER.value
        
        for box_position in box_positions:
            board[box_position[0]][box_position[1]] = GameElements.BOX_ON_GOAL.value if box_position in self.goal_positions else GameElements.BOX.value
        
    def update_positions(self):
        next_player_position = self.adjacent_position(self.player_position)
        next_player_obstacle = self.board[next_player_position[0]][next_player_position[1]]
        
        # Player runs into a wall
        if next_player_obstacle == GameElements.WALL.value:
            return
        # Player runs into a box
        elif next_player_obstacle in [GameElements.BOX.value, GameElements.BOX_ON_GOAL.value]:
            next_box_position = self.adjacent_position(next_player_position)
            next_box_obstacle = self.board[next_box_position[0]][next_box_position[1]]

            # Box can be pushed if there is floor or goal behind it
            if next_box_obstacle in [GameElements.FLOOR.value, GameElements.GOAL.value]:
                box_index = self.box_positions.index(next_player_position)
                self.box_positions[box_index] = next_box_position
                self.board[self.player_position[0]][self.player_position[1]] = GameElements.FLOOR.value
                self.player_position = next_player_position
                
            # There is a wall or another box behind the box, so it cannot be pushed    
            else:
                return
        # Next position is floor or goal
        elif next_player_obstacle in [GameElements.FLOOR.value, GameElements.GOAL.value]:
            self.board[self.player_position[0]][self.player_position[1]] = GameElements.FLOOR.value 
            self.player_position = next_player_position

        else:
            print("ERROR")
            assert(0)
        self.redraw_board()

    # POST: Returns the position of the player after a move
    def adjacent_position(self, position, move=None):
        if move is None:
            move = self.current_move

        move_dict = {"w": (-1, 0), "a": (0, -1), "s": (1, 0), "d": (0, 1)}

        delta_x, delta_y = move_dict.get(move, (0, 0))

        new_position = [position[0] + delta_x, position[1] + delta_y]
        
        return new_position

    # POST: Updates the game status:
    # Game is won if all boxes are on goals and the number of turns is less than the maximum number of turns
    # otherwise game is lost if the number of turns is greater than the maximum number of turns
    def update_game_status(self):
        if(sorted(self.box_positions) == sorted(self.goal_positions) and self.turn <= self.max_number_of_turns):
                self.end = 1
                self.reward = 1
                if not self.disable_prints:
                    print("WIN!")
        elif self.turn > self.max_number_of_turns:
            self.end = 1
            if not self.disable_prints:
                print("LOSE!")

    # POST: Returns the features of the state if action were taken, without actually changing the state of the game
    # is used for the RL agent to compute the value of the next state
    def step(self, action, gamma):
        
        board = deepcopy(self.board)
        player_position = deepcopy(self.player_position)
        box_positions = deepcopy(self.box_positions)
        
        next_player_position = self.adjacent_position(player_position, move=action)
        next_player_obstacle = board[next_player_position[0]][next_player_position[1]]
        
        # Player runs into a wall
        if next_player_obstacle == GameElements.WALL.value:
            return
        # Player runs into a box
        elif next_player_obstacle in [GameElements.BOX.value, GameElements.BOX_ON_GOAL.value]:
            next_box_position = self.adjacent_position(next_player_position, move=action)
            next_box_obstacle = board[next_box_position[0]][next_box_position[1]]

            # Box can be pushed if there is floor or goal behind it
            if next_box_obstacle in [GameElements.FLOOR.value, GameElements.GOAL.value]:
                box_index = box_positions.index(next_player_position)
                box_positions[box_index] = next_box_position
                board[player_position[0]][player_position[1]] = GameElements.FLOOR.value
                player_position = next_player_position
                
            # There is a wall or another box behind the box, so it cannot be pushed    
            else:
                return

        elif next_player_obstacle in [GameElements.FLOOR.value, GameElements.GOAL.value]:
            board[player_position[0]][player_position[1]] = GameElements.FLOOR.value 
            player_position = next_player_position

        else:
            print("ERROR")
            assert(0)
        
        
        self.redraw_board(board=board, player_position=player_position, box_positions=box_positions)
        targets = self.targets(box_positions=box_positions)
        return [targets, self.distance(player_position=player_position, box_positions=box_positions, board=board), self.gamma1(gamma=gamma), self.gamma2(gamma=gamma, box_positions=box_positions), self.connectivity(board=board)], 1 if targets == 1 and self.turn + 1 <= self.max_number_of_turns else 0, 1 if targets == 1 or self.turn + 1> self.max_number_of_turns else 0
   
    """
    compute features needed for the state feed into the RL agent
    """
    def targets(self, box_positions):
        return len(set(map(tuple, box_positions)).intersection(set(map(tuple,self.goal_positions))))/len(self.box_positions)
    
    def gamma1(self, gamma):
        return pow(gamma, len(self.goal_positions))

    def gamma2(self, gamma, box_positions=None):
        if box_positions is None:
            box_positions = self.box_positions
        number_of_boxes_on_goal = self.targets(box_positions=box_positions) * len(self.goal_positions)
        return pow(gamma, len(self.box_positions) - number_of_boxes_on_goal)
   
    # TODO: get something more sophisticated here: taking into account the player movement when he goes from box to box
    # current idea: model problem as assignment problem (the assumption that the graph is bipartite fully connected might be violated for example:
    #   #######
    #   #.$@$.#
    #   ####### )
    # Nevertheless we use BFS to compute the pairwise distances (ignoring other boxes and the player, only worrying about the walls themselves) and then we use the Hungarian algorithm to solve the assignment problem

    def distance(self, player_position, box_positions, board):
        if board is None:
            board = self.board
        if box_positions is None:
            box_positions = self.box_positions
        cost_matrix = self.get_pairwise_distances(box_positions=box_positions, board=board)

        # using the Hungarian algorithm to solve the assignment problem
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        # Calculate the minimum cost based on the assignment
        min_cost = sum([cost_matrix[row_ind[i]][col_ind[i]] for i in range(len(row_ind))])
        # need to add a component that gives distance between player and next box
        
        player_distance  = self.bfs(player_position, self.find_elements(GameElements.BOX.value, board=board), board=board)
        if len(player_distance) == 0:
            return min_cost
        return min_cost + min(player_distance.values())

    # POST: Returns a matrix that contains the pairwise distances between the boxes and goals:
    # distance[i][j] is the distance between the i-th box and the j-th goal
    def get_pairwise_distances(self, box_positions, board):
        assert(len(box_positions) == len(self.goal_positions))
        size = len(box_positions)
        
        distances = [[0 for _ in range(size)] for _ in range(size)]
        for i in range(size):
            box_distances = self.bfs(box_positions[i], self.goal_positions, board=board)
            for j in range(size):
                distances[i][j] = box_distances[(self.goal_positions[j][0], self.goal_positions[j][1])]
        
        return distances
    
    # POST: Returns a dictionary that contains the distances between the start and the end positions, where the keys are the end positions and the values the distances
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
                        if board[new_x][new_y] in [GameElements.FLOOR.value, GameElements.GOAL.value, GameElements.BOX.value, GameElements.BOX_ON_GOAL.value, GameElements.PLAYER.value, GameElements.PLAYER_ON_GOAL.value]:
                            queue.append((new_x, new_y))
                            visited[new_x][new_y] = True
            step += 1
        return distance 
    
    # POST: Returns the number of connected components in the board
    # Here a connected component is a component in which the player can move without pushing a box
    def connectivity(self, board):
        connected_components = 0
        floor = self.find_elements(GameElements.FLOOR.value, board=board)
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
                    if not visited[new_x][new_y] and board[new_x][new_y] in [GameElements.FLOOR.value, GameElements.GOAL.value, GameElements.PLAYER.value, GameElements.PLAYER_ON_GOAL.value]:
                        queue.append((new_x, new_y))

        return connected_components # we want this to be normalized maybe this will do it, seems unlikely that board has more than 10 connected components?
    def legal_moves(self):
        legal_moves = {"w": True, "a": True, "s": True, "d": True}
        for move in legal_moves:
            next_player_position = self.adjacent_position(self.player_position, move=move)
            next_player_obstacle = self.board[next_player_position[0]][next_player_position[1]]
            if next_player_obstacle == GameElements.WALL.value:
                legal_moves[move] = False
            if next_player_obstacle in [GameElements.BOX.value, GameElements.BOX_ON_GOAL.value]:
                next_box_position = self.adjacent_position(next_player_position, move=move)
                next_box_obstacle = self.board[next_box_position[0]][next_box_position[1]]
                if next_box_obstacle in [GameElements.WALL.value, GameElements.BOX.value, GameElements.BOX_ON_GOAL.value]:
                    legal_moves[move] = False
        return [key for key, value in legal_moves.items() if value is True]       
    # POST: returns the state of the game
    def state(self, gamma):
        return [self.targets(box_positions=self.box_positions), self.distance(player_position=self.player_position, box_positions=self.box_positions, board=self.board), self.gamma1(gamma), self.gamma2(gamma), self.connectivity(board=self.board)], self.reward, self.end


class ReverseGame(Game):
    def __init__(self, game: Game, disable_prints=True):
        super().__init__(level_id=game.level_id)
        self.disable_prints = disable_prints
        # remove player from board:
        
        self.board = self.reverse_board(self.board)
        self.max_number_of_turns = 50
        
        # Initialize the game elements
        self.player_position = self.find_element([GameElements.PLAYER.value, GameElements.PLAYER_ON_GOAL.value])
        self.box_positions = sorted(self.find_elements([GameElements.BOX.value, GameElements.BOX_ON_GOAL.value]))
        self.goal_positions = sorted(self.find_elements([GameElements.PLAYER_ON_GOAL.value, GameElements.BOX_ON_GOAL.value, GameElements.GOAL.value]))
        
    # POST: Returns the board where all boxes are placed on goals and the player is set to a random floor position
    def reverse_board(self, board):
        
        board = deepcopy(board)
        player_position = self.find_element([GameElements.PLAYER.value, GameElements.PLAYER_ON_GOAL.value], board=board)
        box_positions = self.find_elements([GameElements.BOX.value, GameElements.BOX_ON_GOAL.value], board=board)
        goal_positions = self.find_elements([GameElements.GOAL.value, GameElements.BOX_ON_GOAL.value, GameElements.PLAYER_ON_GOAL.value], board=board)
        
        board[player_position[0]][player_position[1]] = GameElements.FLOOR.value
        
        # set remove box from board:
        for box in box_positions:
            board[box[0]][box[1]] = GameElements.FLOOR.value
        
        # place WALLs on goals so that the interior excludes the goals
        for goal in goal_positions:
            board[goal[0]][goal[1]] = GameElements.WALL.value
        
        interior = self.find_interior(board=board)
        self.player_position = random.choice(self.find_elements(GameElements.FLOOR.value, interior))
        
        for goal in goal_positions:
            board[goal[0]][goal[1]] = GameElements.GOAL.BOX_ON_GOAL.value
        
        board[self.player_position[0]][self.player_position[1]] = GameElements.PLAYER.value
        return board

    def load_microban_level(self, level_id):
        return self.reverse_level(super().load_microban_level(level_id))

    def update_game_status(self):
        if(self.targets(box_positions=self.box_positions) == 0 and self.turn <= self.max_number_of_turns):
                if self.disable_prints == False:
                    print("WIN!")
                self.reward = 1
                self.end = 1
        elif self.turn > self.max_number_of_turns:
            if self.disable_prints == False:
                print("LOSE!")
            self.reward = 0
            self.end = 1

    def behind_player(self, position, move=None):
        if move is None:
            move = self.current_move

        move_dict = {"w": (1, 0), "a": (0, 1), "s": (-1, 0), "d": (0, -1)}

        delta_x, delta_y = move_dict.get(move, (0, 0))

        new_position = [position[0] + delta_x, position[1] + delta_y]
        
        return new_position

    def update_positions(self):
        next_player_position = self.adjacent_position(self.player_position)
        next_player_obstacle = self.board[next_player_position[0]][next_player_position[1]] # TODO: find cleaner expression for this
        
        # Next position is floor or goal
        if next_player_obstacle in [GameElements.FLOOR.value, GameElements.GOAL.value]:
            # restore flied under player
            self.board[self.player_position[0]][self.player_position[1]] = GameElements.FLOOR.value
            
            position_behind_player = self.behind_player(self.player_position)
            # pull box if there is one
            if position_behind_player in self.box_positions:
                box_index = self.box_positions.index(position_behind_player)
                self.box_positions[box_index] = self.player_position
                # restore field under box
                self.board[position_behind_player[0]][position_behind_player[1]] = GameElements.FLOOR.value
                
            self.player_position = next_player_position
            self.redraw_board()

    def legal_moves(self):
        legal_moves = {"w": False, "a": False, "s": False, "d": False}
        for move in legal_moves:
            next_player_position = self.adjacent_position(self.player_position, move=move)
            next_player_obstacle = self.board[next_player_position[0]][next_player_position[1]]
            if next_player_obstacle == GameElements.FLOOR.value:
                legal_moves[move] = True
        return [key for key, value in legal_moves.items() if value is True]

    
    def step(self, action, gamma):
        board = deepcopy(self.board)
        player_position = deepcopy(self.player_position)
        box_positions = deepcopy(self.box_positions)
        
        next_player_position = self.adjacent_position(self.player_position, move=action)
        next_player_obstacle = self.board[next_player_position[0]][next_player_position[1]] # TODO: find cleaner expression for this
        
        # Next position is floor or goal
        if next_player_obstacle in [GameElements.FLOOR.value, GameElements.GOAL.value]:
            # restore flied under player
            board[player_position[0]][player_position[1]] = GameElements.FLOOR.value
            
            position_behind_player = self.behind_player(player_position, move=action)
            # pull box if there is one
            if position_behind_player in box_positions:
                box_index = box_positions.index(position_behind_player)
                box_positions[box_index] = player_position
                # restore field under box
                board[position_behind_player[0]][position_behind_player[1]] = GameElements.FLOOR.value
                
            player_position = next_player_position
        self.redraw_board(board=board, player_position=player_position, box_positions=box_positions)
        targets = self.targets(box_positions=box_positions)
        
        return [targets, self.distance(player_position=player_position, box_positions=box_positions, board=board), self.gamma1(gamma=gamma), self.gamma2(gamma=gamma, box_positions=box_positions), self.connectivity(board=board)], 1 if targets == 0 and self.turn + 1 <= self.max_number_of_turns else 0, 1 if targets == 0 or self.turn + 1 > self.max_number_of_turns else 0
     
    # POST: Returns the positions form which boxes can be pulled, returns empty list if no box can be pulled
    def box_movable(self, box_positions, board):
        height = len(board)
        width = len(board[0])
        pullabel_positions = []
        allowed_positions = [GameElements.FLOOR.value, GameElements.GOAL.value, GameElements.PLAYER.value, GameElements.PLAYER_ON_GOAL.value]
        for box_position in box_positions:
            if box_position[0] - 2 >= 0:
                if board[box_position[0] - 1][box_position[1]] in allowed_positions and board[box_position[0] - 2][box_position[1]] in allowed_positions:
                    pullabel_positions.append([box_position[0]-1, box_position[1]])
            if box_position[0] + 2 < height:
                if board[box_position[0] + 1][box_position[1]] in allowed_positions and board[box_position[0] + 2][box_position[1]] in allowed_positions:
                    pullabel_positions.append([box_position[0]+1, box_position[1]])
            if box_position[1] - 2 >= 0:
                if board[box_position[0]][box_position[1] - 1] in allowed_positions and board[box_position[0]][box_position[1] - 2] in allowed_positions:
                    pullabel_positions.append([box_position[0], box_position[1]-1])
            if box_position[1] + 2 < width:
                if board[box_position[0]][box_position[1] + 1] in allowed_positions and board[box_position[0]][box_position[1] + 2] in allowed_positions:
                    pullabel_positions.append([box_position[0], box_position[1]+1])

        return pullabel_positions
            
    def distance(self,player_position, box_positions, board):
        """
        # Manhattan distance from player to all boxes that are not on goal
        if self.targets(box_positions=box_positions) == 0:
            return 0
        else:
            boxes_on_goal = self.find_elements(GameElements.BOX_ON_GOAL.value, board=board)
            return sum([abs(player_position[0]-box_on_goal[0]) + abs(player_position[1]-box_on_goal[1]) for box_on_goal in boxes_on_goal])
        """
        
        # return distance to next box that is not on goal
        if self.targets(box_positions=box_positions) == 0:
            return 0
        else:
            # find next box that can be moved:
            boxes_on_goal = self.find_elements(GameElements.BOX_ON_GOAL.value, board=board)
            movable_box = self.box_movable(boxes_on_goal, board)
            if len(movable_box) == 0:
                return -1 # don't know if this is a good idea
            # TODO: it might happen that the player is not able to reach the box, in this case we should return -1
            distance = self.bfs(start=player_position, end=movable_box, board=board)
            if len(distance) == -1:
                return -1
            else :
                return min(distance.values())
        

if __name__ == "__main__":
    Wearhouse = Game(1, disable_prints=False)
    
    print("---")
    reversed_Wearhouse = ReverseGame(Wearhouse, disable_prints=False)
    print("---")
    reversed_Wearhouse.play()
    assert 0