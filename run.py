import random
from art import *
from utils import (text, paragraph, add_space, clear_terminal, ask_user,
                   loading, color_player, color_neutral,
                   color_error)


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
            defense: int) -> None:
        super().__init__(name)
        self.health = health
        self.attack = attack
        self.defense = defense
        self.inventory = inventory
        self.potions = potions
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
            storyLineVisited: list,
            storyLineFought: list,
            storyLineWonFight: list,
            storyLineLostFight: list,
            storyLineDefeated: list,
            health: int,
            attack: int,
            defense: int,
            fought: bool = False
    ) -> None:
        super().__init__(name)
        self.storyLine = storyLine
        self.storyLineVisited = storyLineVisited
        self.storyLineFought = storyLineFought
        self.storyLineWonFight = storyLineWonFight
        self.storyLineLostFight = storyLineLostFight
        self.storyLineDefeated = storyLineDefeated
        self.health = health
        self.attack = attack
        self.defense = defense
        self.fought = fought


class Neutral(Character):
    def __init__(
            self,
            name,
            storyLine,
            storyLineVisited=None,
            storyLineCompleted=None,
            questItem=None
    ) -> None:
        super().__init__(name)
        self.storyLine = storyLine
        self.storyLineVisited = storyLineVisited
        self.storyLineCompleted = storyLineCompleted
        self.questItem = questItem


class Interaction:
    def __init__(self, player):
        self.player = player

    def add_new_item(self, item):
        self.player.inventory.append(item)

    def print_story_line(self, storyLine):
        for line in storyLine:
            space = line['space'] if 'space' in line else 1
            delay = line['delay'] if 'delay' in line else 0.1
            color = line['color'] if 'color' in line else None
            if 'clear' in line:
                clear_terminal()
            elif 'text' in line:
                paragraph(line['text'], space=space, color=color, delay=delay)
            elif 'neutral' in line:
                paragraph("- " + line['neutral'],
                          space=space, color=color_neutral, delay=delay)
            elif 'enemy' in line:
                paragraph("- " + line['enemy'],
                          space=space, color=color_neutral, delay=delay)
            elif 'player' in line:
                paragraph("- " + line['player'],
                          space=space, color=color_player, delay=delay)
            elif 'continue' in line:
                ask_user('continue', space=space)
            elif 'item' in line:
                self.add_new_item(line['item'])
            elif 'gameover' in line:
                reset_game(game)

    def with_area(self, area, visited):
        add_space()
        if not visited:
            self.print_story_line(area.storyLine)
        else:
            self.print_story_line(area.storyLineVisited)

    def with_neutral(self, neutral, visited):
        add_space()
        if not visited:
            self.print_story_line(neutral.storyLine)
        elif visited and neutral.questItem:
            has_quest_item = any(
                item.name == neutral.questItem.name for item in self.player.inventory
            )
            if has_quest_item and neutral.questItem:
                # Player has the quest item, proceed with the special storyline
                self.print_story_line(neutral.storyLineCompleted)
                reset_game()
            else:
                # Player does not have the quest item or no quest item specified, proceed with the visited storyline
                self.print_story_line(neutral.storyLineVisited)
        else:
            self.print_story_line(neutral.storyLineVisited)

    def with_enemy(self, enemy, location, visited):
        if not visited:
            self.print_story_line(enemy.storyLine)
            text(f"{enemy.name} stats - health: {enemy.health}, attack: {enemy.attack}, "
                 f"defense: {enemy.defense}", space=1)
        else:
            if enemy.health <= 0:
                self.print_story_line(enemy.storyLineDefeated)
                return
            elif enemy.fought:
                self.print_story_line(enemy.storyLineFought)
                text(f"{enemy.name} stats - health: {enemy.health}, attack: {enemy.attack}, "
                     f"defense: {enemy.defense}", space=1)
            else:
                self.print_story_line(enemy.storyLineVisited)
                text(f"{enemy.name} stats - health: {enemy.health}, attack: {enemy.attack}, "
                     f"defense: {enemy.defense}", space=1)

        combat = Combat(self.player, enemy)
        results = combat.to_fight_or_not_to_fight()
        if results == "retreat":
            text("You have retreated from the battle.")
            location.return_to_previous_position()
            return False
        elif results == "won":
            text(f"You have defeated {enemy.name}!", space=1)
            self.print_story_line(enemy.storyLineWonFight)
            return True
        elif results == "lost":
            text(f"You have been defeated by {enemy.name}!", space=1)
            self.print_story_line(enemy.storyLineLostFight)


class Combat:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy

    def combat(self):
        # Set the fought attribute to True
        self.enemy.fought = True

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
        weapon_bonus = self.player.weapon.attack if self.player.weapon else 0
        return base_attack + weapon_bonus

    def calculate_player_defense(self):
        base_defense = self.player.defense
        armor_bonus = self.player.armour.defense if self.player.armour else 0
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
    def __init__(
            self,
            name: str,
            description: str,
            size: tuple,
            areas: dict,
            travel: dict
    ) -> None:
        self.name = name
        self.description = description
        self.size = size
        self.travel = travel
        self.areas = areas if areas else []
        self.player_position = (0, 0)
        self.player_prev_position = (0, 0)
        self.contents = {}
        self.map = [["" for _ in range(size[0])] for _ in range(size[1])]
        self.visited = [[False for _ in range(
            size[0])] for _ in range(size[1])]
        self.randomly_place_elements()

    def place_on_map(self, element, position=None):
        """
        Places an element on the map at the specified position.
        """
        while position is None or position in self.contents:
            position = self.get_random_position()
        self.contents[position] = element

    def is_visited(self, position):
        return self.visited[position[1]][position[0]]

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
        visited = self.is_visited(position)
        if position in self.contents:
            element = self.contents[position]
            if isinstance(element, Area):
                interaction = Interaction(player)
                interaction.with_area(element, visited)

                # Mark the position as visited
                self.mark_visited(self.player_position)

                if element.enemy:
                    interaction.with_enemy(element.enemy, self, visited)

                # Start interaction with neutral if no enemy or enemy defeated
                if (not element.enemy or element.enemy.health <= 0) and element.neutral:
                    interaction.with_neutral(element.neutral, visited)

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
                    name = item.name
                    text(f"{index + 1}. {name}")

                add_space()
                prompt = "Select an item number to interact with, or type '0' to cancel: "
                choices = [str(i) for i in range(1, len(area.items) + 1)]
                choice = ask_user("number", numbers=choices, prompt=prompt)

                try:
                    choice_index = int(choice) - 1
                    if 0 <= choice_index < len(area.items):
                        item = area.items[choice_index]
                        self.interact_with_area_items(
                            item, area, player)
                    elif choice_index == -1:
                        text("You decided not to pick up any items.")
                    else:
                        text("Invalid choice.")
                except ValueError:
                    text("Invalid input. Please enter a number.")
            else:
                text("You searched the area but found nothing.")

    def interact_with_area_items(self, item, area, player):
        if isinstance(item, Weapon):
            name = item.name
            add_space()
            text(f"You found a {name}.")
            if ask_user("confirm", prompt="Do you want to equip it? "):
                if player.weapon:
                    area.items.append(player.weapon)
                player.weapon = item
                text(f"You have equipped the {name}.", space=1)
                area.items.remove(item)

        elif isinstance(item, Armour):
            name = item.name
            add_space()
            text(f"You found a {name}.")
            if ask_user(type="confirm", prompt="Do you want to equip it?"):
                if player.armour:
                    area.items.append(player.armour)
                player.armour = item
                text(f"You have equipped the {name}.", space=1)
                area.items.remove(item)

        elif isinstance(item, Potion):
            name = item.name
            add_space()
            text(f"You found a {name}.")
            if ask_user(type="confirm", prompt="Do you want to take it?"):
                player.potions.append(item)
                area.items.remove(item)
                text(f"You have added the {name} to your inventory.", space=1)

        elif isinstance(item, Book):
            name = item.name
            add_space()
            text(f"You found a {name}.")
            if ask_user(type="confirm", prompt="Do you want to take it?"):
                player.inventory.append(item)
                area.items.remove(item)
                text("You have added the book to your inventory.", space=1)

        elif isinstance(item, Item):
            name = item.name
            add_space()
            text(f"You found a {name}.")
            if ask_user(type="confirm", prompt="Do you want to take it?"):
                player.inventory.append(item)
                area.items.remove(item)

    def print_travel_story_line(self, direction):
        if direction in self.travel:
            for line in self.travel[direction]:
                paragraph(line, space=1, delay=0.6)


class Yolkaris(Location):
    def __init__(self, size, areas, travel) -> None:
        super().__init__(
            name="Yolkaris",
            description="A vibrant planet with diverse ecosystems.",
            size=size,
            areas=areas,
            travel=travel
        )


class Mystara(Location):
    def __init__(self, size, areas, travel) -> None:
        super().__init__(
            name="Mystara",
            description="A mysterious planet covered in thick jungles.",
            size=size,
            areas=areas,
            travel=travel
        )


class Luminara(Location):
    def __init__(self, size, areas, travel) -> None:
        super().__init__(
            name="Luminara",
            description="A radiant planet with a luminous landscape.",
            size=size,
            areas=areas,
            travel=travel
        )


class Area:
    def __init__(
            self,
            name: str,
            storyLine: list,
            storyLineVisited: list,
            visited: bool = False,
            enemy=None,
            neutral=None,
            position=None,
            items=None,
    ) -> None:
        self.name = name
        self.storyLine = storyLine
        self.storyLineVisited = storyLineVisited
        self.visited = visited
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


class Book(Item):
    def __init__(
            self,
            name: str,
            description: str,
            storyLine: list) -> None:
        super().__init__(name, description)
        self.storyLine = storyLine


class Spaceship(Item):
    def __init__(self, name: str, description: str) -> None:
        super().__init__(name, description)


class Special(Item):
    def __init__(self, name: str, description: str, storyLine: list = None) -> None:
        super().__init__(name, description)
        self.storyLine = storyLine


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
    text("  search     - Search the area for items", delay=0.1)
    text("  help       - Show this help message", delay=0.1)
    text("  inventory  - Show your inventory", delay=0.1)
    text("  potion     - Use a potion", delay=0.1)
    text("  stats      - Show your stats", delay=0.1)
    text("  reset      - Reset the game", delay=0.1)
    text("  quit       - Quit the game", delay=0.1)
    text(" ")


def reset_game(game_instance=None):
    # If a game instance is provided, use it; otherwise, create a new one
    if game_instance is None:
        game_instance = Game()
    game_instance.reset_game()
    return game_instance


class Game:
    """
    This is the main class for the game.
    """

    def __init__(self) -> None:
        self.location_objects = {}
        self.current_location = 0
        self.game_over = False
        self.player = None

    def setup_game(self):
        """
        This method sets up the game.
        """
        # clear_terminal()
        # game_title()
        # text("Welcome to Yolkaris Odyssey, a text-base"
        #      " adventure game.", delay=0.1)
        # text("Coded and designed by Patrick Hladun.", delay=0.1, space=1)
        ask_user(type='continue',
                 prompt='Press enter to start the game: ', space=0)
        clear_terminal()
        self.create_player()
        # clear_terminal()
        # text(f"Hey {self.player.name}!", delay=0.6, space=1)
        # paragraph("Welcome to Yolkaris Odyssey! You're about to embark on a"
        #           " thrilling adventure as Charlie, a courageous chicken with a"
        #           " spirit of exploration. This game takes you to the"
        #           " beautiful planet of Yolkaris, where every corner is filled"
        #           " with wonder and mystery.")
        # paragraph("Yolkaris Odyssey presents three enthralling tales, each"
        #           " unfolding in its own unique way. Discover the mysteries"
        #           " hidden within the dense forests of Mystara, experience the"
        #           " ethereal beauty of Luminara's radiant fields, and delve"
        #           " into the ancient, forgotten lore that pervades every inch"
        #           " of Yolkaris. Each path you choose leads to new discoveries"
        #           " and adventures.")
        # game_level = self.select_game_level()
        game_level = 2
        self.setup_areas(game_level)
        clear_terminal()
        # loading(['Generating game', '.', '.', '.',
        #         '.', '.', '.', '.'], 'Game generated')
        # loading(['Starting game', '.', '.', '.', '.'])
        self.assign_player_to_location()
        self.current_location = 0
        starting_location = self.get_current_location()
        starting_location.check_for_interaction((0, 0), self.player)
        self.display_map()

    def select_game_level(self):
        """
        This method allows the player to select the game level.
        """
        text("Select your Game:", delay=0.2, space=1)
        text("  1. The Broken Clock", delay=0.2)
        text("  2. The Dark Dust", delay=0.2, space=1)
        return ask_user(type="number", numbers=['1', '2', '3'])

    def start_game(self) -> None:
        """
        This is the main game loop.
        """
        while not self.game_over:
            self.choose_action()

    def setup_areas(self, level) -> None:

        if level == 1:

            yolkaris_size = (4, 2)
            mystara_size = (2, 1)
            luminara_size = (2, 1)

            yolkaris_areas = [
                Area(name="Capital City",
                     storyLine=[
                         {
                             "clear": True
                         },
                         {
                             "text": "The Broken Clock Adventure",
                             "delay": 0.6,
                             "space": 1
                         },
                         {
                             "text": "Capital City, where ancient whispers"
                             " meet the present's breath, lies beneath the"
                             " Grand Clock's timeless gaze. Its cobbled paths,"
                             " etched by countless souls, converge at"
                             " Yolkaris' beating heart."
                         },
                         {
                             "text": "Here stands the Grand Clock, silent"
                             " sentinel of time, now frozen in an eerie"
                             " stillness. Amidst this hush, Charlie, a beacon"
                             " of hope, steps forward with valor and"
                             " inquisitiveness in his heart."
                         },
                         {
                             "text": "Summoned by the echoes of old tales and"
                                     " the allure of the unknown, he weaves through"
                                     " the city's veiled streets to the Timekeeper. At"
                                     " the foot of the slumbering clock, a vestige of"
                                     " arcane power, a quest of fate unfolds for"
                                     " Charlie."
                         },
                         {
                             "text": "Embarking on a quest through time's"
                                     " woven fabric, he seeks to stir ancient echoes,"
                                     " awakening the chronicles lost to the ages.",
                             "space": 0
                         }
                     ],
                     storyLineVisited=[
                         {
                             "clear": True
                         },
                         {
                             "text": "Back in Capital City, the stillness of"
                                     " the Grand Clock looms, casting a silent shadow"
                                     " over the timeless streets.",
                             "space": 1
                         }
                     ],
                     items=[
                         Book(
                             name="The Broken Clock Book",
                             description="A tome chronicling the saga of"
                                         " Yolkaris' Grand Clock, whose ticking has"
                                         " ceased.",
                             storyLine=[
                                 {
                                     "clear": True
                                 },
                                 {
                                     "text": "The Broken Clock: A Tale of"
                                             " Time's Standstill",
                                     "delay": 0.6,
                                     "space": 1
                                 },
                                 {
                                     "text": "In the heart of Yolkaris"
                                             " stands the Grand Clock, once the"
                                             " pulsing chronometer of the realm."
                                             " Legends say its hands moved in"
                                             " harmony with the cosmic dance, until"
                                             " silence befell. The clock's halt has"
                                             " shrouded Yolkaris in a temporal"
                                             " anomaly, threatening the very fabric"
                                             " of time itself.",
                                     "space": 1
                                 },
                                 {
                                     "text": "The Time Crystal, hidden"
                                             " within the enigmatic Crystal Hills,"
                                             " holds the secret to awakening the"
                                             " clock. This book, penned by the last"
                                             " Timekeeper, serves as a guide for"
                                             " the brave soul daring enough to"
                                             " embark on this perilous quest. To"
                                             " restore the clock's magic and revive"
                                             " the rhythm of Yolkaris, the Time"
                                             " Crystal must be retrieved before the"
                                             " threads of time unravel completely.",
                                     "space": 1
                                 },
                             ]
                         )
                     ],
                     neutral=Neutral(
                         name="Timekeeper",
                         questItem=Item(name="The Time Crystal"),
                         storyLine=[
                             {
                                 "neutral": "Ah, Charlie! The Grand Clock, our"
                                            " timeless guardian, has ceased its rhythmic"
                                            " heartbeat. Its magic wanes. The Time"
                                            " Crystal in Crystal Hills is the key to its"
                                            " revival.",
                                 "space": 0,
                             },
                             {
                                 "player": "Fear not, Timekeeper. I shall"
                                           " reclaim the crystal and rekindle the"
                                           " clock's ancient magic.",
                                 "space": 0,
                             },
                             {
                                 "neutral": "Be swift, for the sands of time"
                                            " wait for no one. Our fate rests in your"
                                            " wings.",
                             },
                             {
                                 "continue": True
                             },
                             {
                                 "clear": True
                             },
                             {
                                 "text": "Embark on the Yolkaris Odyssey with"
                                         " these words of guidance:"
                             },
                             {
                                 "text": "In this tale, your journey begins"
                                         " in Yolkaris, a realm of myths and"
                                         " mysteries."
                             },
                             {
                                 "text": "- Use the 'map' command to find your"
                                         " path within this enchanted land.",
                                 "space": 0
                             },
                             {
                                 "text": "- Traverse the land through 'north',"
                                         " 'south', 'east', and 'west'. Discover your"
                                         " destiny.",
                                 "space": 0
                             },
                             {
                                 "text": "- In your quest, 'search' the areas"
                                         " for hidden treasures and secrets.",
                                 "space": 0
                             },
                             {
                                 "text": "- Keep your inventory filled with"
                                         " artifacts and tools. Check it with the"
                                         " 'inventory' command.",
                                 "space": 0
                             },
                             {
                                 "text": "- When your health is low, 'potion'"
                                         " can be used to restore your vitality.",
                                 "space": 0
                             },
                             {
                                 "text": "- Keep an eye on your 'stats' to"
                                         " track your progress.",
                                 "space": 0
                             },
                             {
                                 "text": "- If you require guidance, simply"
                                         " type 'help' to view a list of available"
                                         " commands.",
                                 "space": 0
                             },
                             {
                                 "text": "- To begin anew or end your"
                                         " adventure, use 'reset' or 'quit' anytime."
                             },
                             {
                                 "text": "Good fortune on your quest. May your"
                                         " journey be filled with wonder.",
                                 "space": 0
                             },
                         ],
                         storyLineVisited=[
                             {
                                 "neutral": "Hey Charlie, do you have the"
                                            " crystal?",
                                 "space": 0,
                             },
                             {
                                 "player": "No I do not.",
                                 "space": 0,
                             },
                             {
                                 "neutral": "Without the crystal I can't fix the."
                                            " clock. You need to find the crystal.",
                                 "space": 0,
                             },
                         ],
                         storyLineCompleted=[
                             {
                                 "neutral": "Ah, Charlie, you've returned! And"
                                            " with the Time Crystal, no less?",
                                 "space": 0,
                             },
                             {
                                 "player": "Yes, Timekeeper. The journey was"
                                           " perilous, but the crystal is here.",
                                 "space": 0,
                             },
                             {
                                 "neutral": "Splendid! Let's not waste another"
                                            " moment. Hand it over, and let's witness"
                                            " history reborn.",
                                 "space": 0,
                             },
                             {
                                 "continue": True
                             },
                             {
                                 "text": "With a careful hand, the Timekeeper"
                                         " places the crystal into the heart of the"
                                         " Grand Clock. Ancient gears begin to turn, a"
                                         " soft ticking fills the air, growing louder,"
                                         " until the whole town is enveloped in the"
                                         " familiar sound of time's steady march.",
                                 "space": 1,
                             },
                             {
                                 "text": "The townsfolk gather, eyes wide with"
                                         " wonder as the Grand Clock's hands resume"
                                         " their eternal dance. Cheers erupt, and"
                                         " Charlie, standing beside the Timekeeper,"
                                         " watches as the shadow of stagnation lifts,"
                                         " giving way to a renewed flow of time.",
                                 "space": 1,
                             },
                             {
                                 "neutral": "You've done it, Charlie! The heart"
                                            " of Yolkaris beats once more, thanks to you."
                                            " This day will be remembered as the moment"
                                            " when time itself was mended by the courage"
                                            " of a single soul.",
                                 "space": 1,
                             },
                             {
                                 "text": "Game Over!",
                             },
                             {
                                 "continue": True
                             },
                             {
                                 "gameover": True
                             }
                         ]
                     ),
                     position=(0, 0),
                     ),
                Area(name="Bounty Harbour",
                     storyLine=[
                         {
                             "clear": True
                         },
                         {
                             "text": "Bounty Harbour bustles with life, a hub "
                                     " for seafaring souls and wandering traders. The"
                                     " aroma of the ocean mingles with exotic spices,"
                                     " weaving a tapestry of adventure and mystery in"
                                     " the air."
                         },
                         {
                             "text": "Charlie, amidst the vibrant chatter of"
                                     " the marketplace and rhythmic creaking of ships,"
                                     " takes in the colorful tapestry of sails and"
                                     " flags, each narrating tales of distant lands"
                                     " and mysterious seas."
                         },
                     ],
                     storyLineVisited=[
                         {
                             "clear": True
                         },
                         {
                             "text": "You are back in Bounty Harbour",
                         }
                     ],
                     items=[],
                     position=(1, 0),
                     ),
                Area(name="Cluckington Valley",
                     storyLine=[
                         {
                             "clear": True
                         },
                         {
                             "text": "Cluckington Valley stretches beneath the"
                                     " gaze of ancient, watchful peaks, a tapestry of"
                                     " verdure and life woven across the land's broad"
                                     " back. Its fields, a green so vibrant they seem"
                                     " to pulse with the heartbeats of the earth"
                                     " itself, are dotted with wildflowers that perform"
                                     " silent operas to an audience of bees.",
                             "space": 1
                         },
                         {
                             "text": "A peculiar fact about the valley is its"
                                     " infamous 'Laughing Tree,' a gnarled oak whose"
                                     " branches creak in patterns that sound eerily"
                                     " like chicken laughter, especially on windy"
                                     " nights. Locals say it's the valley's way of"
                                     " reminding everyone that nature has its own"
                                     " sense of humor.",
                             "delay": 0.6
                         }
                     ],
                     storyLineVisited=[
                         {
                             "clear": True
                         },
                         {
                             "text": "You are back in Cluckington Valley",
                         }
                     ],
                     items=[
                         Book(
                             name="The Laughing Tree's Joke Book",
                             description="A collection of the most"
                                         "whimsical and hearty chuckles sourced"
                                         "directly from the Laughing Tree of"
                                         "Cluckington Valley. This book promises to"
                                         "lift the spirits of anyone brave enough to"
                                         "open its pages, offering a light-hearted"
                                         " escape into the world of feathered humor.",
                             storyLine=[
                                 {
                                     "text": "Giggles from the Canopy:"
                                             " The Laughing Tree's Joke Book",
                                     "delay": 0.6,
                                     "space": 1
                                 },
                                 {
                                     "text": "1. Why did the chicken join"
                                             " a band? Because it had the"
                                             " drumsticks ready!",
                                     "space": 1
                                 },
                                 {
                                     "text": "2. What do you call a"
                                             " chicken that haunts the barn? A"
                                             " poultry-geist!",
                                     "space": 0
                                 },
                                 {
                                     "text": "3. Why did the rooster go to"
                                             " the comedy show? To"
                                             " cockle-doodle-DOO its best"
                                             " impression!",
                                     "space": 0
                                 },
                                 {
                                     "text": "4. What does a chicken need"
                                             " to lay an egg every day?"
                                             " Hen-durance!",
                                     "space": 0
                                 },
                                 {
                                     "text": "5. How do chickens stay fit?"
                                             " Egg-ercise!",
                                     "space": 0
                                 },
                                 {
                                     "text": "6. What do you call a crazy"
                                             " chicken? A cuckoo cluck!",
                                     "space": 0
                                 },
                                 {
                                     "text": "7. Why did the chicken stop"
                                             " in the middle of the road? It saw"
                                             " the sign: 'Egg Xing'!",
                                     "space": 1
                                 }
                             ]
                         ),
                         Potion(
                             name="Small Potion",
                             health=25
                         ),
                     ],
                     position=(0, 1),
                     ),
                Area(name="Crystal Hills",
                     storyLine=[
                         {
                             "clear": True
                         },
                         {
                             "text": "After his long and arduous journey,"
                                     " Charlie, the brave chicken from Yolkaris, finally"
                                     " stood at the threshold of Crystal Hills. The"
                                     " path he had traversed had been fraught with"
                                     " challenges and perils, but he had endured,"
                                     " driven by the unwavering purpose of obtaining"
                                     " the Time Crystal."
                         },
                         {
                             "text": "Before him lay the Crystal Hills, a"
                                     " place of legend and wonder. The hills shimmered"
                                     " with the radiant glow of Time Crystals, each one"
                                     " a fragment of the past and the future. It had"
                                     " taken him many moons to reach this sacred place,"
                                     " and the weight of his quest rested heavily on"
                                     " his wings."
                         },
                         {
                             "text": "The air was thick with an aura of"
                                     " ancient magic, and the very ground beneath his"
                                     " feet seemed to vibrate with the essence of time"
                                     " itself. Charlie could feel the watchful eyes of"
                                     " the guardian, Phineas Blackthorn, as he neared"
                                     " the heart of the Crystal Hills."
                         },
                         {
                             "continue": True
                         },
                         {
                             "text": "As Charlie continued his journey through"
                                     " the surreal and disorienting landscape of"
                                     " crystals, he couldn't help but reflect on the"
                                     " trials that had brought him here. The Time"
                                     " Crystal, the key to saving Yolkaris from"
                                     " impending darkness, was within his grasp, but"
                                     " first, he had to face the formidable guardian"
                                     " and prove himself."
                         },
                         {
                             "text": "Phineas emerged from the shimmering"
                                     " crystals as if he were a part of the very fabric"
                                     " of time itself. His presence commanded the"
                                     " attention of the crystals that surrounded him,"
                                     " their luminous glow accentuating his enigmatic"
                                     " presence."
                         },
                         {
                             "text": "As Charlie stood before Phineas"
                                     " Blackthorn, the guardian of the Time"
                                     " Crystals, a tense atmosphere hung in the"
                                     " air. The guardian, an enigmatic figure with"
                                     " a monocle and an impeccably groomed feather"
                                     " coat, gazed at Charlie with a wry smile."
                         },
                     ],
                     storyLineVisited=[
                         {
                             "clear": True},
                         {
                             "text": "You are back in Crystal Hills",
                         }],
                     enemy=Enemy(
                         name="Phineas Blackthorn",
                         storyLine=[
                             {
                                 "continue": True
                             },
                             {
                                 "enemy": "Ah, young traveler, You've reached"
                                          " the heart of the Crystal Hills, but before"
                                          " you can claim the Time Crystal, there's a"
                                          " challenge you must face."
                             },
                             {
                                 "text": "Charlie furrowed his brow, awaiting"
                                         " Phineas's instructions."
                             },
                             {
                                 "enemy": "We shall have a test of your"
                                          " skills and intelligence. If you succeed,"
                                          " the Time Crystal will be yours. Fail, let's"
                                          " just say you'll be the butt of some"
                                          " egg-cellent jokes! Oh, ho ho! Ha ha ha! Hee"
                                          " hee! Ah, ha ha! Hohoho! Ha ha ha! Heeheehe!"
                                          " Ahahaha! Ho ho ho! Ha ha ha! Hee hee! Ah,"
                                          " ha ha! Hilarious! Ho ho ho! Ha ha ha! Hee"
                                          " hee! Ah, ha ha! Tremendous! Oh, ho ho! Ha"
                                          " Marvelous! Ho ho ho! Ha ha! Uncontrollable!"
                                          " Oh, ho ho! Ha ha! Hee hee! Oh, I am sorry,"
                             },
                             {
                                 "continue": True
                             },
                             {
                                 "text": "Phineas finally said, his laughter"
                                         " subsiding."
                             },
                             {
                                 "enemy": "Do you accept the challenge?"
                                          " Ha ha ha! Hee hee! Ah, ha ha! Hilarious!"
                             }
                         ],
                         storyLineVisited=[
                             {
                                 "enemy": "Hey, welcome back, Charlie! Are you"
                                          " ready this time to take on the challenge?"
                                          " Can we fight? Ha ha ha! Sorry.",
                             },
                         ],
                         storyLineFought=[
                             {
                                 "enemy": "Ah, Charlie, back for another"
                                          " round, I see. Ready to continue where we"
                                          " left off, or have you come to reconsider?"
                                          " The challenge awaits.",
                             },
                         ],
                         storyLineWonFight=[
                             {
                                 "text": "You have defeated Phineas Blackthorn."
                                         " With a gracious nod and a smile, Phineas"
                                         " Blackthorn conceded."
                             },
                             {
                                 "enemy": "Well done, Charlie. You've proven"
                                          " yourself worthy. You can now go and take"
                                          " the Time Crystal; you have earned it."
                             }
                         ],
                         storyLineLostFight=[
                             {
                                 "text": "Phineas Blackthorn couldn't help"
                                         " but raise an eyebrow and quip"
                             },
                             {
                                 "enemy": "Well, Charlie, I suppose you'll"
                                          " have to stick to egg-citing adventures for"
                                          " now. The Time Crystal remains elusive, like"
                                          " a chicken chasing its tail!"
                             },
                             {
                                 "text": "Game Over!",
                             },
                             {
                                 "continue": True
                             },
                             {
                                 "gameover": True
                             }
                         ],
                         storyLineDefeated=[
                             {
                                 "text": "What else do you need, Charlie?"
                                         " You've already bested me in our challenge,"
                                         " and I have no more tests to offer.",
                             },
                         ],
                         health=50,
                         attack=40,
                         defense=20
                     ),
                     items=[Item(name="The Time Crystal")
                            ],
                     position=(3, 1),
                     ),
                Area(name="Yonder Forest",
                     storyLine=[
                         {
                             "clear": True
                         },
                         {
                             "text": "Yonder Forest loomed ahead, a dense"
                                     " canopy of ancient trees whispering secrets from"
                                     " centuries past. Its shadowy depths, untouched by"
                                     " time, held both allure and mystery."
                         },
                         {
                             "text": "Charlie paused at the forest's edge, the"
                                     " cool shade brushing against his feathers like a"
                                     " promise of the unknown. 'This forest has seen"
                                     " more seasons than we can fathom,' he thought,"
                                     " 'each tree a silent guardian of history.'"
                         },
                         {
                             "player": "I better keep moving and make it"
                                       " through this forest before night falls. It's"
                                       " wise not to linger here when the shadows grow"
                                       " long. There's no telling what lurks in the dark."
                         },
                         {
                             "text": "Taking a deep breath, Charlie stepped"
                                     " forward. The forest floor felt soft underfoot,"
                                     " inviting him deeper into the green shadows."
                         },
                         {
                             "continue": True
                         }
                     ],
                     storyLineVisited=[
                         {
                             "clear": True
                         },
                         {
                             "text": "You are back in Yonder Forest",
                         }
                     ],
                     enemy=Enemy(
                         name="Shadow Stalker",
                         storyLine=[
                             {
                                 "enemy": "You've entered my domain, little"
                                          " chicken. But know this, none shall cross"
                                          " these woods without challenging me. It is"
                                          " the law of the shadows."
                             },
                             {
                                 "text": "The Shadow Stalker's voice was"
                                         " chilling, echoing through the darkened"
                                         " forest, causing the leaves to shiver and the"
                                         " air to grow heavy with tension. Charlie"
                                         " stood firm, ready to face the impending"
                                         " challenge."
                             },
                             {
                                 "player": "Why do you enforce such a law,"
                                           " Shadow Stalker? What drives you to demand"
                                           " challenges from those who enter?"
                             },

                             {
                                 "enemy": "I seek to prove my dominance,"
                                          " Charlie. I crave the thrill of battle and"
                                          " the taste of victory. The law of the shadows"
                                          " is my way, and you, by entering, have"
                                          " accepted the challenge."
                             }
                         ],
                         storyLineVisited=[
                             {
                                 "enemy": "You're back, Charlie. I hope you"
                                          " brought your feather duster this time!"
                             },
                         ],
                         storyLineFought=[
                             {
                                 "enemy": "You've returned, Charlie. Ready"
                                          " to face me again?"
                             },
                         ],
                         storyLineWonFight=[
                             {
                                 "text": "You have defeated the Shadow"
                                         " Stalker."
                             },
                             {
                                 "text": "The creature vanished into the"
                                         " shadows, defeated. As the darkness receded,"
                                         " a faint whisper reached Charlie's ears."
                             },
                             {
                                 "enemy": "You may have bested me, but your"
                                          " quest is far from over, Charlie. Seek the"
                                          " mighty Feathered Blade that once belonged"
                                          " to the legendary warrior, Sir Cluckington."
                                          " The elusive Feathered Blade can be found"
                                          " concealed within the depths of the Yonder"
                                          " Forest, waiting for a worthy owner."
                             },
                             {
                                 "text": "The creature vanished into the"
                                         " shadows, defeated. As the darkness receded,"
                                         " a faint whisper reached Charlie's ears."
                             }
                         ],
                         storyLineLostFight=[
                             {
                                 "text": "The Shadow Stalker's eyes gleamed"
                                         " with malice as it spoke."
                             },
                             {
                                 "enemy": "You're no match for me, little"
                                          " chicken. You'll never leave this forest."
                             },
                             {
                                 "text": "Game Over!",
                             },
                             {
                                 "continue": True
                             },
                             {
                                 "gameover": True
                             }
                         ],
                         storyLineDefeated=[
                             {
                                 "enemy": "You've defeated me, Charlie. I have"
                                          " no more fight left in me."
                             },
                         ],
                         health=30,
                         attack=5,
                         defense=30
                     ),
                     items=[
                         Weapon(
                             name="Feathered Blade",
                             description="A blade made from the"
                                         " finest feathers, light and sharp.",
                             attack=18,
                             actions=[
                                 "Slice",
                                 "Stab",
                                 "Thrust"
                             ]
                         ),
                     ],
                     ),
                Area(name="Clucker's Canyon",
                     storyLine=[
                         {
                             "clear": True
                         },
                         {
                             "text": "Clucker's Canyon, with its echoing"
                                     " walls and towering red cliffs, is a marvel of"
                                     " nature on Yolkaris. The canyon has witnessed"
                                     " the rise and fall of many civilizations,"
                                     " holding secrets of the past within its rugged"
                                     " landscape. It's said that the echoes in the"
                                     " canyon are the voices of ancient Yolkarians."
                         },
                         {
                             "text": "The canyon is not just a historical"
                                     " site but also a treasure trove of mystery."
                                     " Explorers and treasure hunters often delve"
                                     " into its depths, seeking lost artifacts of the"
                                     " chicken civilizations that once flourished"
                                     " here."
                         },
                         {
                             "player": "I wonder what stories these cliffs"
                                       " could tell if they could talk. Ancient voices..."
                                       " I hope they can guide me on my quest. Mystery"
                                       " and treasure... sounds like an adventure waiting"
                                       " to happen. Lost artifacts... maybe they hold"
                                       " clues about The Time Crystal."
                         }
                     ],
                     storyLineVisited=[
                         {
                             "clear": True
                         },
                         {
                             "text": "You are back in Clucker's Canyon",
                         }
                     ],
                     items=[
                         Potion(
                             name="Medium Potion",
                             health=50
                         )
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
                     storyLineVisited=[
                         {
                             "clear": True
                         },
                         {
                             "text": "You are back in Bubble Beach",
                         }
                     ],
                     items=[
                         Potion(
                             name="Small Potion",
                             health=25
                         )
                     ],
                     ),
                Area(name="Peckers Peak",
                     storyLine=[
                         {
                             "clear": True
                         },
                         {
                             "text": "Peckers Peak, the crowning glory of Yolkaris,"
                                     " stands tall, its heights veiled in the whispers"
                                     " of ancient tales. This revered summit, where the"
                                     " skies kiss the earth, was once the sacred"
                                     " observatory of the elder chickens."
                         },
                         {
                             "text": "Here, under the canvas of the cosmos, they"
                                     " unraveled the mysteries of the stars, leaving a"
                                     " legacy etched in the winds. As Charlie's path"
                                     " ascends, each step is a journey through time."
                         },
                         {
                             "text": "The winds carry legends, and the stones are"
                                     " etched with the wisdom of ages. Reaching the"
                                     " peak, Charlie is enveloped in a world of awe,"
                                     " the horizon stretching infinitely."
                         },
                         {
                             "text": "The air is thick with the essence of bygone eras,"
                                     " and the silence speaks of hidden truths. Atop"
                                     " this celestial altar, where the ancient chickens"
                                     " once gazed upon the heavens."
                         },
                         {
                             "continue": True
                         },
                         {
                             "text": "Charlie feels an overwhelming connection to the"
                                     " stars. Their ancient wisdom, like a forgotten"
                                     " song, resonates within him, guiding his heart."
                                     " The whispers of Peckers Peak instill in him a"
                                     " sense of purpose."
                         },
                         {
                             "player": "Wow, the view from here is incredible!"
                                       " I can see the whole of Yolkaris and Crystal Hills."
                                       " It's said that the ancient chickens gazed at the stars"
                                       " from here, plotting their courses across the skies. If"
                                       " only I had their knowledge now..."
                         },
                         {
                             "continue": True
                         }
                     ],
                     storyLineVisited=[
                         {
                             "clear": True
                         },
                         {
                             "text": "You are back in Peckers Peak",
                         }
                     ],
                     enemy=Enemy(
                         name="Viktor Thornhart",
                         storyLine=[
                             {
                                 "enemy": "You've ventured into my territory,"
                                          " stranger. Prepare to face the consequences."
                             },
                             {
                                 "player": "Who are you, and why do you guard"
                                           " this place?"
                             },
                             {
                                 "enemy": "I am Viktor Thornhart, protector of"
                                          " these hallowed grounds. The secrets hidden"
                                          " here are not for the untested. If you wish"
                                          " to proceed, you must prove your worth."
                             },
                             {
                                 "text": "The tension in the air thickens as"
                                         " you prepare to face Viktor, the enigmatic"
                                         " guardian of these sacred grounds."
                             }
                         ],
                         storyLineVisited=[
                             {
                                 "enemy": "You've returned, Charlie. Ready"
                                          " to face me again?"
                             },
                         ],
                         storyLineFought=[
                             {
                                 "enemy": "You've returned, Charlie. Ready"
                                          " to face me again?"
                             },
                         ],
                         storyLineWonFight=[
                             {
                                 "text": "With a final, determined effort, you"
                                         " overcome Viktor Thornhart's defenses."
                             },
                             {
                                 "enemy": "You've proven your mettle, Charlie."
                                          "I yield."
                             },
                             {
                                 "text": "Viktor's stern demeanorc softens,"
                                         " acknowledging your strength."
                             },
                             {
                                 "enemy": "I'll share a secret with you,"
                                          " Charlie. In the heart of these peaks,"
                                          " you'll find the Feathered Armor."
                             },
                             {
                                 "text": "Viktor's words pique your curiosity"
                                         " as he reveals the existence of the finest"
                                         " armor, crafted from the lightest and"
                                         " strongest feathers known."
                             }
                         ],
                         storyLineLostFight=[
                             {
                                 "text": "Viktor Thornhart's eyes gleamed"
                                         " with malice as he spoke."
                             },
                             {
                                 "enemy": "You're no match for me, little"
                                          " chicken. You'll never leave this place."
                             },
                             {
                                 "text": "Game Over!",
                             },
                             {
                                 "continue": True
                             },
                             {
                                 "gameover": True
                             }
                         ],
                         storyLineDefeated=[
                             {
                                 "enemy": "You've defeated me, Charlie. I have"
                                          " no more fight left in me."
                             },
                         ],
                         health=30,
                         attack=5,
                         defense=30
                     ),
                     items=[
                         Armour(
                             name="Feathered Armor",
                             description="Armor made from the finest"
                                         " feathers, light and strong.",
                             defense=20
                         ),
                     ]
                     )
            ]

            mystara_areas = []

            luminara_areas = []

        elif level == 2:

            yolkaris_size = (2, 2)
            mystara_size = (2, 3)
            luminara_size = (3, 3)

            yolkaris_areas = [
                Area(name="Capital City",
                     storyLine=[
                         {
                             "clear": True
                         },
                         #  {
                         #      "text": "The Dark Dust",
                         #      "delay": 0.6,
                         #      "space": 1
                         #  },
                         #  {
                         #      "text": "In the shadow of an ever-expanding universe, where celestial bodies dance in the"
                         #              " silent ballet of the cosmos, there lies a planet now cloaked in darkness. The Dark Dust,"
                         #              " a cosmic malaise born from the deepest recesses of space, has descended upon this world,"
                         #              " veiling it from the life-giving rays of its star. Ecosystems falter, and despair grips"
                         #              " the inhabitants as their vibrant home edges toward oblivion."
                         #  },
                         #  {
                         #      "text": "Against this backdrop of encroaching doom, the Aurora Orb emerges from the annals"
                         #              " of legend. Crafted in the forge of time by beings whose existence predates the stars"
                         #              " themselves, this Orb is said to radiate with an ethereal light, powerful enough to"
                         #              " scatter the Dark Dust and restore balance to the cosmos."
                         #  },
                         #  {
                         #      "text": "Charlie, a remarkable chicken chosen by destiny, ventures beyond the stars on a"
                         #              " mission to find the Aurora Orb. His journey, rich with cosmic mysteries and guarded by"
                         #              " ancient beings, showcases the bravery that dwells within the most unexpected champions."
                         #  },
                         #  {
                         #      "continue": True
                         #  }
                     ],
                     storyLineVisited=[
                         {
                             "clear": True
                         },
                         {
                             "text": "You are back in Capital City"
                         },
                     ],
                     items=[],
                     neutral=Neutral(
                         name="Archibald Thorne",
                         questItem=Item(name="Aurora Orb"),
                         storyLine=[
                             #  {
                             #      "text": "Archibald Thorne, a seasoned "
                             #              "navigator of the cosmos, leaned "
                             #              "closer, his voice a blend of "
                             #              "wisdom and urgency. ",

                             #  },
                             #  {
                             #      "neutral": "Charlie, the fate of our world "
                             #                 "hangs in the balance. The Dark "
                             #                 "Dust threatens to consume all "
                             #                 "that is vibrant and alive. But "
                             #                 "you, my friend, have a destiny "
                             #                 "that extends beyond the stars."
                             #  },
                             #  {
                             #      "neutral": "Your journey will take you beyond "
                             #                 "the known, through the tapestry of stars, "
                             #                 "to worlds that have only existed in the "
                             #                 "whispers of the old. You must find the "
                             #                 "Aurora Orb and bring its light back to "
                             #                 "Yolkaris."
                             #  },
                             #  {
                             #      "text": "He paused, ensuring Charlie's full "
                             #              "attention.",
                             #  },
                             #  {
                             #      "neutral": "To embark on this pivotal journey, you'll need a vessel unlike any other."
                             #                 " Seek out the enigmatic engineer, Eudora Quasar. She possesses the Nebula Voyager II,"
                             #                 " a marvel of cosmic engineering. This ship, compact as an egg yet vast as your"
                             #                 " courage, will be your chariot among the stars.",
                             #      "space": 0
                             #  },
                             #  {
                             #      "neutral": "Your first destination is Mystara, a planet veiled in mystery and ancient"
                             #                 " secrets. There, you will find the clues necessary to guide you on your quest for the"
                             #                 " Aurora Orb. Remember, the Nebula Voyager II is not just your transport; it's the key"
                             #                 " to navigating the challenges that lie between the realms of known and unknown.",
                             #      "space": 0
                             #  },
                             #  {
                             #      "text": "He handed Charlie a celestial map, marked with coordinates and symbols"
                             #              " indecipherable to the uninitiated."
                             #  },
                             #  {
                             #      "neutral": "The journey ahead is perilous, fraught with wonders and dangers alike. But"
                             #                 " I believe in you, Charlie. You have within you the heart of a voyager, capable of"
                             #                 " braving the infinite night."
                             #  },
                             #  {
                             #      "continue": True
                             #  },
                             #  {
                             #      "clear": True
                             #  },
                             #  {
                             #      "text": "Embark on the Yolkaris Odyssey with"
                             #              " these words of guidance:"
                             #  },
                             #  {
                             #      "text": "In this tale, your journey begins"
                             #              " in Yolkaris, a realm of myths and"
                             #              " mysteries."
                             #  },
                             #  {
                             #      "text": "- Use the 'map' command to find your"
                             #              " path within this enchanted land.",
                             #      "space": 0
                             #  },
                             #  {
                             #      "text": "- Traverse the land through 'north',"
                             #              " 'south', 'east', and 'west'. Discover your"
                             #              " destiny.",
                             #      "space": 0
                             #  },
                             #  {
                             #      "text": "- In your quest, 'search' the areas"
                             #              " for hidden treasures and secrets.",
                             #      "space": 0
                             #  },
                             #  {
                             #      "text": "- Keep your inventory filled with"
                             #              " artifacts and tools. Check it with the"
                             #              " 'inventory' command.",
                             #      "space": 0
                             #  },
                             #  {
                             #      "text": "- When your health is low, 'potion'"
                             #              " can be used to restore your vitality.",
                             #      "space": 0
                             #  },
                             #  {
                             #      "text": "- Keep an eye on your 'stats' to"
                             #              " track your progress.",
                             #      "space": 0
                             #  },
                             #  {
                             #      "text": "- If you require guidance, simply"
                             #              " type 'help' to view a list of available"
                             #              " commands.",
                             #      "space": 0
                             #  },
                             #  {
                             #      "text": "- To begin anew or end your"
                             #              " adventure, use 'reset' or 'quit' anytime."
                             #  },
                             #  {
                             #      "text": "Good fortune on your quest. May your"
                             #              " journey be filled with wonder.",
                             #      "space": 0
                             #  },
                         ],
                         storyLineVisited=[
                             {
                                 "text": "The hallowed halls of the observatory felt heavier as Charlie stepped in, the weight of unmet expectations pressing down."
                             },
                             {
                                 "neutral": "Archibald Thorne, peering through his grand telescope, turned, his gaze filled with a mix of anticipation and concern.",
                                 "space": 1,
                             },
                             {
                                 "neutral": "Charlie, my boy, what news do you bring from the stars?",
                                 "space": 0,
                             },
                             {
                                 "player": "I've journeyed far and wide, Archibald, yet the Aurora Orb remains beyond my grasp.",
                                 "space": 0,
                             },
                             {
                                 "neutral": "Ah, the cosmos is vast and its secrets well-guarded. Do not despair, Charlie. This is but a setback on a path filled with many. The Orb is out there, waiting for one worthy and persistent enough to uncover it.",
                                 "space": 1,
                             },
                             {
                                 "neutral": "Return to the stars, Charlie. Your quest is far from over, and Yolkaris' hope still shines bright within you. Remember, the journey itself forges the hero, not merely the triumph.",
                                 "space": 1,
                             },
                             {
                                 "text": "With a renewed sense of purpose, Charlie nodded, the determination to succeed reigniting within him. The quest for the Aurora Orb was far from over, and his journey through the cosmos awaited.",
                                 "space": 1,
                             },
                             {
                                 "continue": True
                             }
                         ],
                         storyLineCompleted=[
                             {
                                 "text": "As Charlie stepped into the observatory, a hush fell over the gathered crowd, anticipation hanging thick in the air."
                             },
                             {
                                 "neutral": "Archibald Thorne, his eyes gleaming with hope, turned from his telescope to face Charlie, the room's silence pregnant with expectation.",
                                 "space": 1,
                             },
                             {
                                 "neutral": "Is it true, Charlie? Have you brought back the light to Yolkaris?",
                                 "space": 0,
                             },
                             {
                                 "player": "Yes, Archibald. The Aurora Orb is with me. We can now cleanse the dark dust from our skies.",
                                 "space": 0,
                             },
                             {
                                 "text": "A collective gasp filled the observatory as Charlie held up the Orb. Its glow, soft yet potent, seemed to pulse with the heartbeat of the planet itself.",
                                 "space": 1,
                             },
                             {
                                 "neutral": "Incredible! Charlie, you've done more than just retrieve an ancient relic; you've given us all a future. Let's waste no time. To the activation chamber!",
                                 "space": 1,
                             },
                             {
                                 "text": "The assembly moved to the chamber, where the Orb was carefully set into its ancient cradle. Archibald initiated the activation sequence, and the Orb's light intensified, beams shooting skywards.",
                                 "space": 1,
                             },
                             {
                                 "text": "Outside, the dark dust began to dissipate like shadows at dawn, revealing the azure skies of Yolkaris. The sunlight, warm and life-giving, touched the planet once more, coaxing life back into the world.",
                                 "space": 1,
                             },
                             {
                                 "neutral": "You've done it, Charlie! Yolkaris is saved!",
                                 "space": 1,
                             },
                             {
                                 "text": "Cheers erupted, echoing through the observatory and beyond, as people everywhere rejoiced. Charlie, amidst the celebration, knew that this moment marked not just the end of a journey, but the dawn of a new era for Yolkaris.",
                                 "space": 1,
                             },
                             {
                                 "text": "Game Over!",
                             },
                             {
                                 "continue": True
                             },
                             {
                                 "gameover": True
                             }
                         ]
                     ),
                     position=(0, 0),
                     ),
                Area(name="Bounty Harbour",
                     storyLine=[
                         {
                             "clear": True
                         },
                         {
                             "text": "Bounty Harbour bustles with life, a hub "
                                     " for seafaring souls and wandering traders. The"
                                     " aroma of the ocean mingles with exotic spices,"
                                     " weaving a tapestry of adventure and mystery in"
                                     " the air."
                         },
                         {
                             "text": "Charlie, amidst the vibrant chatter of"
                                     " the marketplace and rhythmic creaking of ships,"
                                     " takes in the colorful tapestry of sails and"
                                     " flags, each narrating tales of distant lands"
                                     " and mysterious seas."
                         },
                     ],
                     storyLineVisited=[
                         {
                             "clear": True
                         },
                         {
                             "text": "You are back in Bounty Harbour",
                         }
                     ],
                     items=[],
                     ),
                Area(name="Gearhaven District",
                     storyLine=[
                         {
                             "clear": True
                         },
                         {
                             "text": "Charlie's journey led him to the heart of Gearhaven District, a place where the"
                                     " past and future collided amidst gears and gizmos. Nestled within this industrial bastion"
                                     " was Eudora Quasar's workshop, a veritable cavern of wonders where metal met magic under"
                                     " her skilled hands."
                         },
                     ],
                     storyLineVisited=[
                         {
                             "clear": True
                         },
                         {
                             "text": "You are back in Gearhaven District",
                         }
                     ],
                     items=[],
                     neutral=Neutral("Eudora Quasar",
                                     storyLine=[
                                         {
                                             "neutral": "Ah, Charlie,",
                                         },
                                         {
                                             "text": "she exclaimed, her voice echoing slightly in the vast space."
                                         },
                                         {
                                             "neutral": "I've been expecting you. Archibald sent word of your quest. It's not"
                                             " every day we get to send someone off to the stars."
                                         },
                                         {
                                             "text": "She led Charlie to a peculiar object covered by a tarp. With a dramatic flourish,"
                                             " she unveiled the Nebula Voyager II. The small, egg-shaped vessel sat innocuously on the"
                                             " workbench, its surface smooth and enigmatic."
                                         },
                                         {
                                             "neutral": "This,is the Nebula Voyager II. A marvel of engineering, if I do say so myself."
                                             " It can carry you across the galaxies, transforming from this compact egg to a fully"
                                             " equipped starship at your command."
                                         },
                                         {
                                             "item": Spaceship(
                                                 name="Nebula Voyager II",
                                                 description="The Nebula Voyager II stands as a marvel of cosmic engineering,"
                                                 "seamlessly blending elegance with functionality. This compact vessel transforms from the"
                                                 " size of an egg into a sleek, two-to-three-seater starship, designed for ease of"
                                                 " transport and rapid interstellar travel. Its hull, reflecting the myriad colors of deep"
                                                 " space, houses a hyperdrive capable of swift journeys across galaxies, while its"
                                                 " transparent cockpit offers breathtaking views of the cosmos. Inside, the Voyager's"
                                                 " efficient layout includes life-support systems, advanced navigation controls, and ample"
                                                 " storage, all within a space that maximizes comfort for its adventurers. It's more than"
                                                 " a ship; it's a gateway to the unknown, crafted for those brave enough to explore the"
                                                 " mysteries of the universe. The Nebula Voyager II is a testament to the spirit of"
                                                 " exploration, inviting its passengers to embark on journeys beyond the stars."
                                             )
                                         },
                                         {
                                             "text": "You have received an item: Nebula Voyager II"
                                         },
                                         {
                                             "text": "Charlie examined the Nebula Voyager II, a mix of awe and curiosity in his eyes."
                                             " Eudora explained its operation, how a twist and a press could unfold the universe's"
                                             " mysteries before him."
                                         },
                                         {
                                             "neutral": "As you embark on your journey to Mystara and beyond, remember, the path will"
                                             " not be easy, but the Nebula is more than a vessel. It's a companion, one that will"
                                             " guide you through the darkest reaches and bring you home."
                                         },
                                         {
                                             "text": "Charlie nodded, his heart swelling with gratitude and determination."
                                         },
                                         {
                                             "player": "Thank you, Eudora. I won't let you down."
                                         },
                                         {
                                             "text": "As he left the workshop, the Nebula Voyager II in hand, Charlie felt the weight"
                                             " of his mission anew. But with the support of friends like Eudora and the ingenuity of"
                                             " Gearhaven District behind him, he knew he was ready to face whatever the cosmos held."
                                         }
                                     ],
                                     storyLineVisited=[
                                         {
                                             "neutral": "Charlie, back so soon? How's the Nebula Voyager II treating you?",
                                             "space": 0,
                                         },
                                         {
                                             "player": "It's been fantastic, Eudora. Couldn't have gotten far without it.",
                                             "space": 0,
                                         },
                                         {
                                             "neutral": "Great to hear. Remember, every adventure is a chance to learn something new. Safe travels, Charlie.",
                                             "space": 1,
                                         },
                                         {
                                             "continue": True
                                         }
                                     ]
                                     ),
                     ),
                Area(name="Cluckington Valley",
                     storyLine=[
                         {
                             "clear": True
                         },
                         {
                             "text": "Cluckington Valley unfolds beneath the watchful gaze of ancient peaks, a lush expanse teeming with life. Its fields, radiant with a green vibrancy, pulse with the earth's own rhythms, while wildflowers perform silent symphonies for a buzzing audience of bees.",
                             "space": 1
                         }
                     ],
                     storyLineVisited=[
                         {
                             "clear": True
                         },
                         {
                             "text": "Returning to Cluckington Valley",
                             "space": 1
                         }
                     ],
                     items=[
                         {
                             "item": Potion(name="Small Potion", health=25),
                             "quantity": 1
                         }
                     ],
                     )
            ]

            mystara_areas = [
                Area(name="Astral Port",
                     storyLine=[
                         {
                             "clear": True
                         },
                         {
                             "text": "Astral Port, where the pulse of intergalactic trade beats strong. Ships from"
                                     " across the universe dock here, their hulls brimming with goods from distant worlds. The"
                                     " air hums with the languages of a thousand planets, a testament to the port's role as a"
                                     " crossroads of the cosmos."
                         },
                     ],
                     storyLineVisited=[
                         {
                             "clear": True
                         },
                         {
                             "text": "Returning to Astral Port"
                         }
                     ],
                     ),
                Area(name="Quantum Quarters",
                     storyLine=[
                         {
                             "text": "Quantum Quarters, a district where the future is now. The architecture defies"
                                     " gravity, and technology unseen on any other planet makes daily life a constant marvel."
                                     " Here, the impossible is just another part of the day."
                         }
                     ],
                     storyLineVisited=[
                         {
                             "text": "Returning to Quantum Quarters"
                         }
                     ],
                     ),
                Area(name="Moonlight Market",
                     storyLine=[
                         {
                             "text": "Moonlight Market, illuminated by the soft glow of the twin moons. Stalls"
                                     " overflow with exotic spices, rare artifacts, and treasures untold. It's a treasure"
                                     " hunter's dream, a place where fortunes can be found or lost with a single deal."
                         }
                     ],
                     storyLineVisited=[
                         {
                             "text": "Returning to Moonlight Market"
                         }
                     ],
                     enemy=Enemy(
                         name="Nomo Gerhad",
                         storyLine=[
                             {
                                 "text": "Ambling through the Moonlight Market's labyrinth of stalls, Charlie immerses himself in the vibrant tapestry of cosmic commerce. His senses are alive with the exotic scents of alien spices and the colorful displays of interstellar artifacts. It's a place where the universe converges, offering treasures from every corner of the galaxy."
                             },
                             {
                                 "text": "His wanderlust momentarily sated by small purchases, Charlie's attention is suddenly snatched by a familiar figure darting through the throng. 'Caesar!' he calls out, recognizing the silhouette of an old friend. With a mix of excitement and curiosity, he weaves through the crowd, his calls drowned by the cacophony of the market."
                             },
                             {
                                 "text": "The figure leads him into a shadow-clad alley, away from the luminous glow of the stalls. The bustling sounds of the market fade into an eerie silence, replaced by the muted echoes of their footsteps. 'Caesar, wait!' Charlie urges, but as the figure turns, a chilling transformation unfolds."
                             },
                             {
                                 "text": "Before Charlie stands not Caesar, but a creature with a pale, featureless face, its form shifting unsettlingly. This is Nomo Gerhad, known amongst the market's shadows as a shapeshifting thief. Unlike his kin, who often use their gifts for benign purposes, Nomo preys on the unsuspecting, luring them with the guise of familiar faces."
                             },
                             {
                                 "text": 'With a sinister grace, Nomo produces a knife, its blades gleaming ominously in the dim light. "Empty your pockets, little one," he hisses, a threat veiled in quiet menace.'
                             },
                             {
                                 "player": "You've picked the wrong target. I won't be parting with my belongings today."
                             },
                             {
                                 "text": "Faced with a dire choice, Charlie must quickly decide: confront Nomo Gerhad in a desperate bid for self-defense or attempt to outpace the thief's malevolence in a sprint for safety."
                             }
                         ],
                         storyLineVisited=[
                             {
                                 "enemy": "'Fancy seeing you here again,' Nomo taunts, a smirk playing on his lips. 'Ready for another lesson, or will you surprise me this time?'"
                             },
                         ],
                         storyLineFought=[
                             {
                                 "enemy": "Bruised from their last encounter, Charlie faces Nomo with a newfound resolve. 'You won't best me again,' he declares, the market's ambient light glinting off his determination."
                             },
                         ],
                         storyLineWonFight=[
                             {
                                 "text": "With a decisive blow, Charlie bests Nomo Gerhad, watching as the creature's guise fades, leaving behind only the truth of his deceit. 'Your tricks end here,' Charlie proclaims, victorious."
                             },
                         ],
                         storyLineLostFight=[
                             {
                                 "text": "Overwhelmed by Nomo's guile, Charlie stumbles, the market's din fading as darkness claims him. 'Better luck next time,' Nomo's voice echoes mockingly in the void."
                             },
                         ],
                         storyLineDefeated=[
                             {
                                 "text": "Ambling through the market once more, Charlie's eyes meet Nomo's. There's no malice this time, only a nod of respect. 'You've earned your peace,' Nomo concedes, disappearing into the crowd."
                             },
                         ],
                         health=60,
                         attack=20,
                         defense=10,
                         fought=False
                     ),
                     ),
                Area(name="Observatory",
                     storyLine=[
                         {
                             "text": "The Observatory, a temple to the stars where ancient and modern knowledge"
                                     " converge. Astronomers and seers alike peer into the depths of space, seeking answers"
                                     " to questions as old as time itself"
                         }
                     ],
                     storyLineVisited=[
                         {
                             "text": "Returning to Observatory"
                         }
                     ],
                     neutral=Neutral(
                         name="SpaceWalker Jones",
                         storyLine=[
                             {
                                 "text": "In the heart of Astral Port, amidst the hum of intergalactic commerce and the kaleidoscope of alien diversity, Charlie spots a familiar face. Spacewalker Jones, his old friend from the distant and peculiar planet Earth, approaches with a wide grin.",
                                 "space": 1
                             },
                             {
                                 "text": "Jones, whose tales of adventure span the cosmos, greets Charlie with the warmth of a thousand suns. 'Charlie, my friend! It's been too long,' he exclaims, clapping Charlie on the back. 'How's the quest going?'",
                                 "space": 1
                             },
                             {
                                 "text": "Over cups of steaming galactic brew, Jones listens intently to Charlie's tale of Yolkaris and the encroaching Dark Dust. With each word, his eyes twinkle with the promise of adventure and knowledge.",
                                 "space": 1
                             },
                             {
                                 "text": "'Ah, the Aurora Orb, you say? Fascinating!' Jones muses, leaning back. 'I've heard whispers of such artifacts during my travels. Powers beyond imagination... But it's the Old Citadel that you should seek out. Within its walls lie secrets ancient and profound.'",
                                 "space": 1
                             },
                             {
                                 "text": "Charlie, heartened by Jones's guidance, feels a renewed vigor. 'Thank you, Jones. I knew you'd have some wisdom to share,' he says, a smile breaking across his face.",
                                 "space": 1
                             },
                             {
                                 "text": "'Remember, Charlie,' Jones replies, his gaze piercing the starlit void outside, 'the universe is vast, filled with mysteries waiting to be unraveled. Keep your curiosity alive; it's the most powerful tool you have.'",
                                 "space": 1
                             },
                             {
                                 "text": "With a final hearty laugh, Jones melds back into the tapestry of the port, leaving Charlie to ponder the journey ahead. The brief reunion, a reminder of the bonds forged across the stars, propels Charlie forward, the Old Citadel and its secrets calling to him.",
                                 "space": 1
                             }
                         ]
                     )),
                Area(name="Sanctuary",
                     storyLine=[
                         {
                             "text": "Sanctuary, a haven of peace in a universe of chaos. Here, weary travelers find"
                                     " solace among verdant gardens and tranquil waters, a place to rest and rejuvenate"
                                     " before continuing on their cosmic journeys."
                         }
                     ],
                     storyLineVisited=[
                         {
                             "text": "Returning to Sanctuary"
                         }
                     ],
                     enemy=Enemy(
                         name="Viktor Draven",
                         storyLine=[
                             {
                                 "text": "In the serene silence of Sanctuary, a shadow looms large, casting an ominous pall over the hallowed grounds. Standing at its heart is Viktor Draven, once a revered guardian of the Sanctuary, now turned rogue. His betrayal is shrouded in mystery, a tale of power corrupting absolutely."
                             },
                             {
                                 "text": "Viktor's eyes, once bright with the light of protection, now glint with malevolence. 'So, you seek the Aurora Orb,' he muses, a cold smile playing upon his lips. 'A noble quest, but one that ends here, with me.'"
                             },
                             {
                                 "enemy": "'Prepare yourself, for I will not let you pass. The secrets of the Sanctuary are mine to guard, even from the likes of you,' Viktor declares, his voice echoing ominously."
                             }
                         ],
                         storyLineVisited=[
                             {
                                 "text": "Charlie's return to the Sanctuary brings him face-to-face once more with Viktor Draven. The air crackles with tension, the unresolved conflict between them palpable."
                             },
                             {
                                 "enemy": "'You show great tenacity to return here, but it will not be enough. I stand firm, unwavering. Leave now, or face defeat,' Viktor warns, his stance unyielding."
                             }
                         ],
                         storyLineFought=[
                             {
                                 "enemy": "'Our last encounter was merely a preview. Now, witness the true extent of my power,' Viktor boasts, readying himself for the impending clash."
                             }
                         ],
                         storyLineWonFight=[
                             {
                                 "text": "With Viktor Draven bested, the Sanctuary's oppressive atmosphere lifts, replaced by a hopeful clarity. Charlie stands victorious, a beacon of resolve in the face of darkness.",
                             }
                         ],
                         storyLineLostFight=[
                             {
                                 "text": "'You have fought valiantly but in vain,' Viktor sneers, looming over Charlie. 'The Sanctuary remains under my watch, its secrets sealed away.'"
                             }
                         ],
                         storyLineDefeated=[
                             {
                                 "text": "As Charlie revisits the now peaceful Sanctuary, he reflects on his victory over Viktor Draven. The guardian's fall from grace serves as a somber reminder of the fine line between protector and tyrant."
                             }
                         ],
                         health=60,
                         attack=20,
                         defense=10,
                         fought=False
                     ),
                     ),
                Area(name="Old Citadel",
                     storyLine=[
                         {
                             "text": "The Old Citadel, a monument to epochs past, whispers tales of glory and ruin. As Charlie steps into its shadowed halls, he is met not by silence, but by a voice as clear as crystal."
                         },
                     ],
                     storyLineVisited=[
                         {
                             "text": "Returning to the Old Citadel"
                         }
                     ],
                     enemy=Enemy(
                         name="Calista Starcross",
                         storyLine=[

                             {
                                 "text": "Before him stands Calista Starcross, guardian of the Citadel's deepest secrets. Her eyes, glowing with an ethereal light, fix upon Charlie. 'You tread on sacred ground, seeker. What brings you to the heart of history?' she inquires, her tone a blend of curiosity and caution."
                             },
                             {
                                 "text": "Charlie, taken aback by her sudden appearance, senses the weight of the moment. Here stands a being tied to the Citadel's ancient legacy, offering not just confrontation but a test of worth."
                             },
                             {
                                 "player": "'I seek the truths buried within these walls,' Charlie responds, his resolve firm. 'And I will face whatever trials you deem necessary.'"
                             },
                             {
                                 "enemy": "'Very well,' Calista nods, stepping back as the air around her crackles with arcane energy. 'Show me that your purpose is true, and perhaps the Citadel will reveal its secrets to you.'"
                             }
                         ],
                         storyLineVisited=[
                             {
                                 "enemy": "'You return, still seeking the Citadel's secrets,' Calista observes as Charlie reenters the ancient halls. 'Have you discovered the courage to face what lies ahead?'"
                             }
                         ],
                         storyLineFought=[
                             {
                                 "enemy": "'Our last encounter was but a prelude,' Calista declares, her voice echoing off the stone. 'Let us see if you've grown in wisdom and strength.'"
                             }
                         ],
                         storyLineWonFight=[
                             {
                                 "text": "As the battle fades, Calista Starcross acknowledges Charlie's victory with a nod of respect. 'You have proven yourself, seeker. The Citadel's secrets await those who are truly ready to understand them.'"
                             },
                             {
                                 "text": "Amidst the silence of the Old Citadel, where whispers of the past linger like ghosts, Charlie stumbles upon an object unlike any other. Nestled in an alcove, hidden from the untrained eye, lies the Holographic Cosmos Codex. This ancient artifact, bound by time yet untouched by it, exudes a faint glow, inviting the curious and the brave. Its surface is adorned with intricate etchings that seem to dance in the dim light, telling tales of cosmic journeys and celestial secrets.",
                             },
                             {
                                 "text": "Charlie reaches out, his fingers brushing against the Codex, feeling the pulse of history within.",
                             },
                             {
                                 "item": Special(
                                     name="Holographic Cosmos Codex",
                                     description="An encyclopedic device that, upon activation, unfolds into a 3D map of the galaxy, each sector revealing a part of the cosmic chronicle that culminates in the revelation of Luminara's significance."
                                 )
                             },
                             {
                                 "text": "You have found an item: Holographic Cosmos Codex"
                             },
                             {
                                 "player": "What mysteries do you hold? he wonders aloud, his voice a mere whisper in the vast chamber.",
                             },

                         ],
                         storyLineLostFight=[
                             {
                                 "text": "Defeated, Charlie feels the weight of his shortcomings. 'You lack the readiness to uncover what lies within,' Calista's voice softens, not in mockery but as a mentor's counsel. 'Return when time has honed your resolve.'"
                             }
                         ],
                         storyLineDefeated=[
                             {
                                 "text": "In the quiet aftermath, the Citadel seems to stand a bit lighter, as if acknowledging Charlie's growth. Calista Starcross, now an ally, offers silent guidance through the echoing corridors."
                             }
                         ],
                         health=70,
                         attack=25,
                         defense=15,
                         fought=False
                     ),
                     items=[
                         Potion(
                             name="Small Potion",
                             health=25
                         )
                     ]
                     ),
            ]

            luminara_areas = [
                Area(name="Neon Nexus of Luminara",
                     storyLine=[
                         {
                             "clear": True
                         },
                         {
                             "text": ""
                         },
                     ],
                     storyLineVisited=[
                         {
                             "clear": True
                         },
                         {
                             "text": ""
                         }
                     ],
                     position=(0, 0)
                     ),
                Area(name="The Cloud City",
                     storyLine=[
                         {
                             "clear": True
                         },
                         {
                             "text": ""
                         },
                     ],
                     storyLineVisited=[
                         {
                             "clear": True
                         },
                         {
                             "text": ""
                         }
                     ],
                     ),
                Area(name="Galactic Grove",
                     storyLine=[
                         {
                             "clear": True
                         },
                         {
                             "text": ""
                         },
                     ],
                     storyLineVisited=[
                         {
                             "clear": True
                         },
                         {
                             "text": ""
                         }
                     ],
                     ),
                Area(name="The Labyrinth of Lost Souls",
                     storyLine=[
                         {
                             "clear": True
                         },
                         {
                             "text": ""
                         },
                     ],
                     storyLineVisited=[
                         {
                             "clear": True
                         },
                         {
                             "text": ""
                         }
                     ],
                     ),
                Area(name="Lightwave Lake",
                     storyLine=[
                         {
                             "clear": True
                         },
                         {
                             "text": ""
                         },
                     ],
                     storyLineVisited=[
                         {
                             "clear": True
                         },
                         {
                             "text": ""
                         }
                     ],
                     ),
                Area(name="Penumbral Plains",
                     storyLine=[
                         {
                             "clear": True
                         },
                         {
                             "text": ""
                         },
                     ],
                     storyLineVisited=[
                         {
                             "clear": True
                         },
                         {
                             "text": ""
                         }
                     ],
                     ),
                Area(name="The Crystal Labyrinth",
                     storyLine=[
                         {
                             "clear": True
                         },
                         {
                             "text": ""
                         },
                     ],
                     storyLineVisited=[
                         {
                             "clear": True
                         },
                         {
                             "text": ""
                         }
                     ],
                     ),
                Area(name="The Temple of the Ancients",
                     storyLine=[
                         {
                             "clear": True
                         },
                         {
                             "text": ""
                         },
                     ],
                     storyLineVisited=[
                         {
                             "clear": True
                         },
                         {
                             "text": ""
                         }
                     ],
                     ),
                Area(name="The Garden of Glass Stars",
                     storyLine=[
                         {
                             "clear": True
                         },
                         {
                             "text": ""
                         },
                     ],
                     storyLineVisited=[
                         {
                             "clear": True
                         },
                         {
                             "text": ""
                         }
                     ],
                     ),
            ]

            yolkaris_travel = {
                "to": [
                    "The Nebula Voyager II approached Yolkaris, its engines "
                    "humming softly. As it landed, the ship retracted into "
                    "its compact egg form, leaving Charlie gazing at the "
                    "familiar vistas of his home planet. 'Back to where it "
                    "all began,' he thought, pocketing the egg and stepping "
                    "onto the verdant fields of Yolkaris."
                ],
                "from": [
                    "Charlie held the egg-sized Nebula Voyager II, giving it "
                    "a precise twist and press. He placed it gently on the "
                    "ground, stepping back as it whirred and expanded into "
                    "the sleek spaceship within seconds. With a determined "
                    "glance at Yolkaris' fading skyline, he boarded, "
                    "ready for the stars to guide his next adventure."
                ]
            }

            mystara_travel = {
                "to": [
                    "Mystara's rugged terrain came into view as Charlie "
                    "descended. Once landed, the Nebula Voyager II collapsed "
                    "back into its egg form with a series of mechanical "
                    "whispers. Charlie picked up the compact egg, "
                    "the mysteries of Mystara awaiting his exploration under "
                    "its ancient skies."
                ],
                "from": [
                    "As the mystic hues of Mystara's atmosphere enveloped "
                    "him, Charlie prepared the Nebula Voyager II for "
                    "departure. With a twist and a press, the egg "
                    "transformed, its form unfolding into the starship that "
                    "gleamed under the alien sun. Charlie entered the "
                    "cockpit, his heart set on the cosmic paths that lay "
                    "ahead."
                ]
            }

            luminara_travel = {
                "to": [
                    "Luminara's brilliance welcomed Charlie as he landed. "
                    "The Nebula Voyager II transformed back into its egg "
                    "state, compact and enigmatic. Holding the egg, Charlie "
                    "stepped out into the gleaming world, its luminescent "
                    "beauty spreading out before him, a canvas of light and "
                    "shadow."
                ],
                "from": [
                    "In the radiant glow of Luminara, Charlie activated the "
                    "Nebula Voyager II. The small egg expanded into his "
                    "interstellar vessel in mere moments, its panels locking "
                    "into place with a satisfying click. He looked back at "
                    "the shimmering landscapes one last time before "
                    "embarking on his journey through the velvet cosmos."
                ]
            }

        self.location_objects = {
            "Yolkaris": Yolkaris(yolkaris_size, yolkaris_areas, yolkaris_travel),
            "Mystara": Mystara(mystara_size, mystara_areas, mystara_travel),
            "Luminara": Luminara(luminara_size, luminara_areas, luminara_travel)
        }

    def create_player(self) -> None:
        """
        This creates the player.
        """
        while True:
            username = ask_user(
                type=None, prompt="Please enter your username: ")
            if 3 <= len(username) <= 24 and username.isalnum() and "_" \
                    not in username:
                self.player = Player(
                    name=username,
                    health=100,
                    attack=15,
                    defense=10,
                    potions=[],
                    inventory=[
                        Special(
                            name="Holographic Cosmos Codex",
                            description="An encyclopedic device that, upon activation, unfolds into a 3D map of the galaxy, each sector revealing a part of the cosmic chronicle that culminates in the revelation of Luminara's significance.",
                            storyLine=[
                                {
                                    "text": "Charlie carefully takes the Holographic Cosmos Codex from his inventory. With a sense of reverence and anticipation, he activates the device. Immediately, the room is transformed into a miniature universe, with stars, planets, and nebulae swirling around in a breathtaking display of light and color."
                                },
                                {
                                    "player": "This is magnificent."
                                },
                                {
                                    "text": "The Codex, responsive to his touch, zooms in on a particular sector marked by a radiant glow. It's Luminara, highlighted among countless star systems, its significance underscored by ancient symbols that orbit it like satellites."
                                },
                                {
                                    "text": "As he interacts with the holographic map, Charlie realizes the Codex is more than a mere tool; it's a key to unlocking the next phase of his journey."
                                },
                                {
                                    "player": "The Orb is on Luminara. This Codex has shown me the way. Luminara holds the answers I've been seeking."
                                },
                                {
                                    "text": "He watches as the Codex folds back into its original form, the galaxy it displayed now etched in his mind's eye."
                                },
                                {
                                    "player": "To Luminara, then. It's time to uncover the secrets it holds and bring back the light to Yolkaris."
                                }
                            ]
                        ),
                        Spaceship(
                            name="Spaceship",
                            description="Testing Spaceship"
                        )
                    ]
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

        # Display player's basic stats
        add_space()
        text(f"Player {player.name}:")
        text(
            f"Health: {player.health}, Attack: {player.attack}, Defense: {player.defense}")
        text(f"Armour: {player.armour.name if player.armour else 'None'}")
        text(f"Weapon: {player.weapon.name if player.weapon else 'None'}")

        # potions count
        potions_count = len(player.potions)
        text(f"Potions: {potions_count}")

        items_count = len(player.inventory)
        text(f"Inventory: {items_count}")
        self.location_and_position()

    def choose_action(self) -> None:
        """
        This method displays the available actions and prompts the player to
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
        elif action == "contents":
            self.show_location_contents()
        elif action in ["search", "s"]:
            self.search_current_area()
        elif action in ["inventory", "i"]:
            self.show_inventory()
        elif action in ["potion", "potions", "p"]:
            self.select_potion()
        elif action == "reset":
            self.reset_game()
        elif action == "quit":
            self.game_over = True

    def reset_game(self) -> None:
        """
        This method resets the game.
        """
        self.setup_game()
        self.start_game()

    def search_current_area(self):
        """
        This method searches the current area for items.
        """
        current_location = self.get_current_location()
        current_location.search_area(self.player)

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

        add_space()
        text("Your inventory contains:", space=1)
        for index, item in enumerate(self.player.inventory, start=1):
            name = item.name
            text(f"{index}. {name}")
        add_space()
        prompt = "Select an item number to interact with, or type '0' to cancel: "
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
        item = self.player.inventory[index]
        name = item.name
        add_space()
        text(f"You selected {name}.", space=1)

        action = ask_user("item")
        if action.lower() in ['use', 'u']:
            self.use_inventory_item(item)
        elif action.lower() in ['inspect', 'i']:
            self.inspect_inventory_item(item)
        else:
            text("Invalid action.")

    def use_inventory_item(self, item):
        name = item.name

        if isinstance(item, Book):
            text(f"You have read the {name}.")
            Interaction.print_story_line(self, item.storyLine)
        elif isinstance(item, Spaceship):
            self.travel_to_new_location()
        elif isinstance(item, Special):
            Interaction.print_story_line(self, item.storyLine)

    def travel_to_new_location(self):
        # Initial locations
        base_destinations = {'Yolkaris': ['Mystara'], 'Mystara': [
            'Yolkaris'], 'Luminara': ['Yolkaris', 'Mystara']}
        special_item_name = "Holographic Cosmos Codex"

        current_location = self.get_current_location()
        add_space()
        text("Select a location to travel to:", space=1)

        # Check if the player has the special item and adjust available locations accordingly
        has_special_item = any(
            item.name == special_item_name for item in self.player.inventory
        ) if self.player.inventory else False

        if has_special_item and current_location.name == 'Mystara':
            available_destinations = base_destinations[current_location.name] + [
                'Luminara']
        else:
            available_destinations = base_destinations[current_location.name]

        # List available locations to travel to
        for index, location in enumerate(available_destinations, start=1):
            text(f"{index}. {location}")

        add_space()

        # Get the user's choice
        choice = ask_user(
            "number", prompt="Where do you want to go? ", numbers=[str(i) for i in range(1, len(available_destinations) + 1)])
        selected_location_name = available_destinations[int(choice) - 1]

        # Find the index of the selected location in the original locations list
        self.current_location = ['Yolkaris', 'Mystara',
                                 'Luminara'].index(selected_location_name)

        new_location = self.get_current_location()
        new_location.player_position = (0, 0)
        new_location.player_prev_position = (0, 0)
        new_location.mark_visited((0, 0))

        add_space()
        current_location.print_travel_story_line('from')
        loading([f'{current_location.name} ', '* ', '* ', '* ', '* ',
                '* ', '* ', '* ', '* ', '* ', '* ', f'{new_location.name}'])
        add_space()
        add_space()
        new_location.print_travel_story_line('to')

    def select_potion(self):
        if not self.player.potions:
            text("Your inventory is empty.")
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
        player = self.player
        max_health = 100
        if player.health == max_health:
            text("You are already at full health.")
        else:
            player.health += potion.health
            if player.health > max_health:
                player.health = max_health
            player.potions.remove(potion)
            text(
                f"You used a {potion.name}. Your health is now {player.health}.")

    def inspect_inventory_item(self, item):
        name = item.name
        description = item.description
        add_space()
        paragraph(f"{name}: {description}")


if __name__ == "__main__":
    game = Game()
    game.setup_game()
    game.start_game()
