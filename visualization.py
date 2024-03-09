import pygame
import sys
from game import Game
from reverse_game import ReverseGame
class Engine:
    def __init__(self, game):
        self.game = game
        
    # Function to draw the board
    def draw_board(self, surface, board, tile_size, wall_image, goal_image):
        board_width = len(board[0]) * tile_size
        board_height = len(board) * tile_size
        offset_x = (surface.get_width() - board_width) // 2
        offset_y = (surface.get_height() - board_height) // 2

        for y, row in enumerate(board):
            for x, char in enumerate(row):
                rect_x = x * tile_size + offset_x
                rect_y = y * tile_size + offset_y
                if char == '#':
                    surface.blit(wall_image, (rect_x, rect_y))
                elif char == '.':
                    surface.blit(goal_image, (rect_x, rect_y))
                else:
                    # Define colors for other elements            
                    color = {
                        '@': (0, 120, 255),    # Player color (blue)
                        '$': (255, 128, 0),    # Box color (orange)
                        ' ': (0, 0, 0),  # Floor color (gray)
                        '*': (255, 215, 0),    # Box on goal color (yellow)
                        '+': (0, 255, 120)  
                    }.get(char, (0, 0, 0))  # Default to floor color if unknown
                    pygame.draw.rect(surface, color, pygame.Rect(rect_x, rect_y, tile_size, tile_size))

    def initialize_pygame(self, window_title, window_size):
        pygame.init()
        screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)
        pygame.display.set_caption(window_title)
        return screen

    def load_images(self, tile_size, wall_image_path, goal_image_path):
        wall_image = pygame.transform.scale(pygame.image.load(wall_image_path), (tile_size, tile_size))
        goal_image = pygame.transform.scale(pygame.image.load(goal_image_path), (tile_size, tile_size))
        return wall_image, goal_image

    def handle_resize(self, screen, game):
        window_size = screen.get_size()
        tile_size = min(window_size[0] // len(game.board[0]), window_size[1] // len(game.board))
        font = pygame.font.Font(None, tile_size)
        return tile_size

    def handle_key_events(self, event, game):
        if event.key in [pygame.K_UP, pygame.K_w]:
            self.game.play(moves="w", gamma=1)
            self.game.print_board()
        elif event.key in [pygame.K_DOWN, pygame.K_s]:
            self.game.play(moves="s", gamma=1)
            self.game.print_board()
        elif event.key in [pygame.K_LEFT, pygame.K_a]:
            self.game.play(moves="a", gamma=1)
            self.game.print_board()
        elif event.key in [pygame.K_RIGHT, pygame.K_d]:
            self.game.play(moves="d", gamma=1)
            self.game.print_board()
        return game

    def visualize(self, game):
        # Initialize Pygame
        screen = self.initialize_pygame("Sokoban Game", (640, 480))
    
        tile_size = min(screen.get_width() // len(game.board[0]), screen.get_height() // len(game.board))
        font = pygame.font.Font(None, 36)
        
        # Load images
        wall_image, goal_image = self.load_images(tile_size, 'images/wall.png', 'images/target.png')

        # Main game loop
        running = True
        # Main loop
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    # Handle window resize
                    screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                    tile_size = self.handle_resize(screen, game)
                    wall_image, goal_image = self.load_images(tile_size, 'images/wall.png', 'images/target.png')

                elif event.type == pygame.KEYDOWN:
                    self.handle_key_events(event, game)

            # Clear the screen
            screen.fill((0, 0, 0))

            # Draw the game board
            self.draw_board(screen, game.board, tile_size, wall_image, goal_image)

            # Update the display
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py arg1 arg2")
    else:
        mode = sys.argv[1]
        level_id = sys.argv[2]
        if mode == "game":
            game = Game(level_id=int(level_id))
            engine = Engine(game)
            engine.visualize(game)
        else:
            game = ReverseGame(Game(level_id=len(level_id)))
            engine = Engine(game)
            engine.visualize(game)
