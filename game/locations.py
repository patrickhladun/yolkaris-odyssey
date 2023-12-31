import random

class Location:
    def __init__(self, name, description, size, enemies, items, other_elements=None):
        self.name = name
        self.description = description
        self.size = size
        self.map = [[" " for _ in range(size[0])] for _ in range(size[1])]
        self.contents = {}  # Dictionary to track what's at each position
        self.player_position = (0, 0)
        self.enemies = enemies
        self.items = items
        self.other_elements = other_elements if other_elements else []
        self.randomly_place_elements()

    def randomly_place_elements(self):
        for enemy in self.enemies:
            self.place_on_map(enemy, "E")

        for item in self.items:
            self.place_on_map(item, "I")

        for element in self.other_elements:
            self.place_on_map(element, "O")  # O for Other Elements

    def place_on_map(self, element, symbol):
        position = self.get_random_position()
        while position in self.contents:
            position = self.get_random_position()  # Find an empty position

        self.contents[position] = element
        self.map[position[1]][position[0]] = symbol

    def get_random_position(self):
        x = random.randint(0, self.size[0] - 1)
        y = random.randint(0, self.size[1] - 1)
        return (x, y)

    def is_valid_position(self, position):
        x, y = position
        return 0 <= x < self.size[0] and 0 <= y < self.size[1]

    def describe(self):
        print(f"{self.name}: {self.description}")

    def display_map(self):
        print("Map:")
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                char = "P " if (x, y) == self.player_position else self.map[y][x] + "."
                print(char, end="")
            print()  # New line after each row
        print()  # Extra line for spacing

    def place_enemy(self, enemy, position):
        if self.is_valid_position(position):
            self.map[position[1]][position[0]] = "E"  # E for Enemy

    def place_item(self, item, position):
        if self.is_valid_position(position):
            self.map[position[1]][position[0]] = "I"  # I for Item

    def is_valid_position(self, position):
        x, y = position
        return 0 <= x < self.size[0] and 0 <= y < self.size[1]

class Yolkaris(Location):
    def __init__(self):
        super().__init__("Yolkaris", "A vibrant planet with diverse ecosystems.", (6,4))

class Mystara(Location):
    def __init__(self):
        super().__init__("Mystara", "A mysterious planet covered in thick jungles.", (16, 6))
        self.place_enemy(enemy_list[1], (3, 2))  # Example: placing an Orc
        self.place_item(armor_list[0], (0, 4))  # Example: placing Leather Armor

class Luminara(Location):
    def __init__(self):
        super().__init__("Luminara", "A radiant planet with a luminous landscape.", (14, 7))
        self.place_enemy(enemy_list[2], (4, 1))  # Example: placing a Troll
        self.place_item(weapon_list[2], (2, 2))  # Example: placing a Bow
        self.place_item(items_list[0], (6, 10))  # Example: placing a Potion


enemy_list = [
    Enemy("Goblin", 10, 5, 2, 5, []),
    Enemy("Orc", 20, 10, 5, 3, []),
    Enemy("Troll", 30, 15, 10, 2, []),
    Enemy("Dragon", 50, 20, 15, 1, [])
]

weapon_list = [
    Weapon("Sword", "A sharp sword", 5),
    Weapon("Axe", "A heavy axe", 10),
    Weapon("Bow", "A long bow", 15),
    Weapon("Staff", "A magical staff", 20)
]

armor_list = [
    Armor("Leather Armor", "A set of leather armor", 2),
    Armor("Chainmail Armor", "A set of chainmail armor", 5),
    Armor("Plate Armor", "A set of plate armor", 10)
]

items_list = [
    Item("Orb", "A magical orb")
]
