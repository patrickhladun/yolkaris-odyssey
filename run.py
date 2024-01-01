from game.config import Config
from art import *
from utils import text, space, clear_terminal

class Character:
    def __init__(self, name, description):
        self.name = name
        self.description = description

class Player(Character):
    def __init__(self, name, description):
        super().__init__(name, description)

class Location:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        
class Yolkaris(Location):
    def __init__(self):
        super().__init__("Yolkaris", "A vibrant planet with diverse ecosystems.")

class Mystara(Location):
    def __init__(self):
        super().__init__("Mystara", "A mysterious planet covered in thick jungles.")

class Luminara(Location):
    def __init__(self):
        super().__init__("Luminara", "A radiant planet with a luminous landscape.")

class Game():
    """
    This is the main class for the game.
    """
    def __init__(self):
        self.location_objects = {
            "Yolkaris": Yolkaris(),
            "Mystara": Mystara(),
            "Luminara": Luminara()
        }
        self.current_location = 0
        self.game_over = False
        self.player = None
        self.config = Config()

    def create_player(self):
        """
        This creates the player.
        """
        text("Welcome to the game! Great adventurer.")
        name = input("What is your name? ")
        description = input("Write about yourself: ")
        self.player = Player(name, description)
        text(f"Hello {self.player.name} {self.player.description}!")
        text("Good luck on your journey!")
        input("Press ENTER to continue ... ")

    def show_player_stats(self):
        player = self.player
        current_location = self.get_current_location()

        # Display player's basic stats
        clear_terminal()
        text("Player Stats:")
        text(f"Name: {player.name}")
        text(f"Description: {player.description}")
    
        text(f"\nCurrent Location: {current_location.name}")
        text(f"{current_location.description}\n")

    def game_title(self):
        """
        This is the main menu.
        """
        yolkaris=text2art("Yolkaris", font="dos_rebel", chr_ignore=True)
        odyssey=text2art("Odyssey", font="dos_rebel", chr_ignore=True)
        print(yolkaris)
        print(odyssey)
        pass

    def intro(self):
        """
        This is the introduction to the game.
        """
        clear_terminal()
        
        text("In the boundless expanse of the cosmos, among a sea of twinkling stars,")
        text("lies Yolkaris - a vibrant and lively planet home to an extraordinary species")
        text("of spacefaring chickens. But now, Yolkaris faces an unprecedented crisis.")
        text("A mysterious and malevolent cosmic dust, known as The Dark Dust, has")
        text("enshrouded the planet in shadow, blocking the essential sunlight and")
        text("disrupting the delicate balance of its ecosystem. The once bright and")
        text("bustling world, a haven of clucking harmony, now teeters on the brink")
        text("of ecological collapse.", delay=0.6, space=1)

        input("Press ENTER to continue ... ")
        clear_terminal()

        text("In this hour of desperation, hope rests on the wings of one brave hero - Clucky.")
        text("Renowned for courage and cleverness, Clucky's destiny is to embark on a quest")
        text("beyond the stars. The mission is dangerous, the stakes are high, and the journey")
        text("will take Clucky to uncharted corners of the galaxy.", delay=0.6, space=1)

        text("As Clucky, you will traverse through cosmic wonders and confront unknown dangers.")
        text("Your quest will lead you to ancient relics and forgotten worlds, where secrets")
        text("of The Dark Dust await to be uncovered. The journey promises challenges, trials,")
        text("and the chance to become the saviour that Yolkaris desperately needs.", delay=0.6, space=1)
        
        input("Press ENTER to continue ... ")
        clear_terminal()

        text("Do you have the courage to step into Clucky's shoes? Are you ready to soar beyond the stars,")
        text("unravel the mystery of The Dark Dust, and find the key to save your beloved planet?")
        text("Your decisions, bravery, and wits will shape the fate of Yolkaris.", delay=0.6, space=1)

        text("Prepare for an odyssey that spans the cosmos - an adventure where your actions will determine")
        text("the survival of an entire world. The journey of Yolkaris Odyssey begins now, and the destiny")
        text("of a planet rests in your wings.", delay=0.6, space=1)

        input("Press ENTER to embark on your journey and become the hero Yolkaris needs... ")

    def show_help(self):
        clear_terminal()
        print("\nAvailable Commands:")
        print("  help      - Show this help message")
        print("  quit      - Quit the game\n")

    def choose_action(self):
        action = input(": ")
        if action == "help":
            self.show_help()
        elif action == "stats":
            self.show_player_stats()
        elif action == "quit":
            self.game_over = True

    def start_game(self):
        """
        This is the main game loop.
        """
        clear_terminal()
        self.game_title()
        text("Welcome to Yolkaris Odyssey! v0.1")
        text("This is a text-based adventure game.")
        input("Press ENTER to start the game ...")
        clear_terminal()
        self.create_player()
        self.intro()
        while not self.game_over:
            self.choose_action()

    def get_current_location(self):
        current_location_name = list(self.location_objects.keys())[self.current_location]
        return self.location_objects[current_location_name]

    def development(self):
        self.create_player()
        while not self.game_over:
            self.choose_action()

if __name__ == "__main__":
    game = Game()
    # game.start_game()
    game.development()