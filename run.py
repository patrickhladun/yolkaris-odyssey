# Terminal size is 80 characters wide and 24 rows high

class Game():
    """
    This is the main class for the game.
    """
    def __init__(self):
        self.game_over = False
        self.player = None

    def start_game(self):
        """
        This is the main game loop.
        """
        while not self.game_over:
            print("Welcome to the game!")
            input("Press enter to exit ...")
            self.game_over = True


if __name__ == "__main__":
    game = Game()
    game.start_game()