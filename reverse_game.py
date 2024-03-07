from copy import deepcopy
import random
from game import Game

class ReverseGame(Game):
    def __init__(self, game: Game):
        super().__init__(level_id=game.level_id)
        
        # remove player from board:
        self.board, self.interior = self.reverse_level(self.board)
    
    def reverse_level(self, level):

        player_position = self.find_element(self.player, level)
        all_box_positions = self.find_elements(self.box, level) + self.find_elements(self.box_on_goal, level)
        level = deepcopy(level)
        level[player_position[0]][player_position[1]] = self.goal if level[player_position[0]][player_position[1]] == self.player_on_goal else self.floor

        # using self.positions_all_boxes is wrong TODO: fix this
        # set remove box from board:
        for box in all_box_positions:
            level[box[0]][box[1]] = self.goal if level[box[0]][box[1]] == self.box_on_goal else self.floor
        
        # place boxes on goals this does not work for all levels
        goals = self.find_elements(self.goal,level)
        for goal in goals:
            level[goal[0]][goal[1]] = self.box_on_goal

        # TODO: set player in starting position correctly, in some cases this might result in an unsolvable situation or even palcement out of the level (have to solve this using that it is in the same connected component)
        interior = self.find_interior(level)
        self.player_position = random.choice(self.find_elements(self.floor, interior))
        level[self.player_position[0]][self.player_position[1]] = self.player
        self.number_of_boxes_on_goal = len(self.find_elements(self.box_on_goal, level))
        self.total_number_of_boxes = self.number_of_boxes_on_goal

        return level, interior

    def find_interior(self, level):
        # find the interior of the level
        level = deepcopy(level)
        height = len(level)
        width = max([len(level[i]) for i in range(height)])
        interior = [['#' for j in range(width)] for i in range(height)]
        
        # use breadth first search to find the interior
        queue = [self.find_element(self.box_on_goal, level)] if self.find_element(self.box_on_goal, level) else [self.find_element(self.box, level)] # TODO: this will fail for 155 since there are boxes that are isolated
        while queue:
            x, y = queue.pop(0)
            if interior[x][y] == '#':
                interior[x][y] = ' '
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    new_x, new_y = x + dx, y + dy
                    if 0 <= new_x < height and 0 <= new_y < width and level[new_x][new_y] in [self.floor, self.goal, self.box, self.box_on_goal, self.player, self.player_on_goal]:
                        if interior[new_x][new_y] == '#':
                            queue.append((new_x, new_y))
                            level[new_x][new_y] = ';' # mark as visited

        return interior

    def load_microban_level(self, level_id):
        return self.reverse_level(super().load_microban_level(level_id))

    def update_game_status(self):
        if(self.move_changed_smth):
            if(self.number_of_boxes_on_goal == 0):
                print("WIN!")
                self.reward = 10
        elif self.turn > 50:
            print("LOSE!")
            self.reward = 0
        self.move_changed_smth = False

    def behind_player(self, position, move=None):
        if move is None:
            move = self.current_move
        new_position = position[:]
        if move == "w":
            new_position[0] += 1
        elif move == "a":
            new_position[1] += 1
        elif move == "s":
            new_position[0] -= 1
        elif move == "d":
            new_position[1] -= 1
        return new_position

    def update_positions(self):
        next_player_position = self.adjacent_position(self.player_position)
        next_player_obstacle = self.board[next_player_position[0]][next_player_position[1]] # TODO: find cleaner expression for this
        if next_player_obstacle in [self.floor, self.goal]:
            self.move_changed_smth = True
            # restore flied under player
            self.board[self.player_position[0]][self.player_position[1]] = self.goal if self.board[self.player_position[0]][self.player_position[1]] == self.player_on_goal else self.floor
            # move player to new position
            self.board[next_player_position[0]][next_player_position[1]] = self.player_on_goal if self.board[next_player_position[0]][next_player_position[1]] == self.goal else self.player
            position_behind_player = self.behind_player(self.player_position)
            # pull box if there is one
            if self.board[position_behind_player[0]][position_behind_player[1]] in [self.box, self.box_on_goal]:
                # restore field under box
                self.board[position_behind_player[0]][position_behind_player[1]] = self.goal if self.board[position_behind_player[0]][position_behind_player[1]] == self.box_on_goal else self.floor
                if self.board[position_behind_player[0]][position_behind_player[1]] == self.goal:
                    self.number_of_boxes_on_goal -= 1
                # move box to new position
                self.board[self.player_position[0]][self.player_position[1]] = self.box_on_goal if self.board[self.player_position[0]][self.player_position[1]] == self.goal else self.box
                if self.board[self.player_position[0]][self.player_position[1]] == self.box_on_goal:
                    self.number_of_boxes_on_goal += 1
            self.player_position = next_player_position

    def step(self, action):
        board = deepcopy(self.board)
        player_position = deepcopy(self.player_position)
        number_of_boxes_on_goal = self.number_of_boxes_on_goal

        next_player_position = self.adjacent_position(player_position, action)
        next_player_obstacle = board[next_player_position[0]][next_player_position[1]] # TODO: find clearner expression for this
        if next_player_obstacle not in [self.floor, self.goal]:
            pass
        else:
            board[player_position[0]][player_position[1]] = self.goal if board[player_position[0]][player_position[1]] == self.player_on_goal else self.floor
            board[next_player_position[0]][next_player_position[1]] = self.player_on_goal if board[next_player_position[0]][next_player_position[1]] == self.goal else self.player
            position_behind_player = self.behind_player(player_position, action)
            if board[position_behind_player[0]][position_behind_player[1]] in [self.box, self.box_on_goal]:
                board[position_behind_player[0]][position_behind_player[1]] = self.goal if board[position_behind_player[0]][position_behind_player[1]] == self.box_on_goal else self.floor
                if board[position_behind_player[0]][position_behind_player[1]] == self.goal:
                    number_of_boxes_on_goal -= 1
                board[player_position[0]][player_position[1]] = self.box_on_goal if board[player_position[0]][player_position[1]] == self.goal else self.box
                if board[player_position[0]][player_position[1]] == self.box_on_goal:
                    number_of_boxes_on_goal += 1
            player_position = next_player_position


if __name__ == "__main__":
    random.seed(0)
    game = Game(level_id=1)
    reverse_game = ReverseGame(game)
    reverse_game.play()
    reverse_game.play(["d", "d", "d", "d", "w", "d"])