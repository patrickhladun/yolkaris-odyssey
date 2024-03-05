class Item:
    """
    Initializes an item in the game.
    """

    def __init__(
            self,
            name: str,
            description: str = None,
            received: str = None
    ) -> None:
        self.name = name
        self.description = description
        self.received = received


class Weapon(Item):
    """
    Initializes a weapon in the game.
    """

    def __init__(
            self,
            name: str,
            attack: int,
            description: str = None,
            received: str = None) -> None:
        super().__init__(name, description, received)
        self.attack = attack


class Armour(Item):
    """
    Initializes an armour in the game.
    """

    def __init__(
            self,
            name: str,
            defense: int,
            description: str = None,
            received: str = None) -> None:
        super().__init__(name, description, received)
        self.defense = defense


class Potion(Item):
    """
    Initializes a potion in the game.
    """

    def __init__(
            self,
            name: str,
            health: int) -> None:
        super().__init__(name)
        self.health = health


class Book(Item):
    """
    Initializes a book in the game.
    """

    def __init__(
            self,
            name: str,
            description: str,
            story_line: list,
            received: str = None) -> None:
        super().__init__(name, description, received)
        self.story_line = story_line


class Spaceship(Item):
    """
    Initializes a spaceship in the game.
    """

    def __init__(self, name: str, description: str) -> None:
        super().__init__(name, description)


class Special(Item):
    """
    Initializes a special item in the game.
    """

    def __init__(self, name: str, description: str = None,
                 story_line: list = None, received: str = None) -> None:
        super().__init__(name, description, received)
        self.story_line = story_line
