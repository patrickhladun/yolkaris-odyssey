from game.config import Config
import random
from art import *
from utils import (text, paragraph, add_space, clear_terminal, ask_user,
                   color_light_gray, color_light_blue, color_player,
                   color_neutral, color_error)
from pprint import pprint


class Character:
    def __init__(self, name: str) -> None:
        self.name = name


class Player(Character):
    def __init__(
            self,
            name: str,
            health: int,
            attack: int,
            inventory: list,
            potions: list,
            coins: int,
            defense: int) -> None:
        super().__init__(name)
        self.health = health
        self.attack = attack
        self.defense = defense
        self.inventory = inventory
        self.potions = potions
        self.coins = coins
        self.weapon = None
        self.armour = None


class Enemy(Character):
    """
    Initializes an enemy character.
    """

    def __init__(
        self,
        name: str,
        storyLine: list,
        health: int,
        attack: int,
        defense: int,
    ) -> None:
        super().__init__(name)
        self.storyLine = storyLine
        self.health = health
        self.attack = attack
        self.defense = defense


class Neutral(Character):
    def __init__(self, name, storyLine) -> None:
        super().__init__(name)
        self.storyLine = storyLine


class Interaction:
    def __init__(self, player):
        self.player = player

    def with_area(self, area):
        for line in area.storyLine:
            space = line['space'] if 'space' in line else 1
            color = line['color'] if 'color' in line else None
            if 'clear' in line:
                clear_terminal()
            elif 'text' in line:
                paragraph(line['text'], space=space,  color=color)
            elif 'continue' in line:
                ask_user('continue', space=space)

    def with_enemy(self, enemy, location):
        add_space()
        text(f"{enemy.name} stands in your way, {self.player.name}", space=1)
        for line in enemy.storyLine:
            paragraph(line['text'], space=1)
        text(f"{enemy.name} stats - health: {enemy.health}, attack: {enemy.attack}, "
             f"defense: {enemy.defense}", space=1)
        combat = Combat(self.player, enemy)
        results = combat.to_fight_or_not_to_fight()
        if results == "retreat":
            text("You have retreated from the battle.")
            location.return_to_previous_position()
            return False
        elif results == "won":
            text(f"You have defeated {enemy.name}!")
            return True
        elif results == "lost":
            text(f"You have been defeated by {enemy.name}!")
            text("Game Over!")

    def with_neutral(self, neutral):
        add_space()
        for line in neutral.storyLine:
            space = line['space'] if 'space' in line else 1
            color = line['color'] if 'color' in line else None
            if 'clear' in line:
                clear_terminal()
            elif 'text' in line:
                paragraph(line['text'], space=space,  color=color)
            elif 'continue' in line:
                ask_user('continue')


class Combat:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy

    def combat(self):
        while self.player.health > 0 and self.enemy.health > 0:
            self.player_attack()
            if self.enemy.health <= 0:
                return "won"

            self.enemy_attack()
            if self.player.health <= 0:
                return "lost"

            if self.continue_or_flee():
                break

        return "retreat"

    def to_fight_or_not_to_fight(self):
        if ask_user('combat'):
            result = self.combat()
            return result
        else:
            return "retreat"

    def continue_or_flee(self):
        return ask_user('retreat')

    def player_attack(self):
        player_attack_power = self.calculate_player_attack_power()
        damage = self.calculate_damage(player_attack_power, self.enemy.defense)
        self.enemy.health -= damage
        text(f"You hit the enemy causing {damage} damage.")

    def enemy_attack(self):
        damage = self.calculate_damage(
            self.enemy.attack, self.calculate_player_defense()
        )
        self.player.health -= damage
        text(f"Enemy hits you causing {damage} damage.")

    def calculate_player_attack_power(self):
        base_attack = self.player.attack
        weapon_bonus = self.player.weapon["attack"] if self.player.weapon else 0
        return base_attack + weapon_bonus

    def calculate_player_defense(self):
        base_defense = self.player.defense
        armor_bonus = self.player.armour["defense"] if self.player.armour else 0
        return base_defense + armor_bonus

    def calculate_damage(self, attack, defense):
        return max(
            int(random.uniform(0.5 * attack, attack) -
                random.uniform(0, defense)), 1
        )

    def display_combat_status(self):
        text(f"Player: health:{self.player.health}")
        if self.enemy.health > 0:
            text(f"Enemy: health:{self.enemy.health}", delay=0.3, space=1)


class Location:
    def __init__(self, name: str, description: str, size: tuple, areas: dict) -> None:
        self.name = name
        self.description = description
        self.size = size
        self.areas = areas if areas else []
        self.player_position = (0, 0)
        self.player_prev_position = (0, 0)
        self.contents = {}
        self.map = [["" for _ in range(size[0])] for _ in range(size[1])]
        self.visited = [[False for _ in range(
            size[0])] for _ in range(size[1])]
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
            if (
                hasattr(area, "position")
                and area.position is not None
                and self.is_valid_position(area.position)
            ):
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
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                if (x, y) == self.player_position:
                    char = "\033[93m \uff30\033[0m"
                elif self.visited[y][x]:
                    char = "\033[90m \uff4f\033[0m"
                elif (x, y) in self.contents and isinstance(
                    self.contents[(x, y)], Area
                ):
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
        x, y = position
        return 0 <= x < self.size[0] and 0 <= y < self.size[1]

    def return_to_previous_position(self):
        self.player_position = self.player_prev_position
        area_name = self.get_area_name_by_position(self.player_prev_position)
        text(f"You have returned to the {area_name}.")

    def get_area_name_by_position(self, position):
        area = self.contents.get(position)
        if area and isinstance(area, Area):
            return area.name
        else:
            return "Unknown Area"

    def check_for_interaction(self, position, player):
        if position in self.contents:
            element = self.contents[position]
            if isinstance(element, Area):
                interaction = Interaction(player)
                interaction.with_area(element)

                enemy_defeated = False
                if element.enemy:
                    ask_user(type='continue')
                    enemy_defeated = interaction.with_enemy(
                        element.enemy, self)

                # Start interaction with neutral if no enemy or enemy defeated
                if (not element.enemy or enemy_defeated) and element.neutral:
                    interaction.with_neutral(element.neutral)

    def print_contents(self):
        if not self.contents:
            print("There are no items or enemies in this location.")
            return

        clear_terminal()
        print("Contents of the location:")
        for position, element in self.contents.items():
            element_type = type(element).__name__
            element_info = f"{element.name}" if hasattr(
                element, "name") else "Unknown"
            print(f"Position {position}: {element_type} - {element_info}")

    def search_area(self, player):
        position = self.player_position
        if position in self.contents:
            area = self.contents[position]
            if hasattr(area, "items") and area.items:
                text("You found the following items:", space=1)
                for index, the_item in enumerate(area.items):
                    # Ensure that item_dict has 'item' and 'quantity' keys
                    item = the_item['item']
                    quantity = the_item['quantity']
                    name = item.name
                    text(f"{index + 1}. {name} (Quantity: {quantity})")

                add_space()
                choice = input(
                    "Select an item to interact with (enter the number), or type '0' to cancel: ")
                try:
                    choice_index = int(choice) - 1
                    if 0 <= choice_index < len(area.items):
                        selected_item_dict = area.items[choice_index]
                        self.interact_with_area_items(
                            selected_item_dict, area, player)
                    elif choice_index == -1:
                        text("You decided not to pick up any items.")
                    else:
                        text("Invalid choice.")
                except ValueError:
                    text("Invalid input. Please enter a number.")
            else:
                print("You searched the area but found nothing.")

    def interact_with_area_items(self, the_item, area, player):
        item = the_item['item']

        if isinstance(item, Weapon):
            name = item.name
            if ask_user("confirm", f"You found a {name}. Do you want to equip it?"):
                if player.weapon:
                    area.items.append({'item': player.weapon, 'quantity': 1})
                player.weapon = item
                text(f"You have equipped the {name}.")
                area.items.remove(the_item)

        elif isinstance(item, Armour):
            name = item.name
            if ask_user(type="confirm", prompt=f"You found a {name}. Do you want to equip it?"):
                if player.armour:
                    area.items.append({'item': player.armour, 'quantity': 1})
                player.armour = item
                text(f"You have equipped the {name}.")
                area.items.remove(the_item)

        elif isinstance(item, Potion):
            name = item.name
            if ask_user(type="confirm", prompt=f"You found a {name}. Do you want to take it?"):
                player.potions.append(item)
                area.items.remove(the_item)


class Yolkaris(Location):
    def __init__(self, size, areas) -> None:
        super().__init__(
            name="Yolkaris",
            description="A vibrant planet with diverse ecosystems.",
            size=size,
            areas=areas
        )


class Mystara(Location):
    def __init__(self, size, areas) -> None:
        super().__init__(
            name="Mystara",
            description="A mysterious planet covered in thick jungles.",
            size=size,
            areas=areas
        )


class Luminara(Location):
    def __init__(self, size, areas) -> None:
        super().__init__(
            name="Luminara",
            description="A radiant planet with a luminous landscape.",
            size=size,
            areas=areas
        )


class Area:
    def __init__(
        self,
        name: str,
        storyLine: list,
        enemy=None,
        neutral=None,
        position=None,
        items=None,
    ) -> None:
        self.name = name
        self.storyLine = storyLine
        self.enemy = enemy
        self.neutral = neutral
        self.position = position
        self.items = items if items else []


class Item:
    def __init__(self, name: str, description: str = None) -> None:
        self.name = name
        self.description = description


class Weapon(Item):
    def __init__(
            self,
            name: str,
            description: str,
            attack: int,
            actions: list) -> None:
        super().__init__(name, description)
        self.attack = attack
        self.actions = actions


class Armour(Item):
    def __init__(
            self,
            name: str,
            description: str,
            defense: int) -> None:
        super().__init__(name, description)
        self.defense = defense


class Potion(Item):
    def __init__(
            self,
            name: str,
            health: int) -> None:
        super().__init__(name)
        self.health = health


class Coin(Item):
    def __init__(
            self,
            name: str,
            description: str) -> None:
        super().__init__(name, description)


def game_title() -> None:
    """
    This is the main menu.
    """
    yolkaris = text2art("Yolkaris", font="dos_rebel", chr_ignore=True)
    odyssey = text2art("Odyssey", font="dos_rebel", chr_ignore=True)
    text(yolkaris)
    text(odyssey)


def show_help() -> None:
    """
    This function displays the available commands.
    """
    text("Available Commands:", space=1)

    text("  north      - Move North (up)", delay=0.1)
    text("  south      - Move South (down)", delay=0.1)
    text("  east       - Move East (up)", delay=0.1)
    text("  west       - Move West (up)", delay=0.1, space=1)

    text("  map        - Show the map", delay=0.1)
    text("  help       - Show this help message", delay=0.1)
    text("  quit       - Quit the game", delay=0.1)
    text(" ")

# select game level
# lvl 1 - A quick game
# lvl 2 - Not to short not to long
# lvl 3 - I understand there is no save game implemented


game_level = 1

if game_level == 1:

    yolkaris_size = (4, 2)
    mystara_size = (2, 1)
    luminara_size = (2, 1)

    yolkaris_areas = [
        Area(
            name="Capital City",
            storyLine=[
                # {
                #     "clear": True
                # },
                # {
                #     "text": "As you embark on 'The Broken Clock' adventure in"
                #     " 'Yolkaris Odyssey', the vibrant energy of The Capital"
                #     " surrounds you. The sun bathes the cobblestone streets"
                #     " in a warm glow, and the citizens of Yolkaris go about"
                #     " their daily routines.",
                # },
                # {
                #     "text": "However, an unusual silence draws your attention"
                #     " to the Grand Clock standing majestically at the city's"
                #     " center. To your surprise, its hands have stopped moving,"
                #     " causing a sense of unease among the townsfolk. ",
                # },
                # {
                #     "text": "As Clucky, the brave and curious chicken, you"
                #     " approach the Grand Clock to investigate the matter."
                #     " There, you meet Timekeeper Ticktock, an elderly bird"
                #     " with keen eyes behind a shiny monocle."
                # },
                # {
                #     "continue": True
                # }
            ],
            items=[],
            neutral=Neutral(
                name="Timekeeper",
                storyLine=[
                    {
                        "text": "Hello"
                    },
                    {
                        "text": "Timekeeper: Ah, Clucky! Our Grand Clock has"
                        " stopped. Its magic is fading. You must find the Time"
                        " Crystal in the Crystal Hills to restore it."
                    },
                    {
                        "text": "Clucky: I will find the crystal and save the"
                        " clock, Timekeeper."
                    },
                    {
                        "text": "Timekeeper: Hurry, for time is of the essence"
                        " now."
                    },
                    {
                        "continue": True
                    },
                    {
                        "clear": True
                    },
                    {
                        "text": "But before you go here is how to Play"
                        " Yolkaris Odyssey:"
                    },
                    {
                        "text": "- There is one location in this story, "
                        " Yolkaris."
                    },
                    {
                        "text": "- You can see your current position within a "
                        " location by using the 'map' command."
                    },
                    {
                        "text": "- To move around the map, use the directional"
                        " commands: 'north', 'south', 'east', and 'west'."
                    },
                    {
                        "text": "- You can search the area you are in using"
                        " the 'search' command."
                    },
                    {
                        "text": "- You can carry items in your inventory."
                        " Check your inventory using the 'inventory' command."
                    },
                    {
                        "text": "Good Luck, and have fun!"
                    },
                ]
            ),
            position=(0, 0),
        ),
        Area(
            name="Bounty Harbour",
            storyLine=[
                {
                    "clear": True
                },
                {
                    "text": "Bounty Harbour, a lively hub where sea and trade unite. It's a place where sailors"
                    " and merchants from afar anchor their ships, bringing exotic wares and stories from"
                    " distant planets. The harbour air is rich with a blend of spices and the fresh ocean breeze.",
                    "space": 1
                },
                {
                    "text": "Tony, a seasoned sailor, spots Clucky and "
                    " approaches with a knowing smile.",
                    "space": 0
                },
                {
                    "text": "Hey Clucky, on a mission for the clock? You're"
                    " our beacon of hope, you know.",
                    "color": color_neutral
                },
                {
                    "text": "Thanks, Tony. Good to see you. Your support means a lot to me.",
                    "space": 1,
                    "color": color_player
                },
                {
                    "text": "Be careful out there, alright? We're counting on you, Clucky.",
                    "space": 1
                },
                {
                    "text": "Will do. See you in a few days, Tony!",
                    "space": 1,
                    "color": color_player
                },
                {
                    "text": "Sara, a cheerful trader, greets Clucky with enthusiasm. Sara: Clucky, we're all"
                    " rooting for you! You're our best chance to fix the clock.",
                    "space": 1
                },
                {
                    "text": "I appreciate it, Sara. I won't let Yolkaris down. The clock will tick again.",
                    "space": 1,
                    "color": color_player
                },
                {
                    "text": "Bring back the magic, my friend. We believe in you, Clucky.",
                    "space": 1
                },
                {
                    "text": "Garry, a local rival, sneers at Clucky. Saving the clock, Clucky? That's a"
                    " laugh. You? The hero? Guess we're really desperate.",
                    "space": 1
                },
                {
                    "text": "Clucky, unfazed, responds with a smile. Every bit counts, Garry. Even"
                    " skepticism like yours.",
                    "space": 1,
                    "color": color_player
                },
                {
                    "text": "Just don't get lost on your way, featherbrain! Not everyone's a believer.",
                    "space": 1
                },
                {
                    "text": "As Clucky walks away, he feels the mixed vibes of support and skepticism, steeling"
                    " himself for the journey ahead. Determined, Clucky heads towards his next destination.",
                    "space": 1
                }

            ],
            position=(1, 0),
        ),
        Area(
            name="Cluckington Valley",
            storyLine=[],
            position=(0, 1),
        ),
        Area(
            name="Crystal Hills",
            storyLine=[],
            enemy=False,
            position=(3, 1),
        ),
        Area(
            name="Yonder Forest",
            storyLine=[],
        ),
        Area(name="Clucker's Canyon",
             storyLine=[
                 {
                     "clear": True
                 },
                 {
                     "text": "Clucker's Canyon, with its echoing walls and"
                     " towering red cliffs, is a marvel of nature on Yolkaris."
                     " The canyon has witnessed the rise and fall of many"
                     " civilizations, holding secrets of the past within its"
                     " rugged landscape. It's said that the echoes in the"
                     " canyon are the voices of ancient Yolkarians."
                 },
                 {
                     "text": "The canyon is not just a historical site but also"
                     " a treasure trove of mystery. Explorers and treasure"
                     " hunters often delve into its depths, seeking lost"
                     " artifacts of the chicken civilizations that once"
                     " flourished here."
                 },
                 {
                     "break": True
                 },
                 {
                     "text": "Clucky - Every echo in Clucker's Canyon tells a"
                     " story. I can almost hear the clucks and caws of the"
                     " ancients. It's like they're still here, sharing their"
                     " tales with anyone who listens. I wonder what stories the"
                     " canyon walls would tell if they could talk"
                 }
             ],
             ),
        Area(name="Bubble Beach",
             storyLine=[
                 {
                     "clear": True
                 },
                 {
                     "text": "Bubble Beach is famous for its iridescent bubbles"
                     " that float up from the sea. The bubbles are said to"
                     " contain tiny galaxies, a reminder of the vastness of"
                     " the universe."
                 },
                 {
                     "text": "These bubbles are mesmerizing. Each one holds a"
                     " tiny galaxy. It's a reminder of how small we are in this"
                     " vast universe. But even the smallest pebble can make"
                     " ripples across the water."
                 }
             ],
             ),
        Area(name="Peckers Peak",
             storyLine=[
                 {
                     "clear": True
                 },
                 {
                     "text": "Peckers Peak is the highest point on Yolkaris,"
                     " known for its breathtaking views. Legend says it's where"
                     " the ancient chickens first learned to navigate the"
                     " stars."
                 },
                 {
                     "text": "Clucky - Wow, the view from here is incredible!"
                     " I can see the whole of Yolkaris and Crystal Hills."
                     " It's said that the ancient chickens gazed at the stars"
                     " from here, plotting their courses across the skies. If"
                     " only I had their knowledge now..."
                 },
             ],
             ),
    ]

    mystara_areas = []

    luminara_areas = []

elif game_level == 2:
    yolkaris_size = (1, 0)
    mystara_size = (1, 1)
    luminara_size = (1, 1)

    yolkaris_areas = [
        Area(
            name="Capital City",
            storyLine=[],
            items=[],
            position=(0, 0),
        ),
    ]

    mystara_areas = []

    luminara_areas = []

elif game_level == 3:
    yolkaris_size = (1, 0)
    mystara_size = (1, 1)
    luminara_size = (1, 1)

    yolkaris_areas = [
        Area(
            name="Capital City",
            storyLine=[],
            items=[],
            position=(0, 0),
        ),
    ]

    mystara_areas = []

    luminara_areas = []


class Game:
    """
    This is the main class for the game.
    """

    def __init__(self) -> None:
        self.location_objects = {
            "Yolkaris": Yolkaris(yolkaris_size, yolkaris_areas),
            "Mystara": Mystara(mystara_size, mystara_areas),
            "Luminara": Luminara(luminara_size, luminara_areas),
        }
        self.current_location = 0
        self.game_over = False
        self.player = None
        self.config = Config()

    def create_player(self) -> None:
        """
        This creates the player.
        """
        while True:
            username = ask_user(
                type=None, prompt="Please enter your username: ")
            if 3 <= len(username) <= 24 and username.isalnum() and "_" not in username:
                self.player = Player(
                    name=username,
                    health=100,
                    attack=10,
                    defense=10,
                    potions=[
                        Potion(
                            name="Small Potion",
                            health=10,
                        )
                    ],
                    coins=0,
                    inventory=[]
                )
                break
            else:
                paragraph(
                    "Invalid username. It should be between 3 to 24 characters"
                    ",contain only letters and numbers, and no underscores.",
                    color=color_error,
                )

    def show_player_stats(self) -> None:
        """
        This method displays the player's stats.
        """
        # Retrieve the player object and current location object
        player = self.player
        current_location = self.get_current_location()

        # Display player's basic stats
        add_space()
        text(f"Player {player.name}:")
        text(
            f"Health: {player.health}, Attack: {player.attack}, Defense: {player.defense}", color=color_light_gray)
        text(f"Armour: {player.armour.name if player.armour else 'None'}")
        text(f"Weapon: {player.weapon.name if player.weapon else 'None'}")

        # potions count
        potions_count = len(player.potions)
        text(f"Potions: {potions_count}")
        # Generating inventory list
        inventory_list = []
        for inventory_item in player.inventory:
            # This is an instance of Weapon, Armour, or Item
            item = inventory_item['item']
            quantity = inventory_item['quantity']
            item_display = f"{item.name} (Quantity: {quantity})" if quantity > 1 else item.name
            inventory_list.append(item_display)
        inventory = ", ".join(inventory_list)
        text(f"Inventory: {inventory}")
        text(f"Coins: {player.coins}")
        self.location_and_position()

    def choose_action(self) -> None:
        """
        This method displays the available actions and prompts the player to 
        choose an action. The method then calls the appropriate method based on 
        the player's choice.
        """
        action = input(">> ")
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
        elif action == "search" or action == "s":
            self.search_current_area()
        elif action == "inventory" or action == "i":
            self.show_inventory()
        elif action == "quit":
            self.game_over = True

    def search_current_area(self):
        """
        This method searches the current area for items.
        """
        current_location = self.get_current_location()
        current_location.search_area(self.player)

    def start_game(self) -> None:
        """
        This is the main game loop.
        """
        clear_terminal()
        game_title()
        text("Welcome to Yolkaris Odyssey, a text-based adventure game.", delay=0.1)
        text("Coded and designed by Patrick Hladun.", delay=0.1, space=1)
        ask_user(type='continue', prompt='Press enter to start the game: ')
        self.create_player()
        self.assign_player_to_location()
        self.intro()
        while not self.game_over:
            self.choose_action()

    def intro(self) -> None:
        """
        This is the introduction to the game.
        """
        clear_terminal()
        text(f"Hello {self.player.name}!", delay=0.5, space=1)
        # Need the welcome story here game intro
        ask_user(type='continue')
        starting_location = self.get_current_location()
        starting_location.check_for_interaction((0, 0), self.player)
        self.display_map()

    def get_current_location(self) -> Location:
        """
        Retrieves the current location object based on the player's position.

        This method accesses the `location_objects` dictionary using the
        `current_location` index, which represents the player's current location

        Returns the current location object where the player is at present.
        """
        # Retrieve the name of the current location based on the player's position
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
        current_location = self.get_current_location()
        area_name = current_location.get_area_name_by_position(
            current_location.player_position)
        text(f"\nCurrent Location: {current_location.name}")
        text(f"Current Position: {area_name}", space=1)

    def display_map(self) -> None:
        """
        This method displays the map of the current location.
        """
        self.location_and_position()
        current_location = self.get_current_location()
        current_location.display_map()

    def update_player_position(self, dx: int, dy: int) -> None:
        """
        This method updates the player's position in the current location.
        dx: int - The change in the x-axis
        dy: int - The change in the y-axis
        """
        # Retrieve the current location object
        current_location = self.get_current_location()

        # Update previous position before changing the current position
        current_location.player_prev_position = current_location.player_position

        # Calculate the new position
        new_position = (current_location.player_position[0] + dx,
                        current_location.player_position[1] + dy)

        # Check if the new position is valid
        if current_location.is_valid_position(new_position):
            current_location.player_position = new_position
            current_location.mark_visited(new_position)
            current_location.check_for_interaction(new_position, self.player)
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

    def show_inventory(self):
        if not self.player.inventory:
            text("Your inventory is empty.")
            return

        text("Your inventory contains:")
        for index, inventory_item in enumerate(self.player.inventory, start=1):
            item = inventory_item['item']
            quantity = inventory_item['quantity']
            name = item.name
            display_text = f"{index}. {name} (Quantity: {quantity})" if quantity > 1 else f"{index}. {name}"
            text(display_text)

        choice = input(
            "Choose an item to interact with (number), or type '0' to cancel: ")
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
        the_item = self.player.inventory[index]
        item = the_item['item']
        quantity = the_item['quantity']
        name = item.name
        print(f"You selected {name}.")
        print(f"Quantity: {quantity}")

        action = input(
            "Do you want to 'use' or 'inspect' the item? (use/inspect): ")
        if action.lower() == 'use':
            self.use_inventory_item(the_item)  # Create this method
        elif action.lower() == 'inspect':
            self.inspect_inventory_item(the_item)  # Create this method
        else:
            text("Invalid action.")


if __name__ == "__main__":
    game = Game()
    game.start_game()
