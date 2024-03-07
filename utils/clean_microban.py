# script to format microban data
from copy import deepcopy

wall = '#'
box = '$'
goal = '.'
player = '@'
floor = ' '
box_on_goal = '*'
player_on_goal = '+'
bedrock = ':'

def find_element(element, board):
        """Find the position of a single element (e.g., the player)"""
        for x, row in enumerate(board):
            for y, char in enumerate(row):
                if char == element:
                    return [x, y]
        return None

def find_interior(level):
        # find the interior of the level
        level = deepcopy(level)
        height = len(level)
        width = max([len(level[i]) for i in range(height)])
        interior = [[bedrock for j in range(width)] for i in range(height)]
        
        # use breadth first search to find the interior
        queue = [find_element(player, level)] if find_element(player, level) else [find_element(player_on_goal, level)]
        while queue:
            x, y = queue.pop(0)
            if interior[x][y] == bedrock:
                interior[x][y] = floor
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    new_x, new_y = x + dx, y + dy
                    if 0 <= new_x < height and 0 <= new_y < width and level[new_x][new_y] in [floor, goal, box, box_on_goal, player, player_on_goal]:
                        if interior[new_x][new_y] == bedrock:
                            queue.append((new_x, new_y))
                            level[new_x][new_y] = ';' # mark as visited

        return interior
def print_board(board):
    for row in board:
        print("".join(row))



with open(f"original_microban.txt", "r") as file:
    transformed = []
    lines = file.readlines()
    h=1
    for i, line in enumerate(lines):
        if line.startswith(f"; {h}"):
            # find next line that starts with ;
            h += 1
            j=i+1
            while not lines[j].startswith(f";"):
                j += 1
            level = [list(lines[k][:-1]) for k in range(i+2,j-1)]
            interior = find_interior(level)
            for i in range(len(interior)):
                for j in range(len(interior[i])):
                    if interior[i][j] != bedrock:
                        interior[i][j] = level[i][j]
                        
             # restore walls (should make this prettier)
            for i in range(len(level)):
                for j in range(len(level[i])):
                    if level[i][j] == wall:
                        interior[i][j] = wall
    
            transformed.append("; " + str(h-1) + "\n")
            transformed.append("\n")
            for row in interior:
                transformed.append("".join(row) + "\n")
            transformed.append("\n")
   
    # save modified lines in a new file
    with open(f"microban.txt", "w") as file:
        for line in transformed:
            file.write(str(line))