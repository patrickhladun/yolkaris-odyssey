from art import text2art
from utils import (text, paragraph, add_space, clear_terminal, ask_user,
                   loading, color_error)
from game.game_manager import game_manager
from game.characters import Player
from game.locations import (Location, Yolkaris, Mystara, Luminara,
                            game_one, game_two)
from game.items import Book, Spaceship, Special
from game.interactions import Interaction


def game_intro() -> None:
    """
    Displays the game intro.
    """
    yolkaris = text2art("Yolkaris", font="dos_rebel", chr_ignore=True)
    odyssey = text2art("Odyssey", font="dos_rebel", chr_ignore=True)
    clear_terminal()
    text(yolkaris)
    text(odyssey)
    text("Welcome to Yolkaris Odyssey, a text-base"
         " adventure game.", delay=0.1)
    text("Coded and designed by Patrick Hladun.", delay=0.1, space=1)
    ask_user(prompt_type='continue',
             prompt='Press enter to start the game: ', space=1)


def show_help() -> None:
    """
    Displays the available commands.
    """
    text("Available Commands:", space=1)

    text("  north      - Move North (up)", delay=0.1)
    text("  south      - Move South (down)", delay=0.1)
    text("  east       - Move East (right)", delay=0.1)
    text("  west       - Move West (left)", delay=0.1, space=1)

    text("  map        - Show the map", delay=0.1)
    text("  search     - Search the area for items", delay=0.1)
    text("  help       - Show available commands", delay=0.1)
    text("  inventory  - Show inventory", delay=0.1)
    text("  potion     - Use a potion", delay=0.1)
    text("  stats      - Show player stats", delay=0.1)
    text("  restart    - Restart the game", delay=0.1)
    text(" ")


def reset_game(game_instance=None):
    """
    Resets the game.
    """
    # If a game instance is provided, use it; otherwise, create a new one
    if game_instance is None:
        game_instance = Game()
    game_instance.reset_game()
    return game_instance


def select_game_level():
    """
    This method allows the player to select the game level.
    """
    text("Select your Game:", delay=0.2, space=1)
    text("   1. The Broken Clock", delay=0.2)
    text("   2. The Dark Dust", delay=0.2, space=1)
    return ask_user(prompt_type="game", numbers=['1', '2'])


def inspect_inventory_item(item):
    """
    Inspects an item in the player's inventory.
    """
    name = item.name
    description = item.description
    add_space()
    paragraph(f"{name}", space=1)
    paragraph(f"{description}", space=1)


class Game:
    """
    This is the main class for the game.
    """

    def __init__(self) -> None:
        """
        Initializes the game.
        """
        self.interaction = Interaction(self)
        self.location_objects = {}
        self.current_location = 0
        self.game_over = False
        self.player = None

    def setup_game(self):
        """
        This method sets up the game.
        """
        game_intro()
        self.create_player()
        clear_terminal()
        text(f"Hey {self.player.name}!", delay=0.6, space=1)
        paragraph("Welcome to Yolkaris Odyssey! You're about to embark on a"
                  " thrilling adventure as Charlie, a courageous chicken with "
                  "a spirit of exploration. This game takes you to the"
                  " beautiful planet of Yolkaris, where every corner is filled"
                  " with wonder and mystery.", space=1)
        paragraph("Yolkaris Odyssey offers two distinct adventures. The first"
                  " is a concise journey focusing on a single planet, ideal"
                  " for those seeking a swift and engaging experience. The"
                  " second expands the horizon to include two additional"
                  " planets, Mystara and Luminara, each with its own"
                  " challenges and secrets to uncover. Your mission in both"
                  " adventures is to save Yolkaris from imminent threats,"
                  " navigating through dangers and unraveling mysteries to"
                  " ensure the survival of your world.")
        game_level = select_game_level()
        self.setup_areas(game_level)
        clear_terminal()
        loading(['Generating game', '.', '.', '.', '.', '.',
                 '.', '.'], 'Game generated')
        loading(['Starting game', '.', '.', '.', '.'])
        self.assign_player_to_location()
        self.current_location = 0
        starting_location = self.get_current_location()
        starting_location.check_for_interaction((0, 0), self.player)
        self.display_map()

    def start_game(self) -> None:
        """
        This is the main game loop.
        """
        while not self.game_over:
            self.choose_action()

    def setup_areas(self, level) -> None:
        """
        Sets up the areas in the game.
        """
        if level == 1:

            self.location_objects = {
                "Yolkaris": Yolkaris(
                    game_one["yolkaris_size"],
                    game_one["yolkaris_areas"],
                )
            }

        elif level == 2:

            self.location_objects = {
                "Yolkaris": Yolkaris(
                    game_two["yolkaris_size"],
                    game_two["yolkaris_areas"],
                    game_two["yolkaris_travel"]
                ),
                "Mystara": Mystara(
                    game_two["mystara_size"],
                    game_two["mystara_areas"],
                    game_two["mystara_travel"]
                ),
                "Luminara": Luminara(
                    game_two["luminara_size"],
                    game_two["luminara_areas"],
                    game_two["luminara_travel"]
                )
            }

    def create_player(self) -> None:
        """
        This creates the player.
        """
        while True:
            username = ask_user(
                prompt_type=None, prompt="Please enter your username: ")
            if 3 <= len(username) <= 24 and username.isalnum() and "_" \
                    not in username:
                self.player = Player(
                    name=username,
                    health=100,
                    attack=15,
                    defense=10,
                    potions=[],
                    inventory=[]
                )
                break
            else:
                paragraph("Invalid username. It should be between 3 to 24 "
                          "characters ,contain only letters and numbers, and "
                          "no underscores.",
                          color=color_error,
                          )

    def show_player_stats(self) -> None:
        """
        This method displays the player's stats.
        """
        # Retrieve the player object and current location object
        player = self.player

        # Display player's basic stats
        add_space()
        attack = player.attack + player.weapon.attack if player.weapon \
            else player.attack
        defense = player.defense + player.armour.defense if player.armour \
            else player.defense
        text(f"Player {player.name}:")
        text(
            f"Health: {player.health}, Attack: {attack}, Defense: {defense}")

        #####
        # Not sure how to properly break these functions
        #####
        armour = player.armour.name if player.armour else "None"
        weapon = player.weapon.name if player.weapon else "None"
        armour_defense = '- adds ' + str(player.armour.defense) \
                         + ' to Defense' if player.armour else ''
        weapon_attack = '- adds ' + str(player.weapon.attack) \
                        + ' to Attack' if player.weapon else ''
        text(f"Armour: {armour} {armour_defense}")
        text(f"Weapon: {weapon} {weapon_attack}")

        # potions count
        potions_count = len(player.potions)
        text(f"Potions: {potions_count}")

        items_count = len(player.inventory)
        text(f"Inventory: {items_count}")
        self.location_and_position()

    def choose_action(self) -> None:
        """
        Displays the available actions and prompts the player to
        choose an action. The method then calls the appropriate method based on 
        the player's choice.
        """

        action = ask_user(prompt=">> ")
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
        elif action == "contents":  # used for debugging purposes only
            self.show_location_contents()
        elif action in ["search", "s"]:
            self.search_current_area()
        elif action in ["inventory", "i"]:
            self.show_inventory()
        elif action in ["potion", "potions", "p"]:
            self.select_potion()
        elif action == "restart":
            game_manager.reset_game()
        else:
            text("Invalid command. Use 'help' to view available commands.",
                 color=color_error)

    def search_current_area(self):
        """
        Searches the current area for items.
        """
        current_location = self.get_current_location()
        current_location.search_area(self.player)

    def get_current_location(self) -> Location:
        """
        Retrieves the current location object based on the player's position.

        This method accesses the `location_objects` dictionary using the
        `current_location` index, which represents the player's current
        location

        Returns the current location object where the player is at present.
        """
        # Retrieve the name of the current location based on the player's
        # position
        current_location_name = list(self.location_objects.keys())[
            self.current_location
        ]
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

    def location_and_position(self) -> None:
        """
        This method displays the current location and the player's position.
        """
        current_location = self.get_current_location()
        area_name = current_location.get_area_name_by_position(
            current_location.player_position)
        text(f"{current_location.name} - {area_name}", space=1)

    def display_map(self) -> None:
        """
        This method displays the map of the current location.
        """
        add_space()
        self.location_and_position()
        current_location = self.get_current_location()
        current_location.display_map()

    def update_player_position(self, dx: int, dy: int) -> None:
        """
        Updates the player's position in the current location.
        dx: int - The change in the x-axis
        dy: int - The change in the y-axis
        """
        # Retrieve the current location object
        current_location = self.get_current_location()

        # Update previous position before changing the current position
        current_location.player_prev_position = \
            current_location.player_position

        # Calculate the new position
        new_position = (current_location.player_position[0] + dx,
                        current_location.player_position[1] + dy)

        # Check if the new position is valid
        if current_location.is_valid_position(new_position):
            current_location.player_position = new_position
            current_location.check_for_interaction(new_position, self.player)
        else:
            text("You can't move in that direction.", color=color_error)

    def move_north(self) -> None:
        """
        Moves the player north.
        """
        self.update_player_position(0, -1)

    def move_south(self) -> None:
        """
        Moves the player south.
        """
        self.update_player_position(0, 1)

    def move_east(self) -> None:
        """
        Moves the player east.
        """
        self.update_player_position(1, 0)

    def move_west(self) -> None:
        """
        Moves the player west.
        """
        self.update_player_position(-1, 0)

    def show_location_contents(self):
        """
        Displays the contents of the current location.
        """
        current_location = self.get_current_location()
        current_location.print_contents()

    def show_inventory(self):
        """
        Displays the player's inventory and prompts the player to interact with
        an item in the inventory."""
        if not self.player.inventory:
            text("Your inventory is empty.")
            return

        add_space()
        text("Your inventory contains:", space=1)
        for index, item in enumerate(self.player.inventory, start=1):
            name = item.name
            text(f"{index}. {name}")
        add_space()
        prompt = "Select an item number to interact with, " \
                 "or type '0' to cancel: "
        choices = [str(i) for i in range(1, len(self.player.inventory) + 1)]
        choice = ask_user("number", numbers=choices, prompt=prompt)
        try:
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(self.player.inventory):
                self.interact_with_inventory_item(choice_index)
            elif choice_index == -1:
                text("Exiting inventory.")
            else:
                text("Invalid choice.")
        except ValueError:
            text("Invalid input. Please enter a number.")

    def interact_with_inventory_item(self, index):
        """
        Interacts with an item in the player's inventory.
        """
        item = self.player.inventory[index]
        name = item.name
        add_space()
        text(f"You selected {name}.", space=1)

        action = ask_user("item")
        if action.lower() in ['use', 'u']:
            self.use_inventory_item(item)
        elif action.lower() in ['inspect', 'i']:
            inspect_inventory_item(item)
        elif action == '0':
            text("Exiting inventory.")
        else:
            text("Invalid action.")

    def use_inventory_item(self, item):
        """
        Uses an item in the player's inventory.
        """
        name = item.name

        if isinstance(item, Book):
            text(f"You have read the {name}.")
            self.interaction.print_story_line(item.story_line)
        elif isinstance(item, Spaceship):
            self.travel_to_new_location()
        elif isinstance(item, Special):
            self.interaction.print_story_line(item.story_line)

    def travel_to_new_location(self):
        """
        Travels to a new location.
        """
        # Initial locations
        base_destinations = {'Yolkaris': ['Mystara'], 'Mystara': [
            'Yolkaris'], 'Luminara': ['Yolkaris', 'Mystara']}
        special_item_name = "Holographic Cosmos Codex"

        current_location = self.get_current_location()
        add_space()
        text("Select a location to travel to:", space=1)

        # Check if the player has the special item and adjust available
        # locations accordingly
        has_special_item = any(
            item.name == special_item_name for item in self.player.inventory
        ) if self.player.inventory else False

        if has_special_item and current_location.name == 'Mystara':
            available_destinations = base_destinations[current_location.name] \
                                     + ['Luminara']
        else:
            available_destinations = base_destinations[current_location.name]

        # List available locations to travel to
        for index, location in enumerate(available_destinations, start=1):
            text(f"{index}. {location}")

        add_space()

        # Get the user's choice
        numbers = [str(i) for i in range(1, len(available_destinations) + 1)]
        choice = ask_user("number",
                          prompt="Where do you want to go? (type '0' to quit)",
                          numbers=numbers)

        if choice == 0:
            add_space(1)
            paragraph("Charlie chose to stay grounded this time. With a swift "
                      "gesture, he watched the spaceship shrink into a small "
                      "egg, which he then carefully tucked into his pocket.",
                      space=1)
            return

        selected_location_name = available_destinations[int(choice) - 1]

        # Find the index of the selected location in the original
        # locations list
        self.current_location = ['Yolkaris', 'Mystara',
                                 'Luminara'].index(selected_location_name)

        new_location = self.get_current_location()
        new_location.player_position = (0, 0)
        new_location.player_prev_position = (0, 0)

        add_space()
        current_location.print_travel_story_line('from')
        loading([f'{current_location.name} ', '* ', '* ', '* ', '* ',
                 '* ', '* ', '* ', '* ', '* ', '* ', f'{new_location.name}'])
        add_space()
        add_space()
        new_location.print_travel_story_line('to')

        ask_user("continue")

        # Check for interaction in the new location and mark it as visited
        new_location.check_for_interaction((0, 0), self.player)
        new_location.mark_visited((0, 0))

    def select_potion(self):
        """
        Selects a potion from the player's inventory to use.
        """
        if not self.player.potions:
            text("You have no potions.")
            return

        add_space()
        text("Use Potions:", space=1)
        add_space()
        for index, potion in enumerate(self.player.potions, start=1):
            name = potion.name
            health = potion.health
            display_text = f"{index}. {name} (Health: {health})"
            text(display_text)
        add_space()
        prompt = "Select a potion number to use it, or type '0' to cancel: "
        choices = [str(i) for i in range(1, len(self.player.potions) + 1)]
        choice = ask_user("number", numbers=choices, prompt=prompt)
        try:
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(self.player.potions):
                potion = self.player.potions[choice_index]
                self.use_potion(potion)
            elif choice_index == -1:
                text("Exiting potions.")
            else:
                text("Invalid choice.")
        except ValueError:
            text("Invalid input. Please enter a number.")

    def use_potion(self, potion):
        """
        Uses a potion from the player's inventory.
        """
        player = self.player
        max_health = 100
        if player.health == max_health:
            text("You are already at full health.")
        else:
            player.health += potion.health
            if player.health > max_health:
                player.health = max_health
            player.potions.remove(potion)
            text(f"You used a {potion.name}. Your health is "
                 f"now {player.health}.")


if __name__ == "__main__":
    game_manager.start_game()
