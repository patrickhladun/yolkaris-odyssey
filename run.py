from game.config import Config
import random
from art import *
from utils import (text, paragraph, space, clear_terminal, ask_user,
                   color_light_gray, color_light_blue)
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
            defense: int) -> None:
        super().__init__(name)
        self.health = health
        self.attack = attack
        self.defense = defense
        self.inventory = []
        self.weapon = None
        self.armor = None


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
    def __init__(self, name) -> None:
        super().__init__(name)


class Interaction:
    def __init__(self, player):
        self.player = player

    def with_area(self, area):
        clear_terminal()
        for line in area.storyLine:
            paragraph(line['text'], space=1)

    def with_enemy(self, enemy, location):
        space()
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
        elif results == "won":
            text(f"You have defeated {enemy.name}!")
        elif results == "lost":
            text(f"You have been defeated by {enemy.name}!")
            text("Game Over!")


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
        if ask_user('combat', color=color_light_blue):
            result = self.combat()
            return result
        else:
            return "retreat"

    def continue_or_flee(self):
        return ask_user('retreat', color=color_light_blue)

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
        armor_bonus = self.player.armor["defense"] if self.player.armor else 0
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
        # print(f"Position: {self.player_position}")
        # pprint(self.map)
        # print('Contents')
        # pprint(f"{self.contents}", width=135)
        # print('Visited')
        # pprint(f"{self.visited}", width=135)
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
                if element.enemy:
                    ask_user('continue', color=color_light_blue)
                    interaction.with_enemy(element.enemy, self)

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
                for index, item in enumerate(area.items):
                    text(f"{index + 1}. {item['name']}", delay=0.2)

                space()
                choice = input(
                    "Select an item to interact with (enter the number), "
                    "or type '0' to cancel: "
                )
                try:
                    choice_index = int(choice) - 1
                    if 0 <= choice_index < len(area.items):
                        selected_item = area.items[choice_index]
                        self.interact_with_item(selected_item, area, player)
                    elif choice_index == -1:
                        text("You decided not to pick up any items.")
                    else:
                        text("Invalid choice.")
                except ValueError:
                    text("Invalid input. Please enter a number.")
            else:
                print("You searched the area but found nothing.")

    def interact_with_item(self, item, area, player):
        if item in weapon.values():
            if ask_user(
                "confirm", f"You found a {item['name']}. Do you want to "
                           f"equip it? "
            ):
                if player.weapon:
                    # Drop the current weapon
                    area.items.append(player.weapon)
                # Equip the new weapon
                player.weapon = item
                text(f"You have equipped the {item['name']}.")
                # Remove the new weapon from the area
                area.items.remove(item)
        elif item in armor.values():
            if ask_user(
                "confirm", f"You found a {item['name']}. Do you want to wear "
                           f"it? "
            ):
                if player.armor:
                    # Drop the current armor
                    area.items.append(player.armor)
                # Wear the new armor
                player.armor = item
                text(f"You have put on the {item['name']}.")
                # Remove the new armor from the area
                area.items.remove(item)
        else:
            player.inventory.append(item)
            text(f"You found a {item['name']} and added it to your inventory.")
            # Remove the item from the area
            area.items.remove(item)


class Yolkaris(Location):
    def __init__(self) -> None:
        super().__init__(
            name="Yolkaris",
            description="A vibrant planet with diverse ecosystems.",
            size=(4, 2),
            areas=yolkaris_areas
        )


class Mystara(Location):
    def __init__(self) -> None:
        super().__init__(
            name="Mystara",
            description="A mysterious planet covered in thick jungles.",
            size=(8, 4),
            areas=mystara_areas,
        )


class Luminara(Location):
    def __init__(self) -> None:
        super().__init__(
            name="Luminara",
            description="A radiant planet with a luminous landscape.",
            size=(7, 4),
            areas=luminara_areas,
        )


class Area:
    def __init__(
        self,
        name: str,
        storyLine: list,
        enemy=None,
        position=None,
        items=None,
    ) -> None:
        self.name = name
        self.storyLine = storyLine
        self.enemy = enemy
        self.position = position
        self.items = items if items else []


weapon = {
    "sword": {
        "name": "Sword",
        "description": "A sharp sword.",
        "attack": 15,
        "actions": ["slash", "stab"],
    },
    "stick": {
        "name": "Stick",
        "description": "Small stick.",
        "attack": 1,
        "actions": ["slash", "stab"],
    },
}

armor = {
    "wooden_shield": {
        "name": "Wooden Shield",
        "description": "Small Metal shield.",
        "defense": 2,
    },
    "metal_shield": {
        "name": "Metal Shield",
        "description": "Small Metal shield.",
        "defense": 12,
    },
}

item = {
    "potion": {
        "name": "Potion",
        "description": "A healing potion.",
        "health": 10,
    },
    "key": {
        "name": "Key",
        "description": "A key.",
    },
    "coin": {
        "name": "Coin",
        "description": "A coin.",
    },
    "gem": {
        "name": "Gem",
        "description": "A gem.",
    },
    "scroll": {
        "name": "Scroll",
        "description": "A scroll.",
    },
}

yolkaris_areas = [
    Area(
        name="Lost City Ruins",
        storyLine=[],
        items=[weapon["stick"]],
        position=(0, 0),
    ),
    Area(
        name="Crystal Caverns",
        storyLine=[],
        items=[
            weapon["sword"],
            armor["wooden_shield"],
            armor["metal_shield"],
            item["potion"],
            item["key"],
            item["coin"],
        ],
        position=(1, 0),
    ),
    Area(
        name="Enchanted Forest",
        storyLine=[
            {
                "text": "A mystical woodland brimming with magical creatures"
                " and ancient trees.",
            },
            {
                "text": "As you step into the Enchanted Forest, a sense of awe"
                " washes over you. The sights and sounds of the forest are"
                " like nothing you've ever experienced. The air feels thick"
                " with magic, almost as if you could reach out and touch"
                " it."
            },
            {
                "text": "Clucky - I feel tired; the journey has been so long"
                " already. A cup of nice coffee would be a blessing now. I"
                " wonder how folks are doing back home. This seems like a"
                " good spot for a quick nap"
            }
        ],
        position=(0, 1),
        enemy=Enemy(
            name="Yorkish",
            storyLine=[
                {
                    "text": "Yorkish, a shadowy figure with glowing eyes and"
                    " sharp dark feathers, moves silently. Its eerie screech"
                    " is feared in the Enchanted Forest."
                },
                {
                    "text": "As you feel its presence, the forest falls"
                    " eerily quiet. Confronted by Yorkish's menacing stare,"
                    " you face a critical choice: fight bravely or retreat"
                    " swiftly."
                }

            ],
            health=20,
            attack=7,
            defense=9,
        ),
    ),
    Area(
        name="Haunted Graveyard",
        storyLine=[],
    ),
]

mystara_areas = [
    Area(
        name="Enchanted Forest",
        storyLine=[],
    ),
]

luminara_areas = [
    Area(
        name="Enchanted Forest",
        storyLine=[],
    ),
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
    text("Available Commands:", space=1)

    text("  north      - Move North (up)", delay=0.1)
    text("  south      - Move South (down)", delay=0.1)
    text("  east       - Move East (up)", delay=0.1)
    text("  west       - Move West (up)", delay=0.1, space=1)

    text("  map        - Show the map", delay=0.1)
    text("  help       - Show this help message", delay=0.1)
    text("  quit       - Quit the game", delay=0.1)
    text(" ")


class Game:
    """
    This is the main class for the game.
    """

    def __init__(self) -> None:
        self.location_objects = {
            "Yolkaris": Yolkaris(),
            "Mystara": Mystara(),
            "Luminara": Luminara(),
        }
        self.current_location = 0
        self.game_over = False
        self.player = None
        self.config = Config()

    def create_player(self) -> None:
        """
        This creates the player.
        """
        # clear_terminal()
        text("Welcome to the game! Great adventurer.")
        while True:
            username = input("Please enter your username: ").strip()
            if 3 <= len(username) <= 24 and username.isalnum() and "_" not in username:
                self.player = Player(username, 100, 10, 10)
                break
            else:
                print(
                    "Invalid username. It should be between 3 to 24 characters"
                    ",contain only letters and numbers, and no underscores."
                )

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
        text(f"Health: {player.health}")
        text(f"Attack: {player.attack}")
        text(f"Defense: {player.defense}")
        text(f"Armour: {player.armor['name'] if player.armor else 'None'}")
        text(f"Weapon: {player.weapon['name'] if player.weapon else 'None'}")
        inventory = ", ".join([item["name"] for item in player.inventory])
        text(f"Inventory: {inventory}")
        # Display player's current location
        text(f"\nCurrent Location: {current_location.name}")
        text(f"{current_location.description}\n")

    def choose_action(self) -> None:
        """
        This method displays the available actions and prompts the player to 
        choose an action. The method then calls the appropriate method based on 
        the player's choice.
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
        elif action == "s":
            self.search_current_area()
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
        # clear_terminal()
        # game_title()
        # paragraph("Welcome to 'Yolkaris Odyssey'! Immerse yourself in a Python text-based adventure game filled with "
        #          "multiple locations to explore, a dynamic map to guide you, enthralling narrations, and exciting "
        #          "battles with enemies. Get ready for an engaging and fun-filled journey!")
        # ask_user('continue', 'Press enter to start the game: ')

        # Create player
        self.create_player()

        # Assign player to current location
        self.assign_player_to_location()

        # Start game intro
        # self.intro()
        while not self.game_over:
            self.choose_action()

    def intro(self) -> None:
        """
        This is the introduction to the game.
        """
        clear_terminal()

        text(f"Hello {self.player.name}!", delay=0.8, space=1)
        paragraph(
            "You'll step into Clucky's shoes, a valiant and clever chicken from the vibrant planet Yolkaris. Once a "
            "haven of peace and harmony, Yolkaris now faces a dire threat that jeopardizes its existence. As Clucky, "
            "it's up to you to embark on a daring quest to save your home planet. Are you ready to don the feathers "
            "of Clucky and become the hero Yolkaris needs? "
        )

        # Ask if user is ready if not, exit the game and show funny message
        ask_user("continue")

        clear_terminal()
        text("Here is the story of Yolkaris Odyssey.", delay=0.8, space=1)
        paragraph(
            "In the boundless expanse of the cosmos, among a sea of twinkling stars, lies Yolkaris - a vibrant and "
            "lively planet home to an extraordinary species of spacefaring chickens. But now, Yolkaris faces an "
            "unprecedented crisis. A mysterious and malevolent cosmic dust, known as The Dark Dust, has enshrouded "
            "the planet in shadow, blocking the essential sunlight and disrupting the delicate balance of its "
            "ecosystem. The once bright and bustling world, a haven of clucking harmony, now teeters on the brink of "
            "ecological collapse. "
        )
        paragraph(
            "In this hour of desperation, hope rests on the wings of one brave hero - Clucky. Renowned for courage "
            "and cleverness, Clucky's destiny is to embark on a quest beyond the stars. The mission is dangerous, "
            "the stakes are high, and the journey will take Clucky to uncharted corners of the galaxy. "
        )
        paragraph(
            "As Clucky, you will traverse through cosmic wonders and confront unknown dangers. Your quest will lead "
            "you to ancient relics and forgotten worlds, where secrets of The Dark Dust await to be uncovered. The "
            "journey promises challenges, trials, and the chance to become the saviour that Yolkaris desperately "
            "needs. "
        )
        ask_user("continue")

        clear_terminal()
        text("How to Play Yolkaris Odyssey:", delay=0.8, space=1)
        text(
            "- There are three locations in the game: Yolkaris, Mystara, and Luminara."
        )
        text(
            "- You can see your current position within a location by using the 'map' command."
        )
        text(
            "- To move around the map, use the directional commands: 'north', 'south', 'east', and 'west'."
        )
        text(
            "- If you encounter items or enemies, you will be prompted to interact with them."
        )
        text(
            "- You can carry items in your inventory. Check your inventory using the 'inventory' command."
        )
        text(
            "- Keep an eye on your health, attack, and defense stats. They are crucial for survival."
        )
        text(
            "- If you need to see the list of available commands at any time, use the 'help' command.",
            delay=0.6,
            space=1,
        )
        text("Good luck on your adventure to save Yolkaris!", delay=0.6, space=1)
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

    def display_map(self) -> None:
        """
        This method displays the map of the current location.
        """
        # Retrieve the current location object
        current_location = self.get_current_location()
        # Display the map of the current location
        text(f"Map of {current_location.name}", space=1)
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


if __name__ == "__main__":
    game = Game()
    game.start_game()
