from copy import deepcopy
import random
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
        self.reward = 0
        self.move_changed_smth = False
        self.number_of_boxes_on_goal = len(self.find_elements(self.box_on_goal))
        self.total_number_of_boxes = len(self.find_elements(self.box)) + self.number_of_boxes_on_goal

        # Status of the player:
        self.current_move = None
  
    """
        @classmethod
        def from_game(cls, game):
            # Create a new instance of the class with properties copied from an existing game instance
            return cls(level_id=game.level_id, board=deepcopy(game.board), end=game.end, turn=game.turn, reward=game.reward, move_changed_smth=game.move_changed_smth, number_of_boxes_on_goal=game.number_of_boxes_on_goal, total_number_of_boxes=game.total_number_of_boxes, current_move=game.current_move)

    """
    def load_microban_level(level_id):
        # load microban level, levels are indexed from 1 to 155

        if level_id < 1 or level_id > 155:
            raise ValueError("Level ID must be between 1 and 155 for Microban levels.")
        
        # load the level from the file
        with open(f"levels/microban.txt", "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if line.startswith(f"; {level_id}"):
                    # find next line that starts with ;
                    j = i + 1
                    while not lines[j].startswith(";"):
                        j += 1
                    level = [list(lines[k][:-1]) for k in range(i+2,j-1)]
                    return level


    def random_board(self): # TODO: implement
        return [
            list("#######"),
            list("#     #"),
            list("#@$.. #"),
            list("#   $ #"),
            list("#     #"),
            list("#######")
        ]
    
    def play(self, moves=None):
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
            return self.state()

    def print_board(self, board=None):
        if self.disable_prints:
            return
        
        if board is None:
            board = self.board

        for row in board:
            print("".join(row))

    def input(self):
        while(True):
            user_input = input().strip().lower()
            if user_input in ["w", "a", "s", "d"]:
                self.current_move = user_input
                return
            else:
                print("Invalid input. Please enter 'w', 'a', 's', 'd'")
                return

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

    def update_game_status(self):
        if(self.move_changed_smth):
            if(self.number_of_boxes_on_goal == self.total_number_of_boxes):
                self.end=True
                if self.disable_prints == False:
                    print("WIN!")
        self.move_changed_smth = False
        if self.turn > 100:
            self.end = True
            if self.disable_prints == False:
                print("LOSE!")

    def log_game(self):
        pass

    def load_level(self, level):
        pass

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

    def state(self):
        return self.convert(self.board), self.reward, int(self.end)

    def step(self, action):
        board = deepcopy(self.board)
        player_position = deepcopy(self.player_position)
        number_of_boxes_on_goal = self.number_of_boxes_on_goal

        next_player_position = self.adjacent_position(player_position, action)
        next_player_obstacle = board[next_player_position[0]][next_player_position[1]] # TODO: find clearner expression for this
        if next_player_obstacle == self.wall:
            pass
        
        elif next_player_obstacle in [self.box, self.box_on_goal]:
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
            else:
                pass #TODO: get rid of these pass statements

        elif next_player_obstacle == self.floor:
            board[player_position[0]][player_position[1]] = self.goal if board[player_position[0]][player_position[1]] == self.player_on_goal else self.floor
            board[next_player_position[0]][next_player_position[1]] = self.player
            player_position = next_player_position

        elif next_player_obstacle == self.goal:
            board[player_position[0]][player_position[1]] = self.goal if board[player_position[0]][player_position[1]] == self.player_on_goal else self.floor 
            board[next_player_position[0]][next_player_position[1]] = self.player_on_goal
            player_position = next_player_position
        else:
            print("ERROR")
            assert(0)
        
        reward = 0
        end = 0
        if number_of_boxes_on_goal == self.total_number_of_boxes:
            reward = 10
            end = 1
        return self.convert(board), reward, end


if __name__ == "__main__":
    Wearhouse = Game(15, disable_prints=False)
    Wearhouse.embed()
    Wearhouse.print_board()
    Wearhouse.play()