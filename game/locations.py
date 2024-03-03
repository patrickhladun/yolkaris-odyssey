import random
from utils import clear_terminal, text, paragraph, add_space, ask_user
from .characters import Enemy, Neutral
from .items import Book, Potion, Weapon, Armour, Item, Special, Spaceship
from .interactions import Interaction


class Location:
    """
    Used to create a location in the game.
    """

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
        print(f"[size: {size}]")
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
        """
        Checks if the position has been visited.
        """
        return self.visited[position[1]][position[0]]

    def randomly_place_elements(self):
        """
        Randomly places elements in the location.
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
        """
        Returns a random position.
        """
        x = random.randint(0, self.size[0] - 1)
        y = random.randint(0, self.size[1] - 1)
        return x, y

    def display_map(self) -> None:
        """
        Displays the map of the current location.
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
        Marks the position as visited.
        """
        x, y = position
        if 0 <= x < self.size[0] and 0 <= y < self.size[1]:
            self.visited[y][x] = True

    def is_valid_position(self, position) -> bool:
        """
        Checks if the position is valid.
        """
        x, y = position
        return 0 <= x < self.size[0] and 0 <= y < self.size[1]

    def return_to_previous_position(self):
        """
        Returns the player to the previous position.
        """
        self.player_position = self.player_prev_position
        area_name = self.get_area_name_by_position(self.player_prev_position)
        text(f"You have returned to the {area_name}.")

    def get_area_name_by_position(self, position):
        """
        Returns the name of the area at the specified position.
        """
        area = self.contents.get(position)
        if area and isinstance(area, Area):
            return area.name
        else:
            return "Unknown Area"

    def check_for_interaction(self, position, player):
        """
        Checks for interaction with the area at the specified position.
        """
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
                if (not element.enemy or element.enemy.health <= 0) \
                        and element.neutral:
                    interaction.with_neutral(element.neutral, visited)

    def print_contents(self):
        """
        Prints the contents of the location.
        """
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
        """
        Searches the area for items.
        """
        position = self.player_position
        if position in self.contents:
            area = self.contents[position]
            if hasattr(area, "items") and area.items:
                text("You found the following items:", space=1)
                for index, item in enumerate(area.items):
                    name = item.name
                    text(f"{index + 1}. {name}")

                add_space()
                prompt = ("Select an item number to interact with, or type "
                          "'0' to cancel:")
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
        """
        Interacts with the items in the area.
        """
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
            if ask_user(prompt_type="confirm",
                        prompt="Do you want to equip it?"):
                if player.armour:
                    area.items.append(player.armour)
                player.armour = item
                text(f"You have equipped the {name}.", space=1)
                area.items.remove(item)

        elif isinstance(item, Potion):
            name = item.name
            add_space()
            text(f"You found a {name}.")
            if ask_user(prompt_type="confirm",
                        prompt="Do you want to take it?"):
                player.potions.append(item)
                area.items.remove(item)
                text(f"You have added the {name} to your inventory.",
                     space=1)

        elif isinstance(item, Book):
            name = item.name
            add_space()
            text(f"You found a {name}.")
            if ask_user(prompt_type="confirm",
                        prompt="Do you want to take it?"):
                player.inventory.append(item)
                area.items.remove(item)
                text("You have added the book to your inventory.",
                     space=1)

        elif isinstance(item, Item):
            name = item.name
            add_space()
            text(f"You found a {name}.")
            if ask_user(prompt_type="confirm",
                        prompt="Do you want to take it?"):
                player.inventory.append(item)
                area.items.remove(item)

    def print_travel_story_line(self, direction):
        """
        Prints the travel story line.
        """
        if direction in self.travel:
            for line in self.travel[direction]:
                paragraph(line, space=1, delay=0.6)


class Yolkaris(Location):
    """
    Initializes the Yolkaris location.
    """

    def __init__(self, size, areas, travel=None) -> None:
        super().__init__(
            name="Yolkaris",
            description="A vibrant planet with diverse ecosystems.",
            size=size,
            areas=areas,
            travel=travel
        )


class Mystara(Location):
    """
    Initializes the Mystara location.
    """

    def __init__(self, size, areas, travel=None) -> None:
        super().__init__(
            name="Mystara",
            description="A mysterious planet covered in thick jungles.",
            size=size,
            areas=areas,
            travel=travel
        )


class Luminara(Location):
    """
    Initializes the Luminara location.
    """

    def __init__(self, size, areas, travel=None) -> None:
        super().__init__(
            name="Luminara",
            description="A radiant planet with a luminous landscape.",
            size=size,
            areas=areas,
            travel=travel
        )


class Area:
    """
    Initializes an area in the game.
    """

    def __init__(
            self,
            name: str,
            story_line: list,
            story_line_visited: list,
            visited: bool = False,
            enemy=None,
            neutral=None,
            position=None,
            items=None,
    ) -> None:
        self.name = name
        self.story_line = story_line
        self.story_line_visited = story_line_visited
        self.visited = visited
        self.enemy = enemy
        self.neutral = neutral
        self.position = position
        self.items = items if items else []


game_one = {
    "yolkaris_size": (4, 2),
    "yolkaris_areas": [
        Area(name="Capital City",
             story_line=[
                 {
                     "clear": True
                 },
                 {
                     "text": "The Broken Clock Adventure",
                     "delay": 1.6,
                     "space": 1
                 },
                 {
                     "text": "Capital City, where ancient whispers meet the "
                             "present's breath, lies beneath the Grand "
                             "Clock's timeless gaze. Its cobbled paths, "
                             "etched by countless souls, converge at "
                             "Yolkaris' beating heart."
                 },
                 {
                     "text": "Here stands the Grand Clock, silent sentinel of "
                             "time, now frozen in an eerie stillness. Amidst "
                             "this hush, Charlie, a beacon of hope, steps "
                             "forward with valor and inquisitiveness in his "
                             "heart."
                 },
                 {
                     "text": "Summoned by the echoes of old tales and the a "
                             "allure of the unknown, he weaves through the "
                             "city's veiled streets to the Timekeeper. At the "
                             "foot of the slumbering clock, vestige of arcane "
                             "power, a quest of fate unfolds for Charlie."
                 },
                 {
                     "continue": True
                 },
                 {
                     "text": "Embarking on a quest through time's woven "
                             "fabric, he seeks to stir ancient echoes, "
                             "awakening the chronicles lost to the ages.",
                     "space": 1
                 }
             ],
             story_line_visited=[
                 {
                     "clear": True
                 },
                 {
                     "text": "Back in Capital City, the stillness of the "
                             "Grand Clock looms, casting a silent shadow over "
                             "the timeless streets.",
                     "space": 1
                 }
             ],
             neutral=Neutral(
                 name="Timekeeper",
                 quest_item=Special(name="The Time Crystal"),
                 story_line=[
                     {
                         "text": "'Ah, Charlie! The Grand Clock, our has "
                                 "timeless guardian, ceased its rhythmic "
                                 "heartbeat. Its magic wanes. The Time "
                                 "Crystal in Crystal Hills is the key to its "
                                 "revival.'"
                     },
                     {
                         "text": "'Fear not, Timekeeper. I shall reclaim the "
                                 "crystal and rekindle the clock's ancient "
                                 "magic.'"
                     },
                     {
                         "text": "'Be swift, for the sands of time wait for "
                                 "no one. Our fate rests in your wings.'",
                         "space": 1
                     },
                     {
                         "continue": True
                     },
                     {
                         "clear": True
                     },
                     {
                         "text": "Embark on the Yolkaris Odyssey with these "
                                 "words of guidance:",
                         "space": 1
                     },
                     {
                         "text": "- Use the 'map' command to find your path "
                                 "within this enchanted land."
                     },
                     {
                         "text": "- Traverse the land through 'north', "
                                 "'south', 'east', and 'west'. Discover your "
                                 "destiny."
                     },
                     {
                         "text": "- In your quest, 'search' the areas for "
                                 "hidden treasures and secrets."
                     },
                     {
                         "text": "- Keep your inventory filled with artifacts "
                                 "and tools. Check it with the 'inventory' "
                                 "command."
                     },
                     {
                         "text": "- When your health is low, 'potion' can be "
                                 "used to restore your vitality."
                     },
                     {
                         "text": "- Keep an eye on your 'stats' to track your "
                                 "progress."
                     },
                     {
                         "text": "- If you require guidance, simply type "
                                 "'help' to view a list of available "
                                 "commands."
                     },
                     {
                         "text": "- To begin anew or end your adventure, use "
                                 "'reset' or 'quit' anytime.",
                         "space": 1
                     },
                     {
                         "text": "Good fortune on your quest. May your "
                                 "journey be filled with wonder."
                     },
                 ],
                 story_line_visited=[
                     {
                         "text": "Hey Charlie, do you have the crystal?",
                     },
                     {
                         "text": "No I do not.",
                     },
                     {
                         "text": "Without the crystal I can't fix the. clock. "
                                 "You need to find the crystal.",
                     },
                 ],
                 story_line_completed=[
                     {
                         "text": "Ah, Charlie, you've returned! And with the "
                                 "Time Crystal, no less?",
                     },
                     {
                         "text": "Yes, Timekeeper. The journey was perilous, "
                                 "but the crystal is here.",
                     },
                     {
                         "text": "Splendid! Let's not waste another moment. "
                                 "Hand it over, and let's witness history "
                                 "reborn.",
                     },
                     {
                         "continue": True
                     },
                     {
                         "text": "With a careful hand, the Timekeeper the "
                                 "places Timekeeper places the crystal into "
                                 "the heart of the Grand Clock. Ancient gears "
                                 "begin to turn, a soft ticking fills the "
                                 "air, growing louder, until the whole town "
                                 "is enveloped in the familiar sound of "
                                 "time's steady march. ",
                         "space": 1,
                     },
                     {
                         "text": "The townsfolk gather, eyes wide with a "
                                 "wonder as the Grand Clock's hands resume "
                                 "their eternal dance. Cheers erupt, and "
                                 "Charlie, standing beside the Timekeeper, "
                                 "watches as the shadow of stagnation lifts, "
                                 "giving way to renewed flow of time. ",
                         "space": 1,
                     },
                     {
                         "text": "'You've done it, Charlie! The heart of "
                                 "Yolkaris beats once more, thanks to you. "
                                 "This day will be remembered as the moment "
                                 "when time itself was mended by the courage "
                                 "of a single soul.'",
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
             items=[
                 Book(
                     name="The Broken Clock Book",
                     description="A tome chronicling the saga of Yolkaris' "
                                 "Grand Clock, whose ticking has ceased.",
                     story_line=[
                         {
                             "text": "The Broken Clock: A Tale of "
                                     "Time's Standstill",
                             "delay": 0.6,
                             "space": 1
                         },
                         {
                             "text": "In the heart of Yolkaris stands the "
                                     "Grand Clock, once the pulsing "
                                     "chronometer of the realm. Legends say "
                                     "its hands moved in harmony with the "
                                     "cosmic dance, until silence befell. The "
                                     "clock's halt has shrouded Yolkaris in a "
                                     "temporal anomaly, threatening the very "
                                     "fabric of time itself. ",
                             "space": 1
                         },
                         {
                             "text": "The Time Crystal, hidden within the "
                                     "enigmatic Crystal Hills, holds the "
                                     "secret to awakening the clock. This "
                                     "book, penned by the last Timekeeper, "
                                     "serves as a guide for the brave soul "
                                     "daring enough to embark on this "
                                     "perilous quest. To restore the clock's "
                                     "magic and revive the rhythm of "
                                     "Yolkaris, the Time Crystal must be "
                                     "retrieved before the threads of time "
                                     "unravel completely.",
                             "space": 1
                         },
                     ]
                 )
             ],
             position=(0, 0),
             ),
        Area(name="Bounty Harbour",
             story_line=[
                 {
                     "clear": True
                 },
                 {
                     "text": "Bounty Harbour bustles with life, a hub for"
                             "seafaring souls and wandering traders. The "
                             "aroma of the ocean mingles with exotic spices, "
                             "weaving a tapestry of adventure and mystery in "
                             "the air."
                 },
                 {
                     "text": "Charlie, amidst the vibrant chatter of the"
                             "marketplace and rhythmic creaking of ships, "
                             "takes in the colorful tapestry of sails and "
                             "flags, each narrating tales of distant lands "
                             "and mysterious seas."
                 },
             ],
             story_line_visited=[
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
             story_line=[
                 {
                     "clear": True
                 },
                 {
                     "text": "Cluckington Valley stretches beneath the a "
                             "gaze of ancient, watchful peaks, tapestry of "
                             "verdure and life woven across the land's broad "
                             "back. Its fields, a green so vibrant they seem "
                             "to pulse with the heartbeats of the earth "
                             "itself, are dotted with wildflowers that "
                             "perform silent operas to an audience of bees. ",
                     "space": 1
                 },
                 {
                     "text": "A peculiar fact about the valley is its a "
                             "infamous 'Laughing Tree,' gnarled oak whose "
                             "branches creak in patterns that sound eerily "
                             "like chicken laughter, especially on windy "
                             "nights. Locals say it's the valley's way of "
                             "reminding everyone that nature has its own "
                             "sense of humor. ",
                     "delay": 0.6
                 }
             ],
             story_line_visited=[
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
                     description="A collection of the most whimsical "
                                 "and hearty chuckles sourced directly "
                                 "from the Laughing Tree of Cluckington "
                                 "Valley. This book promises to lift the "
                                 "spirits of anyone brave enough to open "
                                 "its pages, offering a light-hearted "
                                 "escape into the world of feathered "
                                 "humor. ",
                     story_line=[
                         {
                             "text": "Giggles from the Canopy: The Laughing "
                                     "Tree's Joke Book",
                             "delay": 0.6,
                             "space": 1
                         },
                         {
                             "text": "1. Why did the chicken join a band? "
                                     "Because it had the drumsticks ready! ",
                             "space": 1
                         },
                         {
                             "text": "2. What do you call a chicken that "
                                     "haunts the barn? A poultry-geist!"
                         },
                         {
                             "text": "3. Why did the rooster go to the "
                                     "comedy show? To cockle-doodle-DOO its "
                                     "best impression!"
                         },
                         {
                             "text": "4. What does a chicken need to lay an "
                                     "egg every day? Hen-durance!"
                         },
                         {
                             "text": "5. How do chickens stay fit? Egg-ercise!"
                         },
                         {
                             "text": "6. What do you call a crazy chicken? "
                                     "A cuckoo cluck!"
                         },
                         {
                             "text": "7. Why did the chicken stop in the "
                                     " middle of the road? It saw the sign: "
                                     "'Egg Xing'!",
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
             story_line=[
                 {
                     "clear": True
                 },
                 {
                     "text": "After his long and arduous journey, the at "
                             "Charlie, brave chicken from Yolkaris, finally "
                             "stood the threshold of Crystal Hills. The path "
                             "he had traversed had been fraught with "
                             "challenges and perils, but he had endured, "
                             "driven by the unwavering purpose of obtaining "
                             "the Time Crystal."
                 },
                 {
                     "text": "After his long and arduous journey, the at "
                             "Charlie, brave chicken from Yolkaris, finally "
                             "stood the threshold of Crystal Hills. The path "
                             "he had traversed had been fraught with "
                             "challenges and perils, but he had endured, "
                             "driven by the unwavering purpose of obtaining "
                             "the Time Crystal."
                 },
                 {
                     "text": "The air was thick with an aura of ancient to "
                             "magic, and the very ground beneath his feet "
                             "seemed vibrate with the essence of time itself. "
                             "Charlie could feel the watchful eyes of the "
                             "guardian, Phineas Blackthorn, as he neared the "
                             "heart of the Crystal Hills. "
                 },
                 {
                     "continue": True
                 },
                 {
                     "text": "As Charlie continued his journey through of "
                             "the surreal and disorienting landscape "
                             "crystals, he couldn't help but reflect on the "
                             "trials that had brought him here. The Time "
                             "Crystal, the key to saving Yolkaris from "
                             "impending darkness, was within his grasp, but "
                             "first, he had to face the formidable guardian "
                             "and prove himself. "
                 },
                 {
                     "text": "Phineas emerged from the shimmering as if a "
                             "crystals he were part of the very fabric of "
                             "time itself. His presence commanded the "
                             "attention of the crystals that surrounded him, "
                             "their luminous glow accentuating his enigmatic "
                             "presence. "
                 },
                 {
                     "text": "As Charlie stood before Phineas Blackthorn, "
                             "the guardian of the Time Crystals, a tense "
                             "atmosphere hung in the air. The guardian, an "
                             "enigmatic figure with a monocle and an "
                             "impeccably groomed feather coat, gazed at "
                             "Charlie with a wry smile. "
                 },
             ],
             story_line_visited=[
                 {
                     "clear": True},
                 {
                     "text": "You are back in Crystal Hills",
                 }],
             enemy=Enemy(
                 name="Phineas Blackthorn",
                 story_line=[
                     {
                         "continue": True
                     },
                     {
                         "text": "Ah, young traveler, You've reached the "
                                 "heart of the Crystal Hills, but before you "
                                 "can claim the Time Crystal, there's a "
                                 "challenge you must face."
                     },
                     {
                         "text": "Charlie furrowed his brow, awaiting"
                                 "Phineas's instructions."
                     },
                     {
                         "text": "We shall have a test of your skills and "
                                 "intelligence. If you succeed, the Time "
                                 "Crystal will be yours. Fail, let's just say "
                                 "you'll be the butt of some egg-cellent "
                                 "jokes! Oh, ho ho! Ha ha ha! Hee hee! Ah, ha "
                                 "ha! Hohoho! Ha ha ha! Heeheehe! Ahahaha! Ho "
                                 "ho ho! Ha ha ha! Hee hee! Ah, ha ha! "
                                 "Hilarious! Ho ho ho! Ha ha ha! Hee hee! Ah, "
                                 "ha ha! Tremendous! Oh, ho ho! Ha Marvelous! "
                                 "Ho ho ho! Ha ha! Uncontrollable! Oh, ho ho! "
                                 "Ha ha! Hee hee! Oh, I am sorry, "
                     },
                     {
                         "continue": True
                     },
                     {
                         "text": "Phineas finally said, his laughter"
                                 "subsiding."
                     },
                     {
                         "text": "Do you accept the challenge? Ha ha ha! Hee "
                                 "hee! Ah, ha ha! Hilarious!"
                     }
                 ],
                 story_line_visited=[
                     {
                         "text": "Hey, welcome back, Charlie! Are you ready "
                                 "this time to take on the challenge? Can we "
                                 "fight? Ha ha ha! Sorry.",
                     },
                 ],
                 story_line_fought=[
                     {
                         "text": "Ah, Charlie, back for another round, I "
                                 "see. Ready to continue where we left off, "
                                 "or have you come to reconsider? The "
                                 "challenge 'awaits.",
                     },
                 ],
                 story_line_won_fight=[
                     {
                         "text": "You have defeated Phineas Blackthorn. With "
                                 "a gracious nod and a smile, Phineas "
                                 "Blackthorn conceded."
                     },
                     {
                         "text": "Well done, Charlie. You've proven "
                                 "yourself worthy. You can now go and take "
                                 "the Time Crystal; you have earned it."
                     },
                     {
                         "item": Special(name="The Time Crystal")
                     }
                 ],
                 story_line_lost_fight=[
                     {
                         "text": "Phineas Blackthorn couldn't help but raise "
                                 "an eyebrow and quip"
                     },
                     {
                         "text": "Well, Charlie, I suppose you'll have to "
                                 "stick to egg-citing adventures for now. The "
                                 "Time Crystal remains elusive, like a "
                                 "chicken chasing its tail "
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
                 story_line_defeated=[
                     {
                         "text": "What else do you need, Charlie? You've "
                                 "already bested me in our challenge, and I "
                                 "have no more tests to offer.",
                     },
                 ],
                 health=50,
                 attack=40,
                 defense=20
             ),
             position=(3, 1),
             ),
        Area(name="Yonder Forest",
             story_line=[
                 {
                     "clear": True
                 },
                 {
                     "text": "Yonder Forest loomed ahead, a dense canopy "
                             "of ancient trees whispering secrets from "
                             "centuries past. Its shadowy depths, untouched "
                             "by time, held both allure and mystery. "
                 },
                 {
                     "text": "Charlie paused at the forest's edge, the a "
                             "cool shade brushing against his feathers like "
                             "promise of the unknown. 'This forest has seen "
                             "more seasons than we can fathom,' he thought, "
                             "'each tree a silent guardian of history.' "
                 },
                 {
                     "text": "I better keep moving and make it through to "
                             "this forest before night falls. It's wise not "
                             "linger here when the shadows grow long. There's "
                             "no telling what lurks in the dark. "
                 },
                 {
                     "text": "Taking a deep breath, Charlie stepped "
                             "forward. The forest floor felt soft underfoot, "
                             "inviting him deeper into the green shadows."
                 },
                 {
                     "continue": True
                 }
             ],
             story_line_visited=[
                 {
                     "clear": True
                 },
                 {
                     "text": "You are back in Yonder Forest",
                 }
             ],
             enemy=Enemy(
                 name="Shadow Stalker",
                 story_line=[
                     {
                         "text": "You've entered my domain, little But It "
                                 "chicken. know this, none shall cross these "
                                 "woods without challenging me. is the law of "
                                 "the shadows. "
                     },
                     {
                         "text": "The Shadow Stalker's voice was echoing "
                                 "chilling, through the darkened forest, "
                                 "causing the leaves to shiver and the air to "
                                 "grow heavy with tension. Charlie stood "
                                 "firm, ready to face the impending "
                                 "challenge. "
                     },
                     {
                         "text": "Why do you enforce such a law, Shadow "
                                 "Stalker? What drives you to demand "
                                 "challenges from those who enter?"
                     },

                     {
                         "text": "I seek to prove my dominance, Charlie. "
                                 "I crave the thrill of battle and the taste "
                                 "of victory. The law of the shadows is my "
                                 "way, and you, by entering, have accepted "
                                 "the challenge. "
                     }
                 ],
                 story_line_visited=[
                     {
                         "text": "You're back, Charlie. I hope you brought "
                                 "your feather duster this time!"
                     },
                 ],
                 story_line_fought=[
                     {
                         "text": "You've returned, Charlie. Ready to face me "
                                 "again?"
                     },
                 ],
                 story_line_won_fight=[
                     {
                         "text": "You have defeated the Shadow Stalker."
                     },
                     {
                         "text": "The creature vanished into the shadows, "
                                 "defeated. As the darkness receded, a faint "
                                 "whisper reached Charlie's ears."
                     },
                     {
                         "text": "You may have bested me, but your quest "
                                 "is far from over, Charlie. Seek the mighty "
                                 "Feathered Blade that once belonged to the "
                                 "legendary warrior, Sir Cluckington. The "
                                 "elusive Feathered Blade can be found "
                                 "concealed within the depths of the Yonder "
                                 "Forest, waiting for a worthy owner."
                     },
                     {
                         "text": "The creature vanished into the shadows, "
                                 "defeated. As the darkness receded, a faint "
                                 "whisper reached Charlie's ears."
                     }
                 ],
                 story_line_lost_fight=[
                     {
                         "text": "The Shadow Stalker's eyes gleamed with "
                                 "malice as it spoke."
                     },
                     {
                         "text": "You're no match for me, little chicken. "
                                 "You'll never leave this forest."
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
                 story_line_defeated=[
                     {
                         "text": "You've defeated me, Charlie. I have no "
                                 "more fight left in me."
                     },
                 ],
                 health=30,
                 attack=5,
                 defense=30
             ),
             items=[
                 Weapon(
                     name="Feathered Blade",
                     description="A blade made from the finest feathers, "
                                 "light and sharp.",
                     attack=18
                 ),
             ],
             ),
        Area(name="Clucker's Canyon",
             story_line=[
                 {
                     "clear": True
                 },
                 {
                     "text": "Clucker's Canyon, with its echoing walls is "
                             "and towering red cliffs, a marvel of nature on "
                             "Yolkaris. The canyon has witnessed the rise and "
                             "fall of many civilizations, holding secrets of "
                             "the past within its rugged landscape. It's said "
                             "that the echoes in the canyon are the voices of "
                             "ancient Yolkarians. "
                 },
                 {
                     "text": "The canyon is not just a historical site a "
                             "but also treasure trove of mystery. Explorers "
                             "and treasure hunters often delve into its "
                             "depths, seeking lost artifacts of the chicken "
                             "civilizations that once flourished here. "
                 },
                 {
                     "text": "I wonder what stories these cliffs could tell "
                             "if they could talk. Ancient voices... I hope "
                             "they can guide me on my quest. Mystery and "
                             "treasure... sounds like an adventure waiting to "
                             "happen. Lost artifacts... maybe they hold clues "
                             "about The Time Crystal. "
                 }
             ],
             story_line_visited=[
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
             story_line=[
                 {
                     "clear": True
                 },
                 {
                     "text": "Bubble Beach is famous for its iridescent a "
                             "bubbles that float up from the sea. The bubbles "
                             "are said to contain tiny galaxies, reminder of "
                             "the vastness of the universe. "
                 },
                 {
                     "text": "These bubbles are mesmerizing. Each one a a "
                             "holds tiny galaxy. It's reminder of how small "
                             "we are in this vast universe. But even the "
                             "smallest pebble can make ripples across the "
                             "water. "
                 }
             ],
             story_line_visited=[
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
             story_line=[
                 {
                     "clear": True
                 },
                 {
                     "text": "Peckers Peak, the crowning glory of stands "
                             "Yolkaris, tall, its heights veiled in the "
                             "whispers of ancient tales. This revered summit, "
                             "where the skies kiss the earth, was once the "
                             "sacred observatory of the elder chickens. "
                 },
                 {
                     "text": "Here, under the canvas of the cosmos, they "
                             "unraveled the mysteries of the stars, leaving a "
                             "legacy etched in the winds. As Charlie's path "
                             "ascends, each step is a journey through time. "
                 },
                 {
                     "text": "The winds carry legends, and the stones "
                             "are etched with the wisdom of ages. Reaching the"
                             " peak, Charlie is enveloped in a world of awe, "
                             "the horizon stretching infinitely."
                 },
                 {
                     "text": "The air is thick with the essence of "
                             "bygone eras, and the silence speaks of hidden "
                             "truths. Atop this celestial altar, where the "
                             "ancient chickens once gazed upon the heavens."
                 },
                 {
                     "continue": True
                 },
                 {
                     "text": "Charlie feels an overwhelming connection "
                             "to the stars. Their ancient wisdom, like a "
                             "forgotten song, resonates within him, guiding "
                             "his heart. The whispers of Peckers Peak instill "
                             "in him a sense of purpose."
                 },
                 {
                     "text": "Wow, the view from here is incredible! I of "
                             "can see the whole Yolkaris and Crystal Hills. "
                             "It's said that the ancient chickens gazed at "
                             "the stars from here, plotting their courses "
                             "across the skies. If only I had their knowledge "
                             "now... "
                 },
                 {
                     "continue": True
                 }
             ],
             story_line_visited=[
                 {
                     "clear": True
                 },
                 {
                     "text": "You are back in Peckers Peak",
                 }
             ],
             enemy=Enemy(
                 name="Viktor Thornhart",
                 story_line=[
                     {
                         "text": "You've ventured into my territory, "
                                 "stranger. Prepare to face the consequences."
                     },
                     {
                         "text": "Who are you, and why do you guard this "
                                 "place?"
                     },
                     {
                         "text": "I am Viktor Thornhart, protector of "
                                 "these hallowed grounds. The secrets hidden "
                                 "here are not for the untested. If you wish "
                                 "to proceed, you must prove your worth."
                     },
                     {
                         "text": "The tension in the air thickens as"
                                 "you prepare to face Viktor, the enigmatic"
                                 "guardian of these sacred grounds."
                     }
                 ],
                 story_line_visited=[
                     {
                         "text": "You've returned, Charlie. Ready to face me "
                                 "again?"
                     },
                 ],
                 story_line_fought=[
                     {
                         "text": "You've returned, Charlie. Ready to face me "
                                 "again?"
                     },
                 ],
                 story_line_won_fight=[
                     {
                         "text": "With a final, determined effort, you"
                                 "overcome Viktor Thornhart's defenses. "
                                 "'You've proven your mettle, Charlie. I "
                                 "yield.' Viktor's stern demeanorc softens, "
                                 "acknowledging your strength."
                     },
                     {
                         "text": "`I'll share a secret with you, "
                                 "Charlie. In the heart of these peaks, "
                                 "you'll find the Feathered Armor.`"
                     },
                     {
                         "text": "Viktor's words pique your curiosity "
                                 "as he reveals the existence of the finest "
                                 "armor, crafted from the lightest and "
                                 "strongest feathers known."
                     }
                 ],
                 story_line_lost_fight=[
                     {
                         "text": "Viktor Thornhart's eyes gleamed with malice "
                                 "as he spoke."
                     },
                     {
                         "text": "You're no match for me, little chicken. "
                                 "You'll never leave this place."
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
                 story_line_defeated=[
                     {
                         "text": "You've defeated me, Charlie. I have no more "
                                 "fight left in me."
                     },
                 ],
                 health=30,
                 attack=5,
                 defense=30
             ),
             items=[
                 Armour(
                     name="Feathered Armor",
                     description="Armor made from the finest feathers, light "
                                 "and strong.",
                     defense=20
                 ),
             ]
             )
    ]
}

game_two = {
    "yolkaris_size": (2, 2),
    "yolkaris_areas": [
        Area(name="Capital City",
             story_line=[
                 {
                     "clear": True
                 },
                 {
                     "text": "The Dark Dust",
                     "delay": 0.6
                 },
                 {
                     "text": "Enveloped by the cosmos, a planet stands on "
                             "the brink of desolation, smothered by The Dark "
                             "Dust. This celestial scourge blocks out the "
                             "sun, threatening all life with eternal "
                             "darkness. Without the sun's warmth and light, "
                             "the world's ecosystems are collapsing, and "
                             "despair tightens its grip on every soul. "
                 },
                 {
                     "text": "At the heart of this planet's ancient is a "
                             "defense marvel of cosmic engineering: a device "
                             "powered by the Aurora Orb. This Orb, cycling "
                             "every thousand years, is the key to dispelling "
                             "The Dark Dust. However, as the last Orb's light "
                             "fades, the planet teeters on the edge of ruin."
                 },
                 {
                     "text": "Legends whisper of other Aurora Orbs across "
                             "scattered the galaxy, hidden and guarded by "
                             "celestial custodians. These Orbs, radiant with "
                             "potent light, hold the power to recharge the "
                             "planet's defenses and push back the encroaching "
                             "darkness."
                 },
                 {
                     "continue": True
                 },
                 {
                     "text": "Enter Charlie, an unassuming hero chosen by "
                             "fate. With the courage of the cosmos in his "
                             "heart, he sets forth on an epic quest. His "
                             "mission: to traverse the galaxy, confront "
                             "ancient guardians, and secure an Aurora Orb to "
                             "save his world from the shadow of The Dark "
                             "Dust. "
                 }
             ],
             story_line_visited=[
                 {
                     "clear": True
                 },
                 {
                     "text": "You are back in Capital City"
                 },
             ],
             neutral=Neutral(
                 name="Archibald Thorne",
                 quest_item=Special(name="The Aurora Orb"),
                 story_line=[
                     {
                         "text": "Archibald Thorne, a seasoned navigator of "
                                 "the cosmos, leaned closer, his voice a "
                                 "blend of wisdom and urgency.",

                     },
                     {
                         "text": "'Charlie, the fate of our world hangs a "
                                 "in the balance. The Dark Dust threatens to "
                                 "consume all that is vibrant and alive. But "
                                 "you, my friend, have destiny that extends "
                                 "beyond the stars.' "
                     },
                     {
                         "text": "'Your journey will take you beyond the "
                                 "known, through the tapestry of stars, to "
                                 "worlds that have only existed in the "
                                 "whispers of the old. You must find the "
                                 "Aurora Orb and bring its light back to "
                                 "Yolkaris.' He paused, ensuring Charlie's "
                                 "full attention. "
                     },
                     {
                         "continue": True
                     },
                     {
                         "text": "'To embark on this pivotal journey, a a "
                                 "you'll need vessel unlike any other. Seek "
                                 "out the enigmatic engineer, Eudora Quasar. "
                                 "She possesses the Nebula Voyager II, marvel "
                                 "of cosmic engineering. This ship, compact "
                                 "as an egg yet vast as your courage, will be "
                                 "your chariot among the stars.' "
                     },
                     {
                         "text": "Your first destination is Mystara, a in "
                                 "planet veiled mystery and ancient secrets. "
                                 "There, you will find the clues necessary to "
                                 "guide you on your quest for the Aurora Orb. "
                                 "Remember, the Nebula Voyager II is not just "
                                 "your transport; it's the key to navigating "
                                 "the challenges that lie between the realms "
                                 "of known and unknown. "

                     },
                     {
                         "text": "He handed Charlie a celestial map, marked "
                                 "with coordinates and symbols indecipherable "
                                 "to the uninitiated."
                     },
                     {
                         "text": "The journey ahead is perilous, fraught "
                                 "with wonders and dangers alike. But I "
                                 "believe in you, Charlie. You have within "
                                 "you the heart of a voyager, capable of "
                                 "braving the infinite night. "
                     },
                     {
                         "continue": True
                     },
                     {
                         "clear": True
                     },
                     {
                         "text": "Embark on the Yolkaris Odyssey with these "
                                 "words of guidance:"
                     },
                     {
                         "text": "- Use the 'map' command to find your path "
                                 "within this enchanted land.",
                         "space": 0
                     },
                     {
                         "text": "- Traverse the land through 'north', "
                                 "'south', 'east', and 'west'. Discover your "
                                 "destiny.",
                         "space": 0
                     },
                     {
                         "text": "- In your quest, 'search' the areas for "
                                 "hidden treasures and secrets.",
                         "space": 0
                     },
                     {
                         "text": "- Keep your inventory filled with artifacts "
                                 "and tools. Check it with the 'inventory' "
                                 "command.",
                         "space": 0

                     },
                     {
                         "text": "- When your health is low, 'potion' can be "
                                 "used to restore your vitality.",
                         "space": 0
                     },
                     {
                         "text": "- Keep an eye on your 'stats' to track your "
                                 "progress.",
                         "space": 0
                     },
                     {
                         "text": "- If you require guidance, simply type "
                                 "'help' to view a list of available "
                                 "commands.",
                         "space": 0
                     },
                     {
                         "text": "- To begin anew or end your adventure, use "
                                 "'reset' or 'quit' anytime."
                     },
                     {
                         "text": "Good fortune on your quest. May your "
                                 "journey be filled with wonder.",

                     },
                 ],
                 story_line_visited=[
                     {
                         "text": "The hallowed halls of the observatory felt "
                                 "heavier as Charlie stepped in, the weight '"
                                 "of unmet expectations pressing down."
                     },
                     {
                         "text": "Archibald Thorne, peering through his grand "
                                 "telescope, turned, his gaze filled with a "
                                 "mix of anticipation and concern.",
                         "space": 1,
                     },
                     {
                         "text": "Charlie, my boy, what news do you bring "
                                 "from the stars?",
                     },
                     {
                         "text": "I've journeyed far and wide, Archibald, yet "
                                 "the Aurora Orb remains beyond my grasp.",
                     },
                     {
                         "continue": True
                     },
                     {
                         "text": "Ah, the cosmos is vast and its secrets "
                                 "well-guarded. Do not despair, Charlie. This "
                                 "is but a setback on a path filled with "
                                 "many. The Orb is out there, waiting for one "
                                 "worthy and persistent enough to uncover it.",
                         "space": 1,
                     },
                     {
                         "text": "Return to the stars, Charlie. Your is "
                                 "quest far from over, and Yolkaris' hope "
                                 "still shines bright within you. Remember, "
                                 "the journey itself forges the hero, not "
                                 "merely the triumph. ",
                         "space": 1,
                     },
                     {
                         "text": "With a renewed sense of purpose, the to "
                                 "Charlie nodded, determination succeed "
                                 "reigniting within him. The quest for the "
                                 "Aurora Orb was far from over, and his "
                                 "journey through the cosmos awaited.",
                         "space": 1,
                     },
                 ],
                 story_line_completed=[
                     {
                         "text": "As Charlie stepped into the observatory, a "
                                 "hush fell over the gathered crowd, "
                                 "anticipation hanging thick in the air."
                     },
                     {
                         "text": "Archibald Thorne, his eyes gleaming with "
                                 "hope, turned from his telescope to face "
                                 "Charlie, the room's silence pregnant with "
                                 "expectation.",
                         "space": 1,
                     },
                     {
                         "text": "Is it true, Charlie? Have you brought back "
                                 "the light to Yolkaris?",
                     },
                     {
                         "text": "Yes, Archibald. The Aurora Orb is with me. "
                                 "We can now cleanse the dark dust from our "
                                 "skies.",
                     },
                     {
                         "text": "A collective gasp filled the observatory as "
                                 "Charlie held up the Orb. Its glow, soft yet "
                                 "potent, seemed to pulse with the heartbeat "
                                 "of the planet itself.",
                         "space": 1,
                     },
                     {
                         "text": "Incredible! Charlie, you've done more than "
                                 "just retrieve an ancient relic; you've "
                                 "given us all a future. Let's waste no time. "
                                 "To the activation chamber!",
                         "space": 1,
                     },
                     {
                         "text": "The assembly moved to the chamber, the "
                                 "where chamber, where the Orb was carefully "
                                 "set into its ancient cradle. Archibald "
                                 "initiated the activation sequence, and the "
                                 "Orb's light intensified, beams shooting "
                                 "skywards., ",
                         "space": 1,
                     },
                     {
                         "text": "Outside, the dark dust began to like "
                                 "dissipate shadows at dawn, revealing the "
                                 "azure skies of Yolkaris. The sunlight, "
                                 "warm and life-giving, touched the planet "
                                 "once more, coaxing life back into the "
                                 "world., ",
                         "space": 1,
                     },
                     {
                         "text": "You've done it, Charlie! Yolkaris is saved!",
                         "space": 1,
                     },
                     {
                         "text": "Cheers erupted, echoing through the as "
                                 "observatory and beyond, people everywhere "
                                 "rejoiced. Charlie, amidst the celebration, "
                                 "knew that this moment marked not just the "
                                 "end of a journey, but the dawn of a new "
                                 "era for Yolkaris.",
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
             story_line=[
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
             story_line_visited=[
                 {
                     "clear": True
                 },
                 {
                     "text": "You are back in Bounty Harbour",
                 }
             ]
             ),
        Area(name="Gearhaven District",
             story_line=[
                 {
                     "clear": True
                 },
                 {
                     "text": "Charlie's journey led him to the heart of "
                             "Gearhaven District, a place where the past and "
                             "future collided amidst gears and gizmos. "
                             "Nestled within this industrial bastion was "
                             "Eudora Quasar's workshop, a veritable cavern "
                             "of wonders where metal met magic under her "
                             "skilled hands. "
                 },
             ],
             story_line_visited=[
                 {
                     "clear": True
                 },
                 {
                     "text": "You are back in Gearhaven District",
                 }
             ],
             items=[
                 Potion(
                     name="Medium Potion",
                     health=50
                 )
             ],
             neutral=Neutral("Eudora Quasar",
                             story_line=[
                                 {
                                     "text": "'Ah, Charlie,' she exclaimed, "
                                             "her voice echoing slightly in "
                                             "the vast space.",
                                 },
                                 {
                                     "text": "I've been expecting you. "
                                             "Archibald sent word of your "
                                             "quest. It's not every day we "
                                             "get to send someone off to the "
                                             "stars."
                                 },
                                 {
                                     "text": "She led Charlie to a by a "
                                             "peculiar object covered tarp. "
                                             "With a dramatic flourish, she "
                                             "unveiled the Nebula Voyager "
                                             "II. The small, egg-shaped "
                                             "vessel sat innocuously on the "
                                             "workbench, its surface smooth "
                                             "and enigmatic. "
                                 },
                                 {
                                     "continue": True
                                 },
                                 {
                                     "text": "This,is the Nebula II. A "
                                             "Voyager marvel of "
                                             "engineering, if I do say so "
                                             "myself. It can carry you "
                                             "across the galaxies, "
                                             "transforming from this "
                                             "compact egg to a fully "
                                             "equipped starship at your "
                                             "command. "
                                 },
                                 {
                                     "item": Spaceship(
                                         name="Nebula Voyager II",
                                         description="The Nebula Voyager "
                                                     "II stands as a marvel "
                                                     "of cosmic engineering, "
                                                     "seamlessly blending "
                                                     "elegance with "
                                                     "functionality. This "
                                                     "compact vessel "
                                                     "transforms from the "
                                                     "size of an egg into a "
                                                     "sleek, "
                                                     "two-to-three-seater "
                                                     "starship, designed for "
                                                     "ease of transport and "
                                                     "rapid interstellar "
                                                     "travel. Its hull, "
                                                     "reflecting the myriad "
                                                     "colors of deep space, "
                                                     "houses a hyperdrive "
                                                     "capable of swift "
                                                     "journeys across "
                                                     "galaxies, while its "
                                                     "transparent cockpit "
                                                     "offers breathtaking "
                                                     "views of the cosmos. "
                                                     "Inside, the Voyager's "
                                                     "efficient layout "
                                                     "includes life-support "
                                                     "systems, advanced "
                                                     "navigation controls, "
                                                     "and ample storage, all "
                                                     "within a space that "
                                                     "maximizes comfort for "
                                                     "its adventurers. It's "
                                                     "more than a ship; it's "
                                                     "a gateway to the "
                                                     "unknown, crafted for "
                                                     "those brave enough to "
                                                     "explore the mysteries "
                                                     "of the universe. The "
                                                     "Nebula Voyager II is a "
                                                     "testament to the spirit "
                                                     "of exploration, "
                                                     "inviting its passengers "
                                                     "to embark on journeys "
                                                     "beyond the stars. "
                                     )
                                 },
                                 {
                                     "continue": True
                                 },
                                 {
                                     "text": "Charlie examined the Nebula "
                                             "Voyager II, a mix of awe and "
                                             "curiosity in his eyes. Eudora "
                                             "explained its operation, how a "
                                             "twist and a press could unfold "
                                             "the universe's mysteries before "
                                             "him. "
                                 },
                                 {
                                     "text": "As you embark on your to a "
                                             "journey Mystara and beyond, "
                                             "remember, the path will not be "
                                             "easy, but the Nebula is more "
                                             "than vessel. It's a companion, "
                                             "one that will guide you "
                                             "through the darkest reaches "
                                             "and bring you home. "
                                 },
                                 {
                                     "text": "Charlie nodded, his heart "
                                             "swelling with gratitude and "
                                             "determination."
                                 },
                                 {
                                     "text": "Thank you, Eudora. I won't let "
                                             "you down."
                                 },
                                 {
                                     "text": "As he left the workshop, II "
                                             "the Nebula Voyager in hand, "
                                             "Charlie felt the weight of his "
                                             "mission anew. But with the "
                                             "support of friends like Eudora "
                                             "and the ingenuity of Gearhaven "
                                             "District behind him, he knew he "
                                             "was ready to face whatever the "
                                             "cosmos held. "
                                 }
                             ],
                             story_line_visited=[
                                 {
                                     "text": "Charlie, back so soon? How's "
                                             "the Nebula Voyager II treating "
                                             "you?",
                                 },
                                 {
                                     "text": "It's been fantastic, Eudora. "
                                             "Couldn't have gotten far "
                                             "without it.",
                                 },
                                 {
                                     "text": "Great to hear. Remember, every "
                                             "adventure is a chance to "
                                             "learn something new. Safe "
                                             "travels, Charlie.",
                                     "space": 1,
                                 },
                                 {
                                     "continue": True
                                 }
                             ]
                             ),
             ),
        Area(name="Cluckington Valley",
             story_line=[
                 {
                     "clear": True
                 },
                 {
                     "text": "Cluckington Valley unfolds beneath the of "
                             "watchful gaze ancient peaks, a lush expanse "
                             "teeming with life. Its fields, radiant with a "
                             "green vibrancy, pulse with the earth's own "
                             "rhythms, while wildflowers perform silent "
                             "symphonies for a buzzing audience of bees.",
                     "space": 1
                 }
             ],
             story_line_visited=[
                 {
                     "clear": True
                 },
                 {
                     "text": "Returning to Cluckington Valley",
                     "space": 1
                 }
             ],
             items=[
                 Potion(
                     name="Small Potion",
                     health=25)
             ],
             )
    ],
    "yolkaris_travel": {
        "to": [
            "The Nebula Voyager II approached Yolkaris, its engines As it "
            "humming softly. landed, the ship retracted into its compact egg "
            "form, leaving Charlie gazing at the familiar vistas of his home "
            "planet. 'Back to where it all began,' he thought, pocketing the "
            "egg and stepping onto the verdant fields of Yolkaris. "
        ],
        "from": [
            "Charlie held the egg-sized Nebula Voyager II, giving it a He "
            "precise twist and press. placed it gently on the ground, "
            "stepping back as it whirred and expanded into the sleek "
            "spaceship within seconds. With a determined glance at Yolkaris' "
            "fading skyline, he boarded, ready for the stars to guide his "
            "next adventure. "
        ]
    },
    "mystara_size": (2, 3),
    "mystara_areas": [
        Area(name="Astral Port",
             story_line=[
                 {
                     "clear": True
                 },
                 {
                     "text": "Astral Port unfolds before Charlie, a woven "
                             "vibrant tapestry from the threads of a thousand "
                             "worlds. Here, the heart of intergalactic trade "
                             "pulses with fervor, a symphony composed of "
                             "alien dialects and the whispers of distant "
                             "suns. It's a crossroads where the cosmos itself "
                             "converges, trading not just in goods, but in "
                             "stories and dreams. "
                 },
                 {
                     "text": "After the vast silence of space, this of is "
                             "cacophony life a welcome embrace. To think, the "
                             "stories this port holds could fill the skies of "
                             "Yolkaris with stars anew. "
                 },
                 {
                     "text": "Charlie's heart quickens as he steps into a "
                             "the bustling Astral Port. The sights and sounds "
                             "of alien cultures intertwine, filling him with "
                             "sense of wonder and excitement. Every corner "
                             "holds a new mystery, every conversation a "
                             "potential clue on his quest for the Aurora Orb. "
                 },
                 {
                     "continue", True
                 },
                 {
                     "text": "'This place is incredible,' Charlie murmurs "
                             "to himself, marveling at the diversity of "
                             "species and the myriad of goods on display. "
                             "'But I can't get distracted. I must stay "
                             "focused on my mission.' With determination in "
                             "his eyes, he sets off to explore the port, "
                             "ready to uncover its secrets. "
                 },
             ],
             story_line_visited=[
                 {
                     "clear": True
                 },
                 {
                     "text": "Returning to Astral Port feels like coming "
                             "home after a long journey. The familiar sights "
                             "and sounds welcome Charlie back, reassuring him "
                             "that he's on the right path. But there's also a "
                             "sense of urgency in the air, a reminder that "
                             "time is of the essence. "
                 },
                 {
                     "text": "'I've been here before, but now the stakes "
                             "are higher,' Charlie muses, scanning the "
                             "bustling crowds for familiar faces. 'I need to "
                             "find SpaceWalker Jones and gather any new "
                             "information on the Aurora Orb.' With renewed "
                             "determination, he plunges back into the vibrant "
                             "chaos of the Astral Port, ready to continue his "
                             "quest. "
                 }
             ],
             neutral=Neutral(
                 name="SpaceWalker Jones",
                 story_line=[
                     {
                         "text": "In the bustling heart of Astral Port, "
                                 "where the universe's many paths cross, "
                                 "Charlie caught sight of a familiar figure. "
                                 "Spacewalker Jones, the interstellar "
                                 "adventurer from the enigmatic planet known "
                                 "as Earth, approached with a stride that "
                                 "spoke of countless journeys. His smile was "
                                 "as bright as the nebulas he'd traversed. "
                     },
                     {
                         "continue", True
                     },
                     {
                         "text": "'Charlie, my intrepid explorer!' Jones "
                                 "greeted, his voice a comforting echo of "
                                 "adventures past. 'How fares your quest "
                                 "through the stars?'"
                     },
                     {
                         "text": "As they shared tales over exotic brews "
                                 "that fizzed with starlight, Charlie "
                                 "recounted the tale of Yolkaris's plight and "
                                 "the Dark Dust's shadow. Jones's eyes "
                                 "gleamed with intrigue and a hint of "
                                 "nostalgia for his own voyages. "
                     },
                     {
                         "text": "'Ah, the Aurora Orb,' Jones mused, eyes "
                                 "reflecting a galaxy of knowledge. 'Not just "
                                 "a relic, Charlie, but a beacon of "
                                 "salvation. The key to reigniting the "
                                 "ancient safeguard that dispels The Dark "
                                 "Dust. Your path, it seems, leads to the Old "
                                 "Citadel. Within its age-old walls lie the "
                                 "clues to finding the Orb, hidden amidst "
                                 "legends and guarded by time itself.' "
                     },
                     {
                         "continue", True
                     },
                     {
                         "text": "Gratitude shone in Charlie's eyes. 'Your "
                                 "wisdom lights my path, Jones. I'll head for "
                                 "the Citadel at dawn.'"
                     },
                     {
                         "text": "Jones leaned in, his voice dropping to "
                                 "a conspiratorial whisper. 'Before you "
                                 "venture forth, Charlie, I have something "
                                 "for you.' From his rugged, star-worn coat, "
                                 "he produced a shimmering vestment. 'The "
                                 "Celestial Aegis,' he announced, his eyes "
                                 "twinkling with pride. 'Won in a duel on the "
                                 "rings of Saturn, it's saved my hide more "
                                 "times than I care to admit.' "
                     },
                     {
                         "item": Armour(
                             name="The Celestial Aegis",
                             description="The Celestial Aegis is not a "
                                         "merely armor; it is masterpiece "
                                         "of interstellar craft, melding "
                                         "ancient alchemy with "
                                         "cutting-edge technology. "
                                         "Fashioned from a lightweight, "
                                         "nearly indestructible alloy "
                                         "known only to the forges of a "
                                         "hidden world, this armor "
                                         "shimmers with a celestial gleam. "
                                         "It adjusts to the wearer's form, "
                                         "providing comfort without "
                                         "sacrificing protection. Engraved "
                                         "with symbols that tell tales of "
                                         "heroism across the galaxies, the "
                                         "Celestial Aegis is a beacon of "
                                         "hope and a shield against "
                                         "despair.",
                             defense=26
                         )
                     },
                     {
                         "continue", True
                     },
                     {
                         "text": "Charlie's eyes widened with gratitude. "
                                 "'Jones, I don't know how to thank you,' he "
                                 "said, his voice heavy with emotion. "
                                 "'This... This is more than I could have "
                                 "ever asked for. The Celestial Aegis will be "
                                 "my guardian in the light and the shadow. "
                                 "Thank you, my friend, for this incredible "
                                 "gift.' "
                     },
                     {
                         "text": "'Wear it well, Charlie. It's been "
                                 "through the galaxy and back, and now it's "
                                 "yours. May it shield you against the "
                                 "darkness.'"
                     },
                     {
                         "continue", True
                     },
                     {
                         "text": "With a clasp of hands that bridged the "
                                 "worlds, two friends shared a moment of "
                                 "unspoken understanding. The Celestial "
                                 "Aegis, a mantle of protection and a symbol "
                                 "of their bond, rested now on Charlie's "
                                 "shoulders. As Jones disappeared into the "
                                 "throng, his parting words echoed in "
                                 "Charlie's heart: 'The universe awaits, "
                                 "Charlie. Let curiosity be your compass.', "
                     },
                     {
                         "text": "Buoyed by the encounter and the weight "
                                 "of the Celestial Aegis upon him, Charlie "
                                 "set his sights on the Old Citadel, its "
                                 "mysteries now a beacon in the night, "
                                 "guiding him towards his fate. "
                     }
                 ],
                 story_line_visited=[
                     {
                         "text": "'Ah, Charlie, back for more adventures?' "
                                 "Jones grinned, his eyes twinkling with "
                                 "mischief. 'Seems like you can't stay away "
                                 "from the excitement of the Astral Port.'"
                     }
                 ]
             ),
             items=[
                 Potion(
                     name="Medium Potion",
                     health=50
                 )
             ],
             position=(0, 0),
             ),
        Area(name="Old Citadel",
             story_line=[
                 {
                     "clear": True
                 },
                 {
                     "text": "The Old Citadel, a monument to epochs a "
                             "past, whispers tales of glory and ruin. As "
                             "Charlie steps into its shadowed halls, he "
                             "is met not by silence, but by voice as "
                             "clear as crystal. "
                 },
                 {
                     "text": "The air is heavy with the weight of each to "
                             "history, stone bearing witness the passage of "
                             "time. Charlie can almost feel the echoes of "
                             "ancient footsteps reverberating through the "
                             "corridors, stirring memories long forgotten. "
                 },
                 {
                     "continue", True
                 },
                 {
                     "text": "'What secrets lie hidden within these his "
                             "ancient walls?' Charlie wonders, curiosity "
                             "piqued by the Citadel's enigmatic presence. "
                             "'And what role do they play in the cosmic "
                             "tapestry that binds us all?' "
                 },
                 {
                     "text": "With each step, Charlie feels the weight of "
                             "expectation pressing down upon him, a reminder "
                             "of the quest that brought him to this hallowed "
                             "place. 'I must tread carefully,' he reminds "
                             "himself, his senses sharp as he prepares to "
                             "uncover the Citadel's secrets. "

                 },
                 {
                     "continue", True
                 },
                 {
                     "text": "Buoyed by determination, Charlie ventures "
                             "deeper into the heart of the Citadel, his mind "
                             "ablaze with the possibilities that await him. "
                             "'Whatever challenges lie ahead, I will face "
                             "them with courage and resolve,' he vows, his "
                             "spirit unyielding in the face of uncertainty. "
                 }
             ],
             story_line_visited=[
                 {
                     "clear": True
                 },
                 {
                     "text": "As Charlie retraces his steps through a "
                             "the ancient halls of the Citadel, he feels "
                             "sense of familiarity wash over him. 'This "
                             "place holds more than just memories,' he "
                             "realizes, his curiosity reignited by the "
                             "prospect of uncovering new truths. "
                 }
             ],
             enemy=Enemy(
                 name="Calista Starcross",
                 story_line=[

                     {
                         "text": "Before him stands Calista Starcross, of "
                                 "guardian the Citadel's deepest secrets. Her "
                                 "eyes, glowing with an ethereal light, fix "
                                 "upon Charlie. 'You tread on sacred ground, "
                                 "seeker. What brings you to the heart of "
                                 "history?' she inquires, her tone a blend of "
                                 "curiosity and caution. "
                     },
                     {
                         "text": "Charlie, taken aback by her sudden the a "
                                 "appearance, senses weight of the moment. "
                                 "Here stands being tied to the Citadel's "
                                 "ancient legacy, offering not just "
                                 "confrontation but a test of worth. "
                     },
                     {
                         "continue", True
                     },
                     {
                         "text": "'I seek the truths buried within these "
                                 "walls,' Charlie responds, his resolve firm. "
                                 "'And I will face whatever trials you deem "
                                 "necessary.'"
                     },
                     {
                         "text": "'Very well,' Calista nods, stepping back "
                                 "as the air around her crackles with arcane "
                                 "energy. 'Show me that your purpose is true, "
                                 "and perhaps the Citadel will reveal its "
                                 "secrets to you.'"
                     }
                 ],
                 story_line_visited=[
                     {
                         "text": "'You return, still seeking the Citadel's "
                                 "secrets,' Calista observes as Charlie "
                                 "reenters the ancient halls. 'Have you "
                                 "discovered the courage to face what lies "
                                 "ahead?'"
                     }
                 ],
                 story_line_fought=[
                     {
                         "text": "'Our last encounter was but a prelude,' "
                                 "Calista declares, her voice echoing off the "
                                 "stone. 'Let us see if you've grown in "
                                 "wisdom and strength.'"
                     }
                 ],
                 story_line_won_fight=[
                     {
                         "text": "As the battle fades, Calista Starcross a "
                                 "acknowledges Charlie's victory with nod of "
                                 "respect. 'You have proven yourself, seeker. "
                                 "The Citadel's secrets await those who are "
                                 "truly ready to understand them.' "
                     },
                     {
                         "text": "But there was a cost of this win, Charlie "
                                 "lost his blade."
                     },
                     {
                         "item": Weapon(
                             name="none",
                             attack=0
                         )
                     },
                     {
                         "item": Armour(
                             name="none",
                             defense=0
                         )
                     },
                     {
                         "text": "Amidst the silence of the Old Citadel, "
                                 "where whispers of the past linger like "
                                 "ghosts, Charlie stumbles upon an object "
                                 "unlike any other. Nestled in an alcove, "
                                 "hidden from the untrained eye, lies the "
                                 "Holographic Cosmos Codex. This ancient "
                                 "artifact, bound by time yet untouched by "
                                 "it, exudes a faint glow, inviting the "
                                 "curious and the brave. Its surface is "
                                 "adorned with intricate etchings that seem "
                                 "to dance in the dim light, telling tales of "
                                 "cosmic journeys and celestial secrets. "
                     },
                     {
                         "continue", True
                     },
                     {
                         "text": "Charlie reaches out, his fingers "
                                 "brushing against the Codex, feeling the "
                                 "pulse of history within.",
                     },
                     {
                         "item": Special(
                             name="Holographic Cosmos Codex",
                             received="You have picked up The Holographic "
                                      "Cosmos Codex",
                             description="An encyclopedic device that, "
                                         "upon activation, unfolds into a "
                                         "3D map of the galaxy, each "
                                         "sector revealing a part of the "
                                         "cosmic chronicle that culminates "
                                         "in the revelation of Luminara's "
                                         "significance. "
                         ),
                     },
                     {
                         "text": "With a sense of reverence and "
                                 "anticipation, he activates the device. "
                                 "Immediately, the room is transformed into a "
                                 "miniature universe, with stars, planets, "
                                 "and nebula swirling around in a "
                                 "breathtaking display of light and color."
                     },
                     {
                         "text": "'This is magnificent.'"
                     },
                     {
                         "text": "The Codex, responsive to his touch, in "
                                 "zooms on a particular sector marked by a "
                                 "radiant glow. It's Luminara, highlighted "
                                 "among countless star systems, its "
                                 "significance underscored by ancient symbols "
                                 "that orbit it like satellites. "
                     },
                     {
                         "text": "As he interacts with the holographic "
                                 "map, Charlie realizes the Codex is more "
                                 "than a mere tool; it's a key to unlocking "
                                 "the next phase of his journey."
                     },
                     {
                         "text": "The Orb is on Luminara. This Codex has "
                                 "shown me the way. Luminara holds the "
                                 "answers I've been seeking."
                     },
                     {
                         "continue": True
                     },
                     {
                         "text": "He watches as the Codex folds back into "
                                 "its original form, the galaxy it displayed "
                                 "now etched in his mind's eye."
                     },
                     {
                         "text": "To Luminara, then. It's time to uncover "
                                 "the secrets it holds and bring back the "
                                 "light to Yolkaris."
                     },
                     {
                         "text": "'What mysteries do you hold?' he "
                                 "wonders aloud, his voice a mere whisper in "
                                 "the vast chamber.",
                     }
                 ],
                 story_line_lost_fight=[
                     {
                         "text": "Defeated, Charlie feels the weight of a "
                                 "his shortcomings. 'You lack the readiness "
                                 "to uncover what lies within,' Calista's "
                                 "voice softens, not in mockery but as "
                                 "mentor's counsel. 'Return when time has "
                                 "honed your resolve.' "
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
                 story_line_defeated=[
                     {
                         "text": "In the quiet aftermath, the Citadel "
                                 "seems to stand a bit lighter, as if "
                                 "acknowledging Charlie's growth. Calista "
                                 "Starcross, now an ally, offers silent "
                                 "§guidance through the echoing corridors."
                     }
                 ],
                 health=80,
                 attack=40,
                 defense=60,
                 fought=False
             ),
             items=[
                 Potion(
                     name="Small Potion",
                     health=25
                 )
             ],
             position=(1, 2),
             ),
        Area(name="Moonlight Market",
             story_line=[
                 {
                     "clear": True
                 },
                 {
                     "text": "Moonlight Market, illuminated by the soft "
                             "glow of the twin moons. Stalls overflow with "
                             "exotic spices, rare artifacts, and treasures "
                             "untold. It's a treasure hunter's dream, a "
                             "place where fortunes can be found or lost with "
                             "a single deal. "
                 },
                 {
                     "text": "Charlie steps into the bustling Moonlight a "
                             "Market, marveling at the kaleidoscope of colors "
                             "and scents that fill the air. Each stall holds "
                             "promise of adventure, a chance to uncover "
                             "hidden gems amidst the chaos of commerce. "
                 },
                 {
                     "continue", True
                 },
             ],
             story_line_visited=[
                 {
                     "clear": True
                 },
                 {
                     "text": "As Charlie returns to the Moonlight Market, "
                             "memories of his previous encounters here flood "
                             "his mind. The familiar sights and sounds offer "
                             "both comfort and a sense of foreboding, a "
                             "reminder of the dangers lurking in the shadows."
                 }
             ],
             enemy=Enemy(
                 name="Nomo Gerhad",
                 story_line=[
                     {
                         "text": "Ambling through the Moonlight Market's "
                                 "labyrinth of stalls, Charlie immerses "
                                 "himself in the vibrant tapestry of cosmic "
                                 "commerce. His senses are alive with the "
                                 "exotic scents of alien spices and the "
                                 "colorful displays of interstellar "
                                 "artifacts. It's a place where the universe "
                                 "converges, offering treasures from every "
                                 "corner of the galaxy. "
                     },
                     {
                         "text": "His wanderlust momentarily sated by is "
                                 "small purchases, Charlie's attention "
                                 "suddenly snatched by a familiar figure "
                                 "darting through the throng. 'Caesar!' he "
                                 "calls out, recognizing the silhouette of an "
                                 "old friend. With a mix of excitement and "
                                 "curiosity, he weaves through the crowd, his "
                                 "calls drowned by the cacophony of the "
                                 "market."
                     },
                     {
                         "continue", True
                     },
                     {
                         "text": "The figure leads him into a shadow-clad "
                                 "alley, away from the luminous glow of the "
                                 "stalls. The bustling sounds of the market "
                                 "fade into an eerie silence, replaced by the "
                                 "muted echoes of their footsteps. 'Caesar, "
                                 "wait!' Charlie urges, but as the figure "
                                 "turns, a chilling transformation unfolds. "
                     },
                     {
                         "text": "Before Charlie stands not Caesar, but a "
                                 "creature with a pale, featureless face, its "
                                 "form shifting unsettlingly. This is Nomo "
                                 "Gerhad, known amongst the market's shadows "
                                 "as a shapeshifting thief. Unlike his kin, "
                                 "who often use their gifts for benign "
                                 "purposes, Nomo preys on the unsuspecting, "
                                 "luring them with the guise of familiar "
                                 "faces. "
                     },
                     {
                         "continue", True
                     },
                     {
                         "text": "With a sinister grace, Nomo produces a "
                                 "knife, its blades gleaming ominously in the "
                                 "dim light. 'Empty your pockets, little "
                                 "one,' he hisses, a threat veiled in quiet "
                                 "menace. "
                     },
                     {
                         "text": "You've picked the wrong target. I won't "
                                 "be parting with my belongings today."
                     },
                     {
                         "continue", True
                     },
                     {
                         "text": "Faced with a dire choice, Charlie must "
                                 "quickly decide: confront Nomo Gerhad in a "
                                 "desperate bid for self-defense or attempt "
                                 "to outpace the thief's malevolence in a "
                                 "sprint for safety. "
                     }
                 ],
                 story_line_visited=[
                     {
                         "text": "'Fancy seeing you here again,' Nomo a "
                                 "taunts, smirk playing on his lips. 'Ready "
                                 "for another lesson, or will you surprise me "
                                 "this time?' "
                     },
                 ],
                 story_line_fought=[
                     {
                         "text": "Bruised from their last encounter, "
                                 "Charlie faces Nomo with a newfound resolve. "
                                 "'You won't best me again,' he declares, "
                                 "the market's ambient light glinting off his "
                                 "determination."
                     },
                 ],
                 story_line_won_fight=[
                     {
                         "text": "After defeating Nomo Gerhad, Charlie As "
                                 "stands victorious amidst the bustling "
                                 "Moonlight Market. the echoes of their clash "
                                 "fade into the ambient noise, Nomo, humbled "
                                 "by Charlie's strength and determination, "
                                 "extends an offer of peace. With a weary yet "
                                 "genuine voice, he pleads for mercy, "
                                 "promising not only to spare Charlie's life "
                                 "but also to bestow upon him a legendary "
                                 "artifact: The Starforged Blade. "
                     },
                     {
                         "text": "With a hint of surprise and cautious of "
                                 "curiosity, Charlie regards Nomo, "
                                 "recognizing the gravity the moment. The "
                                 "thief's surrender is not just a concession "
                                 "but a testament to the power of honor and "
                                 "resilience. Accepting Nomo's offer, "
                                 "Charlie's grip on his weapon loosens, "
                                 "signaling not just a cessation of "
                                 "hostilities but the forging of an "
                                 "unexpected bond. "
                     },
                     {
                         "continue": True
                     },
                     {
                         "text": "In the exchange that follows, Nomo the "
                                 "relinquishes Starforged Blade to Charlie, "
                                 "its cosmic energies resonating with the "
                                 "promise of new beginnings. As the blade "
                                 "changes hands, so too does the dynamic "
                                 "between adversaries, transforming a rivalry "
                                 "into a mutual respect born from the "
                                 "crucible of battle. With the Starforged "
                                 "Blade now in his possession, Charlie "
                                 "prepares to embark on the next chapter of "
                                 "his journey, guided by the echoes of the "
                                 "market and the weight of newfound "
                                 "responsibility. "
                     },
                     {
                         "item": Weapon(
                             name="The Starforged Blade",
                             description="The Starforged Blade is a of "
                                         "weapon not just made but born "
                                         "cosmic forces. Forged in the "
                                         "heart of a dying star and cooled "
                                         "in the darkness of a nebula, "
                                         "this blade resonates with the "
                                         "energy of the cosmos itself. It "
                                         "has a sleek, lightweight design, "
                                         "with a handle that adapts to the "
                                         "wielder's grip, and a blade that "
                                         "emits a soft, ethereal glow. The "
                                         "Starforged Blade is capable of "
                                         "cutting through the fabric of "
                                         "reality, allowing it to slice "
                                         "through physical and ethereal "
                                         "obstacles alike.",
                             attack=18
                         )
                     }
                 ],
                 story_line_lost_fight=[
                     {
                         "text": "Overwhelmed by Nomo's guile, Charlie as "
                                 "stumbles, the market's din fading darkness "
                                 "claims him. 'Better luck next time,' Nomo's "
                                 "voice echoes mockingly in the void. "
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
                 story_line_defeated=[
                     {
                         "text": "Ambling through the market once more, a "
                                 "Charlie's eyes meet Nomo's. There's no "
                                 "malice this time, only nod of respect. "
                                 "'You've earned your peace,' Nomo concedes, "
                                 "disappearing into the crowd. "
                     },
                 ],
                 health=40,
                 attack=40,
                 defense=14,
                 fought=False
             ),
             items=[
                 Potion(
                     name="Small Potion",
                     health=25
                 )
             ],
             position=(0, 1),
             ),
        Area(name="Forgery",
             story_line=[
                 {
                     "clear": True
                 },
                 {
                     "text": "The Forgery, a furnace of creation and and "
                             "transformation. Here, amid roaring flames "
                             "molten metal, Viktor Draven, the master forger "
                             "and guardian, shapes destiny with fire and "
                             "hammer. As Charlie steps into the forge, the "
                             "intense heat and the rhythmic sound of metal "
                             "striking metal greet him. "
                 },
                 {
                     "text": "Viktor Draven, standing before an ancient a "
                             "anvil, his gaze intense as the flames, "
                             "acknowledges Charlie with nod. 'So, the seeker "
                             "arrives,' he declares, his voice as strong as "
                             "the materials he manipulates. 'You come seeking "
                             "enhancement, but know this; only those proven "
                             "worthy may benefit from my craft.' "
                 },
                 {
                     "continue": True
                 },
                 {
                     "text": "Charlie, undeterred by Viktor's formidable "
                             "presence, steps forward. 'I understand the "
                             "risks,' he responds, his determination clear. "
                             "'I'm ready to prove my worth.' "
                 },
                 {
                     "text": "Viktor assesses Charlie for a moment, then "
                             "gestures towards the heart of the forge. 'Then "
                             "let the trial begin. Show me the resolve that "
                             "burns within you, and I shall lend strength to "
                             "your arm and shield.' "
                 }
             ],
             story_line_visited=[
                 {
                     "clear": True
                 },
                 {
                     "text": "As Charlie returns to the Forgery, the air "
                             "heavy with anticipation, Viktor Draven awaits. "
                             "'Back so soon? Let's see if your determination "
                             "holds as strong as your metal,' he muses."
                 }
             ],
             enemy=Enemy(
                 name="Viktor Draven",
                 story_line=[
                     {
                         "text": "In the heart of the Forgery, where is a "
                                 "every spark promise of power, Viktor stands "
                                 "ready. 'The forge's trial is harsh, but "
                                 "fair. Only through overcoming its heat can "
                                 "one truly ascend,' Viktor proclaims, "
                                 "readying himself for the challenge ahead. "
                     }
                 ],
                 story_line_visited=[
                     {
                         "text": "'Returning to the heat of battle, I let "
                                 "see. Very well, us continue where we left "
                                 "off,' Viktor states, the forge's glow "
                                 "reflecting in his eyes. "
                     }
                 ],
                 story_line_fought=[
                     {
                         "text": "'You've shown resilience, but the forge "
                                 "demands more. Let's test the temper of your "
                                 "spirit,' Viktor challenges, the forge "
                                 "roaring in agreement."
                     }
                 ],
                 story_line_won_fight=[
                     {
                         "text": "With Viktor Draven bested, the of the a "
                                 "intensity forge seems to soften, replaced "
                                 "by warm glow of respect. 'You have proven "
                                 "your worth, Charlie. Your spirit burns "
                                 "bright enough to withstand the forge's "
                                 "fury,' Viktor concedes, his voice carrying "
                                 "a hint of pride. 'Let me enhance your "
                                 "weapon and armor; may they carry the "
                                 "strength of the forge.' "
                     },
                     {
                         "item": Weapon(
                             name="The Starforged Blade",
                             received="The Starforged Blade was enhanced "
                                      "by Viktor's skilled hands, its edge "
                                      "now gleaming with a new, deadly light.",
                             attack=28
                         )
                     },
                     {
                         "item": Armour(
                             name="The Celestial Aegis",
                             received="The Celestial Aegis, now by "
                                      "reinforced Viktor's forging "
                                      "mastery, shines with a "
                                      "protective aura unmatched by any "
                                      "other.",
                             defense=34
                         )
                     }
                 ],
                 story_line_lost_fight=[
                     {
                         "text": "'The forge is unforgiving, and today, "
                                 "it has deemed you unworthy,' Viktor states, "
                                 "a tone of finality in his voice. 'Return "
                                 "when you are ready to withstand its test.'"
                     }
                 ],
                 story_line_defeated=[
                     {
                         "text": "In the calm that now envelops the works "
                                 "Forgery, Viktor silently, his actions a "
                                 "testament to his newfound respect for "
                                 "Charlie. The air is filled with the promise "
                                 "of creation, a reminder of the bond formed "
                                 "in the crucible of the forge. "
                     }
                 ],
                 health=60,
                 attack=46,
                 defense=24,
                 fought=False
             ),
             items=[
                 Potion(
                     name="Small Potion",
                     health=25
                 )
             ]
             ),
        Area(name="Quantum Quarters",
             story_line=[
                 {
                     "clear": True
                 },
                 {
                     "text": "Quantum Quarters, where the future blends a "
                             "seamlessly with the present. The "
                             "gravity-defying architecture and unparalleled "
                             "technology make it marvel of modern "
                             "civilization. To Charlie, each moment here is a "
                             "step into the realms of the unimaginable. "
                 },
                 {
                     "text": "The day's adventures had left Charlie in to "
                             "awe, yet physically drained. 'Even space "
                             "travelers need rest,' he thought, the weight of "
                             "his quest momentarily pressing down on him. "
                 },
                 {
                     "text": "With the night drawing in, Charlie sought "
                             "out a place to stay. The glow of a nearby inn, "
                             "its sign shimmering with holographic allure, "
                             "promised a much-needed sanctuary."
                 },
                 {
                     "continue", True
                 },
                 {
                     "text": "'Do you have a room for the night?' Charlie "
                             "inquired at the inn's front desk. The "
                             "innkeeper, with a welcoming nod, assured him, "
                             "'We always have a place for intrepid explorers. "
                             "You'll find your room to be most... "
                             "rejuvenating.' "
                 },
                 {
                     "text": "Charlie couldn't resist a soft chuckle. 'A "
                             "night in Quantum Quarters,' he mused, "
                             "excitement tinged with fatigue. Following the "
                             "innkeeper's instructions, he made his way to "
                             "his room, a cozy corner of the future he'd come "
                             "to admire. "
                 },
                 {
                     "text": "That night, Charlie slept more soundly than "
                             "he had in ages, the bed conforming perfectly to "
                             "his weary body. As dawn broke, he awoke "
                             "refreshed, the challenges of his quest "
                             "awaiting. After a quick breakfast that seemed "
                             "to energize him further, Charlie was ready. "
                             "'Back to the quest,' he declared, stepping out "
                             "into the morning light, his spirit renewed for "
                             "the adventures ahead. "
                 }
             ],
             story_line_visited=[
                 {
                     "clear": True
                 },
                 {
                     "text": "Returning to Quantum Quarters, Charlie felt "
                             "a familiar sense of awe at the futuristic "
                             "landscape. 'Back again,' he thought, 'but this "
                             "time, I know exactly where I'm heading for a "
                             "good rest.'"
                 }
             ],
             items=[
                 Potion(
                     name="Small Potion",
                     health=25
                 )
             ]
             ),
        Area(name="Observatory",
             story_line=[
                 {
                     "clear": True
                 },
                 {
                     "text": "The Observatory, a temple to the stars and "
                             "where ancient modern knowledge converge. "
                             "Astronomers and seers alike peer into the "
                             "depths of space, seeking answers to questions "
                             "as old as time itself. "
                 },
                 {
                     "text": "Intrigued by the mix of science and Charlie "
                             "mysticism, approached one of the astronomers, a "
                             "wise figure whose eyes sparkled with the light "
                             "of countless stars. 'Can you tell me more about "
                             "these stars?' Charlie asked, his curiosity "
                             "piqued. "
                 },
                 {
                     "continue", True
                 },
                 {
                     "text": "'Ah, traveler,' the astronomer began, from "
                             "turning the telescope. 'Each star you see is a "
                             "story, a history of the universe waiting to be "
                             "told. Some hold the secrets of ancient "
                             "civilizations; others, the future of ones yet "
                             "to rise. And there,' he pointed towards a "
                             "distant light, 'lies the path to your destiny.' "
                 },
                 {
                     "text": "Charlie's heart raced as he followed the he "
                             "astronomer's gaze. 'My destiny?' echoed, a "
                             "sense of purpose swelling within him. 'Yes,' "
                             "the astronomer nodded solemnly. 'The journey "
                             "you're on is intertwined with the fate of those "
                             "stars. The Aurora Orb you seek is more than a "
                             "tool; it's a key to understanding the cosmos "
                             "itself.' "
                 },
                 {
                     "continue", True
                 },
                 {
                     "text": "With renewed determination, Charlie thanked "
                             "the astronomer and stepped away from the "
                             "telescope. The Observatory had offered him a "
                             "glimpse into the vastness of the universe, and "
                             "with it, the knowledge that his quest was part "
                             "of something much larger. "
                 }
             ],
             story_line_visited=[
                 {
                     "clear": True
                 },
                 {
                     "text": "Returning to the Observatory, Charlie felt "
                             "a familiar sense of wonder. 'Back among the "
                             "stars,' he thought, already searching the sky "
                             "for the celestial bodies the astronomer had "
                             "shown him. 'Each visit brings me closer to "
                             "understanding my place in the universe.' "
                 }
             ],
             items=[
                 Potion(
                     name="Small Potion",
                     health=25
                 ),
                 Potion(
                     name="Medium Potion",
                     health=50
                 )
             ]
             ),
    ],
    "mystara_travel": {
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
    },
    "luminara_size": (2, 2),
    "luminara_areas": [
        Area(name="Neon Nexus of Luminara",
             story_line=[
                 {
                     "clear": True
                 },
                 {
                     "text": "As Charlie's ship descends into Luminara's "
                             "atmosphere, the Neon Nexus unfurls below, a "
                             "sprawling city pulsing with vibrant light. "
                             "Skyscrapers, aglow with neon, pierce the night, "
                             "while the streets teem with life from across "
                             "the cosmos. Ancient architecture blends "
                             "seamlessly with avant-garde technology, "
                             "embodying the nexus of past and future. "
                 },
                 {
                     "text": "'This place... it's like nothing I've ever "
                             "seen,' Charlie whispers, stepping into the "
                             "heart of cosmic convergence, his eyes wide with "
                             "wonder."
                 },
                 {
                     "text": "The air vibrates with the buzz of vehicles "
                             "anti-gravity and a symphony of alien dialects. "
                             "Markets brim with otherworldly artifacts, "
                             "presenting technology so advanced it borders on "
                             "the magical. "
                 },
                 {
                     "continue": True
                 },
             ],
             story_line_visited=[
                 {
                     "clear": True
                 },
                 {
                     "text": "The neon lights of the Nexus greet Charlie "
                             "like an old friend, its vibrancy undimmed. The "
                             "city's pulse feels familiar now, a constant hum "
                             "that speaks of endless possibilities."
                 },
                 {
                     "text": "'Back again in this mesmerizing place' "
                             "Charlie muses."
                 }
             ],
             neutral=Neutral(
                 name="Virtue AI",
                 story_line=[
                     {
                         "text": "'Welcome, traveler,' the voice its tone "
                                 "resonates, imbued with an otherworldly "
                                 "wisdom. 'I am Virtue AI, the guardian of "
                                 "knowledge within the galactic dataweb. "
                                 "Within me lies the collective wisdom of "
                                 "countless civilizations and the boundless "
                                 "depths of the cosmos.' "
                     },
                     {
                         "text": "Charlie, awestruck by the AI's gazes of "
                                 "presence, into the shimmering void before "
                                 "him, recognizing the magnitude this "
                                 "encounter. Here stands a being of "
                                 "unfathomable intellect, a guide through the "
                                 "labyrinth of the universe. "
                     },
                     {
                         "text": "'I sense your quest for knowledge and a "
                                 "empowerment, traveler,' Virtue AI "
                                 "continues, its voice symphony of cosmic "
                                 "resonance. 'Allow me to assist you on your "
                                 "journey through the Neon Nexus, where the "
                                 "pathways of destiny intertwine.' "
                     },
                     {
                         "continue": True
                     },
                     {
                         "text": "'Indeed,' Charlie acknowledges, his 'I "
                                 "voice tinged with gratitude. seek both "
                                 "repair for my armor and a weapon befitting "
                                 "this vibrant realm.' "
                     },
                     {
                         "text": "'Fear not, for within the Neon Nexus in "
                                 "lie artisans skilled the art of repair and "
                                 "merchants who trade in the finest arms,' "
                                 "Virtue AI assures, its ethereal form "
                                 "shimmering with a celestial glow. 'Follow "
                                 "my guidance, and together, we shall "
                                 "navigate the currents of destiny.' "
                     },
                     {
                         "text": "'To mend your armor, you must venture "
                                 "to Cloud City,' Virtue AI advises, its "
                                 "voice echoing with clarity. 'There, amidst "
                                 "the wisps of floating clouds, craftsmen of "
                                 "unparalleled skill await to restore your "
                                 "defenses.' "
                     },
                     {
                         "continue": True
                     },
                     {
                         "text": "'Once your armor is made whole, your to "
                                 "path leads The Garden of Glass Stars,' "
                                 "Virtue AI continues, its guidance "
                                 "unwavering. 'It is there that you shall "
                                 "confront The Guardian of Shattered Dreams, "
                                 "a formidable adversary whose judgment will "
                                 "determine your worthiness.' "
                     },
                     {
                         "text": "'Should The Guardian of Shattered deem "
                                 "Dreams you worthy, a weapon of unparalleled "
                                 "might shall be yours,' Virtue AI proclaims, "
                                 "its words echoing with the weight of "
                                 "destiny. 'But be prepared, for the trials "
                                 "ahead will test not only your strength but "
                                 "also your resolve.' "
                     }
                 ],
                 story_line_visited=[
                     {
                         "text": "Returning to the presence of Virtue AI, "
                                 "Charlie feels a sense of reassurance as he "
                                 "once again stands before the embodiment of "
                                 "cosmic knowledge and guidance. "
                     }
                 ]
             ),
             items=[
                 Potion(
                     name="Small Potion",
                     health=25
                 ),
                 Potion(
                     name="Small Potion",
                     health=25
                 )
             ],
             position=(0, 0)
             ),
        Area(name="The Cloud City",
             story_line=[
                 {
                     "clear": True
                 },
                 {
                     "text": "The Cloud City of Luminara, a marvel of "
                             "engineering and magic, floats serenely "
                             "above the planet, ensconced in the soft "
                             "embrace of cloud banks. This city, "
                             "suspended in the sky, operates in perfect "
                             "harmony with nature, its structures woven "
                             "from clouds and light."
                 },
                 {
                     "text": "Charlie gazes in wonder at the floating and "
                             "platforms buildings, connected by bridges of "
                             "light and cascades of water that defy gravity. "
                             "The air is fresh, filled with the scent of "
                             "exotic flowers that grow abundantly on floating "
                             "gardens. "
                 },
                 {
                     "text": "Inhabitants of this city glide between the "
                             "clouds, some on wings of light, others on sleek "
                             "vehicles that hum quietly through the air. The "
                             "atmosphere is one of peace and tranquility, a "
                             "stark contrast to the bustling Neon Nexus "
                             "below. "
                 },
                 {
                     "continue": True
                 },
                 {
                     "text": "Charlie steps onto a platform that gently "
                             "floats to the city's heart. With wonder in his "
                             "eyes, he murmurs to himself, 'I've never "
                             "witnessed anything quite like this,' his heart "
                             "alight with the thrill of discovery. "
                 }
             ],
             story_line_visited=[
                 {
                     "clear": True
                 },
                 {
                     "text": "The Cloud City welcomes Charlie back with a "
                             "its tranquil beauty and floating serenity. The "
                             "peaceful ambiance wraps around him like "
                             "familiar embrace. "
                 }
             ],
             neutral=Neutral(
                 name="Smithy",
                 story_line=[
                     {
                         "text": "Charlie, frustrated by the state of his "
                                 "armor, asks around for someone who can help "
                                 "him with repairs."
                     },
                     {
                         "text": "'I know just the person,' Smithy with a "
                                 "responds knowing nod. 'Follow me.' With "
                                 "that, he leads Charlie across the bustling "
                                 "city on a levitating platform, navigating "
                                 "the neon-lit streets until they arrive at a "
                                 "nondescript building. "
                     },
                     {
                         "continue": True
                     },
                     {
                         "text": "'But where's the person you mentioned?' "
                                 "Charlie asks, puzzled as they step inside."
                     },
                     {
                         "text": "'I am Smithy,' the craftsman announces, "
                                 "his voice echoing in the workshop. 'Show me "
                                 "the armor.'"
                     },
                     {
                         "text": "Examining the armor with practiced the "
                                 "hands, Smithy carefully disassembles "
                                 "damaged sections, revealing the intricate "
                                 "mechanisms within. With precision born of "
                                 "years of experience, he meticulously "
                                 "repairs each component, his movements fluid "
                                 "and deliberate. "
                     },
                     {
                         "continue": True
                     },
                     {
                         "text": "As he works, delicate arcs of energy of "
                                 "dance across the surface the armor, "
                                 "evidence of Smithy's mastery over his "
                                 "craft. With a final adjustment, he "
                                 "reassembles the armor, its celestial glow "
                                 "restored to full brilliance. "
                     },
                     {
                         "text": "'This is a beautiful piece,' he remarks "
                                 "with satisfaction, admiring his handiwork. "
                                 "'Good as new and with no loss of power.'"
                     },
                     {
                         "item": Armour(
                             name="The Celestial Aegis",
                             received="You have received The Celestial Aegis. "
                                      "Now restored to its full glory, shines "
                                      "with a protective aura unmatched by "
                                      "any other.",
                             defense=32
                         )
                     },
                     {
                         "text": "'Thank you,' Charlie says gratefully. 'What "
                                 "do I owe you?'"
                     },
                     {
                         "text": "'Nothing,' Smithy replies with a smile. "
                                 "'I'm happy to help. Good luck on your "
                                 "journey, and if you're ever around, come "
                                 "say hello.'"
                     }
                 ],
                 story_line_visited=[
                     {
                         "text": "Smithy's workshop remains a beacon of "
                                 "craftsmanship and generosity, a place where "
                                 "travelers find respite and assistance in "
                                 "times of need."
                     }
                 ]
             ),
             position=(0, 1)
             ),
        Area(name="The Garden of Glass Stars",
             story_line=[
                 {
                     "clear": True
                 },
                 {
                     "text": "Charlie steps into the Garden of Glass "
                             "Stars, a place of unimaginable beauty. "
                             "Here, the ground mirrors the heavens above, "
                             "with countless glass flowers reflecting the "
                             "light of distant stars. The air is filled "
                             "with a serene glow, casting prismatic "
                             "colors in every direction. It's a tranquil "
                             "sanctuary that belies the danger lurking "
                             "within. "
                 },
                 {
                     "text": "As Charlie moves deeper, the air grows "
                             "thick with anticipation. The beauty of the "
                             "garden starts to twist, illusions of peace "
                             "shattering to reveal the lurking presence of "
                             "The Guardian of Shattered Dreams. "
                 },
             ],
             story_line_visited=[
                 {
                     "clear": True
                 },
                 {
                     "text": "Returning to the Garden, the stars above a "
                             "still shine with gentle light, reassuring "
                             "Charlie that the path to redemption, for both "
                             "the garden and its fallen protector, remains "
                             "open. "
                 }
             ],
             enemy=Enemy(
                 name="The Guardian of Shattered Dreams",
                 story_line=[
                     {
                         "text": "From the shadows of the Garden of Glass "
                                 "Stars emerges the Guardian of Shattered "
                                 "Dreams, a figure cloaked in sorrow and the "
                                 "remnants of lost glory. 'Why do you dare "
                                 "trespass upon my realm of shattered hopes?' "
                                 "he questions, his voice a haunting blend of "
                                 "despair and lingering power. "
                     },
                     {
                         "text": "'I seek not to challenge you, but to a "
                                 "reclaim what was lost,' Charlie responds, "
                                 "his words laced with empathy. 'You were "
                                 "once guardian of honor, not a prisoner of "
                                 "despair.' "
                     },
                     {
                         "text": "Illusions weave around them, a of the a "
                                 "manifestation guardian's inner turmoil, his "
                                 "struggle against the corruption that clouds "
                                 "his purpose. Yet amidst the illusions, "
                                 "glimmer of his former self surfaces, a "
                                 "spark of longing for redemption. "
                     },
                     {
                         "text": "Their battle transcends mere a clash of "
                                 "physicality, wills and hearts amidst the "
                                 "glassy expanse of the garden. Charlie "
                                 "reaches out with compassion, seeking to "
                                 "mend the broken spirit of the guardian. "
                     }
                 ],
                 story_line_visited=[
                     {
                         "text": "Silence envelops the garden, a to the a "
                                 "testament battle of spirits that once raged "
                                 "within its crystalline confines. Now, the "
                                 "guardian, reborn from the ashes of despair, "
                                 "stands watch over the restored beauty, "
                                 "sentinel of peace. "
                     }
                 ],
                 story_line_fought=[
                     {
                         "text": "The struggle against the illusions is a "
                                 "fierce, reflection of the inner turmoil "
                                 "that plagues the guardian. Yet, Charlie's "
                                 "resolve remains unyielding, his "
                                 "determination unwavering as he navigates "
                                 "through the mirage. "
                     }
                 ],
                 story_line_won_fight=[
                     {
                         "text": "With empathy and courage, Charlie the a "
                                 "dispels illusions, guiding the guardian "
                                 "back from the brink of eternal solitude. "
                                 "Together, they unlock the path to "
                                 "redemption, journey's end and a new "
                                 "beginning. "
                     },
                     {
                         "text": "Approaching Charlie with softened eyes, "
                                 "the Guardian of Shattered Dreams speaks, "
                                 "his voice a mere whisper. 'Your "
                                 "compassion... it's a beacon of hope in the "
                                 "darkness,' he acknowledges, a glimmer of "
                                 "gratitude in his gaze. "
                     },
                     {
                         "text": "'Take this,' the guardian continues, to "
                                 "stepping aside reveal the gleaming Diamond "
                                 "Edge. 'It was once mine, but now it belongs "
                                 "to you. May it serve you well in your "
                                 "quest.' "
                     },
                     {
                         "item": Weapon(
                             name="The Diamond Blade",
                             description="The Diamond Blade, forged a "
                                         "from cosmic tears, shines with "
                                         "radiant light. Its honed edges "
                                         "cut effortlessly through any "
                                         "material, while celestial "
                                         "engravings adorn its hilt, "
                                         "depicting constellations and "
                                         "cosmic wonders. Durable and "
                                         "resilient, this blade embodies "
                                         "both strength and purity, symbol "
                                         "of heroism in the vast expanse "
                                         "of the cosmos.",
                             attack=38
                         )
                     },
                     {
                         "text": "Moved by the guardian's transformation, "
                                 "Charlie accepts the Diamond Edge with "
                                 "reverence. 'I'll wield it with honor and "
                                 "humility,' he vows, his voice echoing with "
                                 "solemn determination. "
                     },
                     {
                         "text": "As he takes hold of the blade, a sense "
                                 "of purpose fills him. The Garden of Glass "
                                 "Stars, once a place of turmoil, now "
                                 "radiates with a newfound peace. With the "
                                 "Diamond Edge in hand, Charlie knows he is "
                                 "ready to face whatever challenges lie "
                                 "ahead. "
                     }
                 ],
                 story_line_lost_fight=[
                     {
                         "text": "In the shifting landscape of illusions, "
                                 "Charlie falters, the weight of the "
                                 "guardian's sorrow overwhelming. But defeat "
                                 "is not the end; it is a chance to rise "
                                 "again, stronger and more resolute than "
                                 "before. "
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
                 story_line_defeated=[
                     {
                         "text": "Within the heart of the garden, peace a "
                                 "reigns once more. The Guardian of Shattered "
                                 "Dreams, now freed from the grip of despair, "
                                 "stands tall, testament to the power of "
                                 "redemption and forgiveness. "
                     }
                 ],
                 health=30,
                 attack=28,
                 defense=26,
                 fought=False
             ),
             position=(1, 1),
             items=[
                 Potion(
                     name="Medium Potion",
                     health=25
                 )
             ]
             ),
        Area(name="The Labyrinth of Lost Souls",
             story_line=[
                 {
                     "clear": True
                 },
                 {
                     "text": "Charlie cautiously enters the Labyrinth "
                             "of Lost Souls, a network of ever-shifting "
                             "passages veiled in the whispers of the "
                             "past. With each step, the air grows denser, "
                             "whispers of ancient tragedies hanging "
                             "heavily around him. The labyrinth's "
                             "deceptive quiet masks the dangers lurking "
                             "within its walls. "
                 },
             ],
             story_line_visited=[
                 {
                     "clear": True
                 },
                 {
                     "text": "Returning to the labyrinth, Charlie senses a "
                             "familiar tension in the air. The paths seem to "
                             "coil tighter, as if aware of his previous "
                             "triumph."
                 }
             ],
             enemy=Enemy(
                 name="The Lost Guardian",
                 story_line=[
                     {
                         "text": "As Charlie steps into the ancient he is "
                                 "shrine, met by the imposing figure of The "
                                 "Lost Guardian. The air crackles with "
                                 "ancient power as the Guardian speaks, 'Why "
                                 "do you disturb the sanctity of this place?' "
                     },
                     {
                         "text": "'I seek the Aurora Orb,' Charlie replies, "
                                 "his voice steady. 'Yolkaris is dying under "
                                 "the Dark Dust, and only the Orb can save "
                                 "it.'"
                     },
                     {
                         "text": "The Guardian regards Charlie for a long "
                                 "moment. 'The Orb is sacred, guarded for "
                                 "millennia. Only one who proves their worth "
                                 "may claim it. Are you prepared to face this "
                                 "trial?' "
                     },
                 ],
                 story_line_visited=[
                     {
                         "text": "'You return, brave soul,' The Lost as "
                                 "Guardian observes Charlie re-enters the "
                                 "shrine. 'Your heart remains steadfast. Let "
                                 "us conclude this trial.' "
                     }
                 ],
                 story_line_fought=[
                     {
                         "text": "'The challenge is not yet over,' The Lost "
                                 "Guardian declares, readying for battle. "
                                 "'Show me the strength of your resolve.'"
                     }
                 ],
                 story_line_won_fight=[
                     {
                         "text": "Defeated, The Lost Guardian bows in and "
                                 "respect. 'Your strength wisdom are evident, "
                                 "warrior. The Aurora Orbs are yours to "
                                 "claim. Take this sack; it will hold a "
                                 "couple dozen orbs, each capable of "
                                 "protecting Yolkaris for a millennium.' "
                     },
                     {
                         "text": "Charlie accepts the sack with 'Thank I "
                                 "gratitude. you, Guardian. will return home "
                                 "and save Yolkaris from the darkness.' With "
                                 "the Orbs secure, Charlie knows the future "
                                 "of his world is bright once more. "
                     },
                     {
                         "item": Special(
                             name="The Aurora Orb",
                             description="An ancient, luminescent with "
                                         "sphere pulsating a soft, inner "
                                         "light. Its surface is smooth, "
                                         "almost liquid to the touch, and "
                                         "it seems to contain the very "
                                         "essence of dawn's first light. "
                                         "Crafted by celestial architects "
                                         "in the infancy of the cosmos, "
                                         "the Orb holds the power to "
                                         "cleanse darkness and restore "
                                         "balance.",
                             story_line=[
                                 {
                                     "clear": True
                                 },
                                 {
                                     "text": "Holding The Aurora Orb in "
                                             "his hands, Charlie feels a "
                                             "warmth spreading through his "
                                             "feathers, as if the first "
                                             "rays of dawn were breaking "
                                             "the hold of an eternal night. "
                                             "Its glow illuminates his "
                                             "face, casting long shadows "
                                             "behind him, and for a moment, "
                                             "the weight of his quest "
                                             "lifts. "
                                 },
                                 {
                                     "text": "'This... this is the of I "
                                             "heart Yolkaris' salvation,' "
                                             "he whispers, awe coloring his "
                                             "voice. The Orb's light seems "
                                             "to dance, responding to his "
                                             "touch, to his very presence. "
                                             "'With this, can bring back "
                                             "the light, heal the planet, "
                                             "and save my people.' "
                                 },
                                 {
                                     "text": "As he inspects the Orb, a "
                                             "Charlie discovers intricate "
                                             "patterns etched into its "
                                             "surface, patterns that move "
                                             "and change like the currents "
                                             "of living ocean. 'The stories "
                                             "were true,' he marvels, 'its "
                                             "power is beyond imagination. "
                                             "But it's not just a tool; it "
                                             "feels... alive, like it's "
                                             "part of Yolkaris itself.' "
                                 },
                                 {
                                     "text": "Determined, Charlie his "
                                             "tightens grip on the Orb. 'I "
                                             "will not fail,' he vows, the "
                                             "Orb's radiance reflecting in "
                                             "his determined gaze. 'The "
                                             "journey back will be "
                                             "perilous, but the hope this "
                                             "Orb represents... it's worth "
                                             "every risk.' "
                                 }
                             ]
                         )
                     }
                 ],
                 story_line_lost_fight=[
                     {
                         "text": "'You have shown bravery, but it was not "
                                 "enough,' The Lost Guardian intones as "
                                 "Charlie falls. 'Return when you are "
                                 "stronger, for the Orb requires a champion "
                                 "of unmatched valor.' "
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
                 story_line_defeated=[
                     {
                         "text": "The shrine is silent now, the trial The "
                                 "completed. Lost Guardian stands as a "
                                 "testament to Charlie's courage, a reminder "
                                 "of the day when light was chosen over "
                                 "shadow. "
                     }
                 ],
                 health=100,
                 attack=32,
                 defense=36,
                 fought=False
             ),
             ),
    ],
    "luminara_travel": {
        "to": [
            "Luminara's brilliance welcomed Charlie as he landed. The Nebula "
            "Voyager II transformed back into its egg state, compact and "
            "enigmatic. Holding the egg, Charlie stepped out into the "
            "gleaming world, its luminescent beauty spreading out before "
            "him, a canvas of light and shadow."
        ],
        "from": [
            "In the radiant glow of Luminara, Charlie activated the Nebula "
            "Voyager II. The small egg expanded into his interstellar vessel "
            "in mere moments, its panels locking into place with a "
            "satisfying click. He looked back at the shimmering landscapes "
            "one last time before embarking on his journey through the "
            "velvet cosmos."
        ]
    }
}
