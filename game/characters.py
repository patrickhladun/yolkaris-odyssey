
class Character:
    """
    Initializes a character.
    """

    def __init__(self, name: str) -> None:
        self.name = name


class Player(Character):
    """
    Initializes a player character.
    """

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
            story_line: list,
            story_line_visited: list,
            story_line_fought: list,
            story_line_won_fight: list,
            story_line_lost_fight: list,
            story_line_defeated: list,
            health: int,
            attack: int,
            defense: int,
            fought: bool = False
    ) -> None:
        super().__init__(name)
        self.story_line = story_line
        self.story_line_visited = story_line_visited
        self.story_line_fought = story_line_fought
        self.story_line_won_fight = story_line_won_fight
        self.story_line_lost_fight = story_line_lost_fight
        self.story_line_defeated = story_line_defeated
        self.health = health
        self.attack = attack
        self.defense = defense
        self.fought = fought


class Neutral(Character):
    """
    Initializes a neutral character.
    """

    def __init__(
            self,
            name,
            story_line,
            story_line_visited=None,
            story_line_completed=None,
            quest_item=None
    ) -> None:
        super().__init__(name)
        self.story_line = story_line
        self.story_line_visited = story_line_visited
        self.story_line_completed = story_line_completed
        self.quest_item = quest_item

