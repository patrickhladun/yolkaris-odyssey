from colorama import Fore, Style, init
import os
import time
import textwrap

# Initialize Colorama
init(autoreset=True)

# Define custom colors
default_color = Style.BRIGHT + Fore.WHITE  # Default color
color_light_blue = Fore.LIGHTBLUE_EX  # Light blue color
color_player = Fore.LIGHTGREEN_EX  # Light green color
color_neutral = Fore.CYAN
color_error = Style.NORMAL + Fore.RED

color_ask_user = Fore.BLUE + Style.BRIGHT


def text(
        text_line,
        delay=0.1,
        space=0,
        color=default_color
):
    """
    Prints text to the terminal with optional color.
    - text: the text to print
    - delay: the delay between each character
    - space: the number of new lines to print after the text
    - color: the color to apply to the text
    """
    line_space = '\n' * space
    colored_text = (color + text_line if color else text_line) + \
        Fore.RESET + line_space
    print(colored_text)
    time.sleep(delay)


def paragraph(
        long_string,
        space=0,
        delay=0.1,
        color=default_color
):
    """
    Prints a paragraph of text to the terminal with optional color.
    - long_string: the text to wrap and print as a paragraph
    - space: the number of new lines to print after the paragraph
    - color: the color to apply to the text
    """
    wrapped_text = textwrap.fill(long_string, width=74)
    lines = wrapped_text.split('\n')

    text(' ' * 3 + lines[0], color=color)

    for i in range(1, len(lines)):
        line = lines[i]
        if i == len(lines) - 1:
            text(line, color=color)
        else:
            text(line, color=color)

    add_space(space=space, delay=delay)


def add_space(space: int = 1, delay: float = 0.2):
    """
    This prints a new line to the terminal.
    - space: the number of new lines to print (default is 1)
    - delay: the delay between each new line
    """
    if space > 1:
        line_space = '\n' * (space - 1)
        print(line_space)
    elif space == 1:
        print('\n', end='')
    time.sleep(delay)


def clear_terminal():
    """
    Clears terminal.
    """
    os.system('clear')


def ask_user(
        prompt_type: str = None,
        color=color_ask_user,
        prompt: str = None,
        error: str = None,
        space: int = 0,
        numbers=None
):
    """
    Prompts the user for input with an optional color.
    - type: the type of prompt ('continue' or 'confirm')
    - color: the color to apply to the prompt text
    - prompt: the prompt text to display (optional)
    """
    if numbers is None:
        numbers = ['1', '2']
    if prompt_type == "continue":
        prompt = prompt if prompt else "Press enter to continue: "
        line_space = '\n' * (space - 1) if space > 0 else ''
        print(color + prompt + Fore.RESET, end="")
        input().strip().lower()
        if space > 0:
            print(line_space)
    elif prompt_type == "number":
        while True:
            prompt = prompt if prompt else "Select a number: "
            print(color + prompt + Fore.RESET, end="")
            choice = input().strip()
            if choice in numbers:
                return int(choice)
            elif choice == '0':
                return 0
            else:
                error = error if error else ("Invalid choice. Please select a "
                                             "correct number.")
                text(color_error + error + Fore.RESET, space=1)
    elif prompt_type == "game":
        while True:
            prompt = prompt if prompt else "Select a game: "
            print(color + prompt + Fore.RESET, end="")
            choice = input().strip()
            if choice in numbers:
                return int(choice)
            error = error if error else ("Invalid choice. Please select a "
                                         "correct number.")
            text(color_error + error + Fore.RESET, space=1)
    elif prompt_type == "confirm":
        prompt = prompt if prompt else "Select 'yes' or 'no': "
        while True:
            print(color + prompt + " (y/n): " + Fore.RESET, end="")
            choice = input().lower().strip()
            if choice in ['yes', 'y']:
                return True
            elif choice in ['no', 'n']:
                return False
            error = error if error else ("Invalid input. Please enter 'yes' "
                                         "or 'no'.")
            text(color_error + error + Fore.RESET, space=1)
    elif prompt_type == "item":
        prompt = prompt if prompt else ("Do you want to 'use' or 'inspect' "
                                        "the item? (u/i), type '0' to cancel:")
        while True:
            print(color + prompt + Fore.RESET, end="")
            choice = input().lower().strip()
            if choice in ['use', 'u', 'inspect', 'i', '0']:
                return choice
            error = error if error else ("Invalid input. Please enter 'u' to "
                                         "use, 'i' to inspect the item or "
                                         "'0' to cancel.")
            text(color_error + error + Fore.RESET, space=1)
    elif prompt_type == "combat":
        prompt = "Do you want to 'fight' or 'retreat'? "
        while True:
            print(color + prompt + Fore.RESET, end="")
            choice = input().lower().strip()
            if choice == 'fight':
                return True
            elif choice == 'retreat':
                return False
            error = error if error else ("Invalid input. Please enter 'fight' "
                                         "or 'retreat'.")
            text(color_error + error + Fore.RESET, space=1)
    elif prompt_type == "retreat":
        prompt = "To continue press enter or 'retreat': "
        while True:
            print(color + prompt + Fore.RESET, end="")
            choice = input().lower().strip()
            if choice == 'retreat':
                return True
            elif choice == '':
                return False
            error = error if error else ("Invalid input. Please enter "
                                         "'retreat' or enter.")
            text(color_error + error + Fore.RESET, space=1)
    else:
        print(color + (prompt if prompt else "") + Fore.RESET, end="")
        return input().strip().lower()


def loading(content=None, ending: str = None):
    if content is None:
        content = ["Loading", ".", ".", "."]
    for i in content:
        print(default_color + i + Fore.RESET, end='', flush=True)
        time.sleep(0.5)
    print('\n' + default_color + ending + Fore.RESET) if ending else None
    time.sleep(0.5) if ending else None
