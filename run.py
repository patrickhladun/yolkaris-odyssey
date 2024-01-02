from game.config import Config
import random
from art import *
from utils import text, paragraph, space, clear_terminal
from pprint import pprint


class Character:
    def __init__(self, name) -> None:
        self.name = name


class Player(Character):
    def __init__(self, name) -> None:
        super().__init__(name)


class Enemy(Character):
    """
    Initializes an enemy character.
    """

    def __init__(self, name: str, description: str, narration: str, dialogue: str):
        super().__init__(name)
        self.description = description
        self.narration = narration
        self.dialogue = dialogue

    def interact(self, player):
        text(f"{self.name} stand on your way")
        paragraph(self.description)
        paragraph(self.narration)
        paragraph(self.dialogue)
        input('exit the fight')


class Location:
    def __init__(self, name: str, description: str, size: tuple, areas) -> None:
        self.name = name
        self.description = description
        self.size = size
        self.areas = areas if areas else []
        self.player_position = (0, 0)
        self.contents = {}
        self.map = [["" for _ in range(size[0])] for _ in range(size[1])]
        self.visited = [[False for _ in range(size[0])] for _ in range(size[1])]
        self.mark_visited(self.player_position)
        self.randomly_place_elements()

    def place_on_map(self, element, position=None):
        """
        Places an element on the map at the specified position.
        """
        while position is None or position in self.contents:
            position = self.get_random_position()
        self.contents[position] = element

    def randomly_place_elements(self):
        """
        This method randomly places elements in the location.
        """
        for area in self.areas:
            if hasattr(area, 'position') and area.position is not None and self.is_valid_position(area.position):
                if area.position not in self.contents:
                    self.place_on_map(area, area.position)
                else:
                    self.place_on_map(area)
            else:
                self.place_on_map(area)

    def get_random_position(self):
        x = random.randint(0, self.size[0] - 1)
        y = random.randint(0, self.size[1] - 1)
        return (x, y)

    def display_map(self) -> None:
        """
        This method displays the map of the current location.
        """
        print(f"Position: {self.player_position}")
        # pprint(self.map)
        print('Contents')
        pprint(f"{self.contents}", width=135)
        # print('Visited')
        # pprint(f"{self.visited}", width=135)
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                if (x, y) == self.player_position:
                    char = "\033[93m \uff30\033[0m"
                elif self.visited[y][x]:
                    char = "\033[90m \uff4f\033[0m"
                elif (x, y) in self.contents and isinstance(self.contents[(x, y)], Area):
                    char = "\033[92m \uff0a\033[0m"
                else:
                    char = " \uff0a"
                print(char, end="")
            print()
        print()

    def mark_visited(self, position) -> None:
        """
        This method marks the position as visited.
        """
        x, y = position
        if 0 <= x < self.size[0] and 0 <= y < self.size[1]:
            self.visited[y][x] = True

    def is_valid_position(self, position) -> bool:
        """
        This method checks if the position is valid.
        """
        print(f"Checking if position is valid: {position}")  # Diagnostic print
        x, y = position
        return 0 <= x < self.size[0] and 0 <= y < self.size[1]

    def check_for_interaction(self, position):
        if position in self.contents:
            element = self.contents[position]
            if isinstance(element, Area):
                element.interact(self.player)

    def print_contents(self):
        if not self.contents:
            print("There are no items or enemies in this location.")
            return

        clear_terminal()
        print("Contents of the location:")
        for position, element in self.contents.items():
            element_type = type(element).__name__
            element_info = f"{element.name}" if hasattr(element, 'name') else "Unknown"
            print(f"Position {position}: {element_type} - {element_info}")

class Yolkaris(Location):
    def __init__(self) -> None:
        super().__init__("Yolkaris", "A vibrant planet with diverse ecosystems.", (4, 2), yolkaris_areas)


class Mystara(Location):
    def __init__(self) -> None:
        super().__init__("Mystara", "A mysterious planet covered in thick jungles.", (8, 4), mystara_areas)


class Luminara(Location):
    def __init__(self) -> None:
        super().__init__("Luminara", "A radiant planet with a luminous landscape.", (7, 4), luminara_areas)


class Area:
    def __init__(self, name: str, description, narration, dialogue, enemy=None, position=None):
        self.name = name
        self.description = description
        self.narration = narration
        self.dialogue = dialogue
        self.enemy = enemy
        self.position = position

    def interact(self, player):
        clear_terminal()
        paragraph(f"You are visiting {self.name}, {self.description}")
        paragraph(self.narration)
        paragraph(self.dialogue)

        if self.enemy:
            self.enemy.interact(player)


yolkaris_areas = [
    Area(
        name="Enchanted Forest",
        description="A mystical woodland brimming with magical creatures and ancient trees.",
        narration="As you step into the Enchanted Forest, a sense of awe washes over you. The sights and sounds of the "
        "forest are like nothing you've ever experienced. The air feels thick with magic, almost as if you could reach "
        "out and touch it.",
        dialogue="I feel tired; the journey has been so long already. A cup of nice coffee would be a "
        "blessing now. I wonder how folks are doing back home. This seems like a good spot for a quick nap.",
        position=(0, 1),
        enemy=Enemy(
            name='Yorkish',
            description='Nasty busty monster yey',
            narration="This monster will bit you in 5 sec",
            dialogue="I think I should be ok against this one"
        )
    ),
    Area("Lost City Ruins",
         "Ancient structures overrun by time, with remnants of a once-great civilization.",
         "Echoes of the past resonate through the crumbling stone, whispering old secrets.",
         "",
         position=(3, 0),),
    Area("Crystal Caverns",
         "Gleaming crystals illuminate this underground wonder, casting colorful reflections.",
         "The caverns sparkle with a thousand hues, each crystal telling its own ancient story.",
         ""
         ),
    Area("Haunted Graveyard",
         "An eerie graveyard where fog hugs the ground and shadows move in the corner of your eye.",
         "The air here is heavy with unspoken stories, and every grave has its own chilling tale.",
         ""),
]

mystara_areas = [
    Area("Enchanted Forest",
         "A mystical woodland brimming with magical creatures and ancient trees.",
         "Every step in this forest feels like walking through a fairy tale.",
         ""),
]

luminara_areas = [
    Area("Enchanted Forest",
         "A mystical woodland brimming with magical creatures and ancient trees.",
         "Every step in this forest feels like walking through a fairy tale.",
         ""),
]


def game_title() -> None:
    """
    This is the main menu.
    """
    yolkaris = text2art("Yolkaris", font="dos_rebel", chr_ignore=True)
    odyssey = text2art("Odyssey", font="dos_rebel", chr_ignore=True)
    print(yolkaris)
    print(odyssey)


def show_help() -> None:
    """
    This function displays the available commands.
    """
    clear_terminal()
    text("Available Commands:", space=1)
    text("  north      - Move North (up)", delay=0.1)
    text("  south      - Move South (down)", delay=0.1)
    text("  east       - Move East (up)", delay=0.1)
    text("  west       - Move West (up)", delay=0.1, space=1)
    text("  map        - Show the map", delay=0.1)
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
        # Create player object and assign it to the game object
        self.player = Player(name)
        text(f"Hello {self.player.name}!")
        text("Good luck on your journey!")

    def show_player_stats(self) -> None:
        """
        This method displays the player's stats.
        """
        # Retrieve the player object and current location object
        player = self.player
        current_location = self.get_current_location()

        # Display player's basic stats
        clear_terminal()
        text("Player Stats:")
        text(f"Name: {player.name}")
        # Display player's current location
        text(f"\nCurrent Location: {current_location.name}")
        text(f"{current_location.description}\n")

    def choose_action(self) -> None:
        """
        This method displays the available actions and prompts the player to choose
        an action. The method then calls the appropriate method based on the player's
        choice.
        """
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
        elif action == "contents":
            self.show_location_contents()
        elif action == "quit":
            self.game_over = True

    def start_game(self) -> None:
        """
        This is the main game loop.
        """
        clear_terminal()
        game_title()
        text("Welcome to Yolkaris Odyssey! v0.3")
        text("This is a text-based adventure game.")
        # input("Press ENTER to start the game ...")
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
        # Retrieve the current location object
        current_location = self.get_current_location()
        # Display the map of the current location
        text(f"Map of {current_location.name}")
        current_location.display_map()

    def update_player_position(self, dx: int, dy: int) -> None:
        """
        This method updates the player's position in the current location.
        dx: int - The change in the x-axis
        dy: int - The change in the y-axis
        """
        # Retrieve the current location object
        current_location = self.get_current_location()
        # Retrieve the player's current position
        x, y = current_location.player_position
        # Calculate the new position
        new_position = (x + dx, y + dy)

        # Check if the new position is valid
        if current_location.is_valid_position(new_position):
            current_location.player_position = new_position
            current_location.mark_visited(new_position)
            current_location.check_for_interaction(new_position)
        else:
            print("You can't move in that direction.")

    def move_north(self) -> None:
        """
        This method moves the player north.
        """
        self.update_player_position(0, -1)

    def move_south(self) -> None:
        """
        This method moves the player south.
        """
        self.update_player_position(0, 1)

    def move_east(self) -> None:
        """
        This method moves the player east.
        """
        self.update_player_position(1, 0)

    def move_west(self) -> None:
        """
        This method moves the player west.
        """
        self.update_player_position(-1, 0)

    def show_location_contents(self):
        current_location = self.get_current_location()
        current_location.print_contents()

if __name__ == "__main__":
    game = Game()
    game.start_game()
