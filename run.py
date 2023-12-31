import os
import time
# Terminal size is 80 characters wide and 24 rows high

class Character:
    def __init__(self, name, description):
        self.name = name
        self.description = description

class Player(Character):
    def __init__(self, name, description):
        super().__init__(name, description)

class Game():
    """
    This is the main class for the game.
    """
    def __init__(self):
        self.game_over = False
        self.player = None
        self.text_speed = 0.4

    def create_player(self):
        """
        This creates the player.
        """
        print_text("Welcome to the game!", self.text_speed)
        name = input("What is your name? ")
        description = input("Write about yourself: ")
        self.player = Player(name, description)
        print_text(f"Welcome {self.player.name}!", self.text_speed)
        print_text("Good luck!", self.text_speed)

    def start_game(self):
        """
        This is the main game loop.
        """
        self.create_player()
        while not self.game_over:
            print_text("Welcome to the game!", self.text_speed)
            input("Press enter to exit ...")
            self.game_over = True

def print_text(text, delay=0.2):
    print(text)
    time.sleep(delay)

if __name__ == "__main__":
    game = Game()
    game.start_game()