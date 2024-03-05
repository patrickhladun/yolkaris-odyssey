class GameManager:
    def __init__(self):
        self.game = None

    def start_game(self):
        """
        Initializes and starts the game.
        """
        # Import Game class here to avoid circular import issues
        from run import Game

        self.game = Game()
        self.game.setup_game()
        self.game.start_game()

    def reset_game(self):
        """
        Resets the game state and starts over.
        """
        self.start_game()


# Create a singleton GameManager instance
game_manager = GameManager()
