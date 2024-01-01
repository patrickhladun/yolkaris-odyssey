from game.config import Config
from art import *
from utils import text, space, clear_terminal


class Character:
    def __init__(self, name) -> None:
        self.name = name


class Player(Character):
    def __init__(self, name) -> None:
        super().__init__(name)


class Location:
    def __init__(self, name: str, description: str, size: tuple) -> None:
        self.name = name
        self.description = description
        self.size = size
        self.map = [[" " for _ in range(size[0])] for _ in range(size[1])]
        self.player_position = (0, 0)
        self.visited = [[False for _ in range(size[0])] for _ in range(size[1])]
        self.mark_visited(self.player_position)

    def display_map(self) -> None:
        print("Map:")
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                if (x, y) == self.player_position:
                    char = " \uff30"  # Player position with space
                elif self.visited[y][x]:
                    char = " \uff4f"  # Dot for visited cells
                else:
                    char = " \uff0a"  # Light dot or space for unvisited cells
                print(char, end="")
            print()  # New line after each row
        print()  # Extra line for spacing

    def mark_visited(self, position) -> None:
        x, y = position
        if 0 <= x < self.size[0] and 0 <= y < self.size[1]:
            self.visited[y][x] = True


    def is_valid_position(self, position) -> bool:
        x, y = position
        return 0 <= x < self.size[0] and 0 <= y < self.size[1]


class Yolkaris(Location):
    def __init__(self) -> None:
        super().__init__("Yolkaris", "A vibrant planet with diverse ecosystems.", (18, 7))


class Mystara(Location):
    def __init__(self) -> None:
        super().__init__("Mystara", "A mysterious planet covered in thick jungles.", (2, 2))


class Luminara(Location):
    def __init__(self) -> None:
        super().__init__("Luminara", "A radiant planet with a luminous landscape.", (2, 2))


def game_title() -> None:
    """
    This is the main menu.
    """
    yolkaris = text2art("Yolkaris", font="dos_rebel", chr_ignore=True)
    odyssey = text2art("Odyssey", font="dos_rebel", chr_ignore=True)
    print(yolkaris)
    print(odyssey)


def show_help() -> None:
    clear_terminal()
    text("Available Commands:", space=1)
    text("  north      - Move North (up)", delay=0.1)
    text("  south      - Move South (down)", delay=0.1)
    text("  east       - Move East (up)", delay=0.1)
    text("  west       - Move West (up)", delay=0.1, space=1)
    text("  help       - Show this help message", delay=0.1)
    text("  quit       - Quit the game", delay=0.1)


def intro() -> None:
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
    text("In this hour of desperation, hope rests on the wings of one brave")
    text("hero - Clucky. Renowned for courage and cleverness, Clucky's destiny is")
    text("to embark on a quest beyond the stars. The mission is dangerous, the")
    text("stakes are high, and the journey will take Clucky to uncharted ")
    text("corners of the galaxy.", delay=0.6, space=1)
    text("As Clucky, you will traverse through cosmic wonders and confront unknown")
    text("dangers. Your quest will lead you to ancient relics and forgotten worlds,")
    text("where secrets of The Dark Dust await to be uncovered. The journey promises")
    text("challenges, trials, and the chance to become the saviour that Yolkaris")
    text("desperately needs.", delay=0.6, space=1)
    input("Press ENTER to continue ... ")
    clear_terminal()
    text("Do you have the courage to step into Clucky's shoes? Are you ready to")
    text("soar beyond the stars, unravel the mystery of The Dark Dust, and find the")
    text("key to save your beloved planet? Your decisions, bravery, and wits will")
    text("shape the fate of Yolkaris.", delay=0.6, space=1)
    text("Prepare for an odyssey that spans the cosmos - an adventure where your")
    text("actions will determine the survival of an entire world. The journey of ")
    text("Yolkaris Odyssey begins now, and the destiny of a planet rests in your wings.", delay=0.6, space=1)

    input("Press ENTER to embark on your journey and become the hero Yolkaris needs... ")


class Game:
    """
    This is the main class for the game.
    """

    def __init__(self) -> None:
        self.location_objects = {
            "Yolkaris": Yolkaris(),
            "Mystara": Mystara(),
            "Luminara": Luminara()
        }
        self.current_location = 0
        self.game_over = False
        self.player = None
        self.config = Config()

    def create_player(self) -> None:
        """
        This creates the player.
        """
        text("Welcome to the game! Great adventurer.")
        name = input("What is your name? ")
        self.player = Player(name)
        text(f"Hello {self.player.name}!")
        text("Good luck on your journey!")

    def show_player_stats(self) -> None:
        player = self.player
        current_location = self.get_current_location()

        # Display player's basic stats
        clear_terminal()
        text("Player Stats:")
        text(f"Name: {player.name}")

        text(f"\nCurrent Location: {current_location.name}")
        text(f"{current_location.description}\n")

    def choose_action(self) -> None:
        action = input(": ")
        if action == "help":
            show_help()
        elif action == "map":
            self.display_map()
        elif action == "north":
            self.move_north()
        elif action == "south":
            self.move_south()
        elif action == "east":
            self.move_east()
        elif action == "west":
            self.move_west()
        elif action == "stats":
            self.show_player_stats()
        elif action == "quit":
            self.game_over = True

    def start_game(self) -> None:
        """
        This is the main game loop.
        """
        clear_terminal()
        game_title()
        text("Welcome to Yolkaris Odyssey! v0.2")
        text("This is a text-based adventure game.")
        input("Press ENTER to start the game ...")
        clear_terminal()
        # Create player
        self.create_player()
        # Assign player to current location
        self.assign_player_to_location()
        # Start game intro
        # intro()
        while not self.game_over:
            self.choose_action()

    def get_current_location(self) -> Location:
        """
        Retrieves the current location object based on the player's position.

        This method accesses the `location_objects` dictionary using the
        `current_location` index, which represents the player's current location

        Returns the current location object where the player is at present.
        """
        # Retrieve the name of the current location based on the player's position
        current_location_name = list(self.location_objects.keys())[self.current_location]
        return self.location_objects[current_location_name]

    def assign_player_to_location(self) -> None:
        """
        Assigns the player to their current location in the game.

        This method updates the current location object to include a reference
        to the player object.
        """
        # Retrieve the current location object
        current_location = self.get_current_location()
        # Assign the player to the current location
        current_location.player = self.player

    def display_map(self) -> None:
        """
        This method displays the map of the current location.
        """
        current_location = self.get_current_location()
        text(f"Current Location: {current_location.name}")
        current_location.display_map()

    def development(self) -> None:
        self.create_player()
        while not self.game_over:
            self.get_current_location()
            self.choose_action()

    def update_player_position(self, dx: int, dy: int) -> None:
        current_location = self.get_current_location()
        x, y = current_location.player_position
        new_position = (x + dx, y + dy)

        if current_location.is_valid_position(new_position):
            current_location.player_position = new_position
            current_location.mark_visited(new_position)
        else:
            print("You can't move in that direction.")

    def move_north(self) -> None:
        self.update_player_position(0, -1)

    def move_south(self) -> None:
        self.update_player_position(0, 1)

    def move_east(self) -> None:
        self.update_player_position(1, 0)

    def move_west(self) -> None:
        self.update_player_position(-1, 0)


if __name__ == "__main__":
    game = Game()
    game.start_game()
    # game.development()
