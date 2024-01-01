import os
import time

from game.config import Config

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
        self.config = Config()

    def create_player(self):
        """
        This creates the player.
        """
        text("Welcome to the game!", self.config.text_delay)
        name = input("What is your name? ")
        description = input("Write about yourself: ")
        self.player = Player(name, description)
        text(f"Welcome {self.player.name}!", self.config.text_delay)

    def intro(self):
        """
        This is the introduction to the game.
        """
        
        text("In the far reaches of the galaxy, nestled among the stars, lies a world")
        text("unlike any other - the planet Yolkaris. A world brimming with mystery and")
        text("adventure, where legends speak of an ancient power hidden deep within its")
        text("vibrant landscapes.", delay=0.6, space=1)
        
        text("You are Clucky, an intrepid space chicken from the distant planet of Aviara.")
        text("Your journey has brought you to Yolkaris on a quest of great importance. The")
        text("fate of your home planet hangs in the balance, threatened by a mysterious")
        text("force known only as The Dark Dust.", delay=0.6, space=1)

        text("The Dark Dust is a cosmic entity that has plagued the galaxy for millennia,")
        text("devouring entire worlds and leaving nothing but darkness in its wake. It is")
        text("said that the only power capable of stopping The Dark Dust is the legendary")
        text("Aurora Orb, a relic of immense power hidden somewhere on Yolkaris.", delay=0.6, space=1)

        text("You must find the Aurora Orb and use its power to save Aviara from certain")
        text("destruction. But you are not alone in your quest. You will be joined by")
        text("your trusty sidekick, Eggy, a small robot with a big heart.", delay=0.6, space=1)

        text("Together, you will explore the vast landscapes of Yolkaris, uncovering its")
        text("secrets and discovering the truth behind the legend of the Aurora Orb.", delay=0.6, space=1)

        text("will you rise to the challenge and become the hero that Aviara needs? Or will")
        text("the secrets of Yolkaris remain locked away forever, shrouded in the shadows")
        text("of the cosmos?", delay=0.6, space=1)
        
        text("The adventure begins now, and the destiny of a world rests in your wings.",space=0)
        text("Good luck!")

    def start_game(self):
        """
        This is the main game loop.
        """
        self.create_player()
        while not self.game_over:
            text("Welcome to the game!")
            input("Press enter to exit ...")
            self.intro()
            input("Press enter to exit ...")
            self.game_over = True

def text(text, delay=0.2, space=0):
    line_space = '\n' * space
    print(text + line_space)
    time.sleep(delay)

def space(space=1,delay=0.2):
    print('\n')
    time.sleep(delay)

if __name__ == "__main__":
    game = Game()
    game.start_game()