import random
from utils import (clear_terminal, paragraph, text, ask_user, add_space)
from .items import Weapon, Armour, Potion, Book, Special, Item
from .game_manager import game_manager


class Interaction:
    """
    Handles the interaction between the player and the game elements.
    """

    def __init__(self, player):
        self.player = player

    def equip(self, item, item_type):
        """
        Equips the player with the item.
        """
        if item.name == 'none':
            setattr(self.player, item_type, None)
            return
        if item.received:
            paragraph(f"{item.received}", space=1)
        else:
            msg = (f"You have received "
                   "'{item.name}'." if item_type == 'armour' else f"You "
                   f"have received the '{item.name}'.")
            paragraph(msg, space=1)
        if item.description:
            paragraph(item.description, space=1)
        setattr(self.player, item_type, item)

    def add_new_item(self, item):
        """
        Adds a new item to the player's inventory.
        """
        if isinstance(item, Weapon):
            self.equip(item, 'weapon')

        elif isinstance(item, Armour):
            self.equip(item, 'armour')

        elif isinstance(item, Potion):
            paragraph(f"You have received {item.name}.", space=1)
            if item.description:
                paragraph(item.description, space=1)
            self.player.potions.append(item)

        elif isinstance(item, Book):
            if item.received:
                paragraph(f"{item.received}", space=1)
            else:
                paragraph(f"You have received a book: '{item.name}'.", space=1)
            self.player.inventory.append(item)

        elif isinstance(item, Special):
            if item.received:
                paragraph(f"{item.received}", space=1)
            self.player.inventory.append(item)

        elif isinstance(item, Item):
            if item.received:
                paragraph(f"{item.received}", space=1)
            else:
                paragraph(f"You have received an item: '{item.name}'.",
                          space=1)
            if item.description:
                paragraph(item.description, space=1)
            self.player.inventory.append(item)

    def print_story_line(self, story_line):
        """
        Prints the story line to the terminal.
        """
        for line in story_line:
            space = line['space'] if 'space' in line else 1
            delay = line['delay'] if 'delay' in line else 0.2
            color = line['color'] if 'color' in line else None
            if 'clear' in line:
                clear_terminal()
            elif 'text' in line:
                paragraph(line['text'], space=space, color=color, delay=delay)
            elif 'continue' in line:
                ask_user('continue', space=space)
            elif 'item' in line:
                self.add_new_item(line['item'])
            elif 'gameover' in line:
                game_manager.reset_game()

    def with_area(self, area, visited):
        """
        Handles the interaction with an area.
        """
        add_space()
        if not visited:
            self.print_story_line(area.story_line)
        else:
            self.print_story_line(area.story_line_visited)

    def with_neutral(self, neutral, visited):
        """
        Handles the interaction with a neutral character.
        """
        if not visited:
            self.print_story_line(neutral.story_line)
        elif visited and neutral.quest_item:
            has_quest_item = any(
                item.name == neutral.quest_item.name for item in
                self.player.inventory
            )
            if has_quest_item and neutral.quest_item:
                # Player has the quest item, proceed with the special
                # story_line
                self.print_story_line(neutral.story_line_completed)
            else:
                # Player does not have the quest item or no quest item
                # specified, proceed with the visited story_line
                self.print_story_line(neutral.story_line_visited)
        else:
            self.print_story_line(neutral.story_line_visited)

    def with_enemy(self, enemy, location, visited):
        """
        Handles the interaction with an enemy.
        """
        if not visited:
            self.print_story_line(enemy.story_line)
            text(f"{enemy.name} stats - health: {enemy.health}, "
                 f" attack: {enemy.attack}, "
                 f"defense: {enemy.defense}", space=1)
        else:
            if enemy.health <= 0:
                self.print_story_line(enemy.story_line_defeated)
                return
            if enemy.fought:
                self.print_story_line(enemy.story_line_fought)
                text(
                    f"{enemy.name} stats - health: {enemy.health}, "
                    f"attack: {enemy.attack}, "
                    f"defense: {enemy.defense}", space=1)
            else:
                self.print_story_line(enemy.story_line_visited)
                text(
                    f"{enemy.name} stats - health: {enemy.health}, "
                    f"attack: {enemy.attack}, "
                    f"defense: {enemy.defense}", space=1)

        combat = Combat(self.player, enemy)
        results = combat.to_fight_or_not_to_fight()
        if results == "retreat":
            text("You have retreated from the battle.")
            location.return_to_previous_position()
            return False
        elif results == "won":
            text(f"You have defeated {enemy.name}!", space=1)
            self.print_story_line(enemy.story_line_won_fight)
            return True
        elif results == "lost":
            text(f"You have been defeated by {enemy.name}!", space=1)
            self.print_story_line(enemy.story_line_lost_fight)


class Combat:
    """
    Handles the combat between the player and an enemy.
    """

    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy

    def combat(self):
        """
        Handles the combat between the player and the enemy.
        """
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
        """
        Handles the decision to fight or retreat.
        """
        if ask_user('combat'):
            result = self.combat()
            return result
        else:
            return "retreat"

    def continue_or_flee(self):
        """
        Prompts the player to continue or flee the battle.
        """
        return ask_user('retreat')

    def player_attack(self):
        """
        Handles the player's attack on the enemy.
        """
        player_attack_power = self.calculate_player_attack_power()
        damage = self.calculate_damage(player_attack_power, self.enemy.defense)
        self.enemy.health -= damage
        text(f"You hit the enemy causing {damage} damage.")

    def enemy_attack(self):
        """
        Handles the enemy's attack on the player.
        """
        damage = self.calculate_damage(
            self.enemy.attack, self.calculate_player_defense()
        )
        self.player.health -= damage
        text(f"Enemy hits you causing {damage} damage.")

    def calculate_player_attack_power(self):
        """
        Calculates the player's attack power.
        """
        base_attack = self.player.attack
        weapon_bonus = self.player.weapon.attack if self.player.weapon else 0
        return base_attack + weapon_bonus

    def calculate_player_defense(self):
        """
        Calculates the player's defense.
        """
        base_defense = self.player.defense
        armor_bonus = self.player.armour.defense if self.player.armour else 0
        return base_defense + armor_bonus

    def calculate_damage(self, attack, defense):
        """
        Calculates the damage caused by the attack.
        """
        return max(
            int(random.uniform(0.5 * attack, attack) -
                random.uniform(0, defense)), 1
        )

    def display_combat_status(self):
        """
        Displays the combat status.
        """
        text(f"Player: health:{self.player.health}")
        if self.enemy.health > 0:
            text(f"Enemy: health:{self.enemy.health}", delay=0.3, space=1)
