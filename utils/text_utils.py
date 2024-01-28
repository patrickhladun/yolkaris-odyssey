from colorama import Fore, Style, init
import os
import time
import textwrap

# Initialize Colorama
init(autoreset=True)

# Define custom colors
default_color = Style.BRIGHT + Fore.WHITE  # Default color
color_light_gray = Fore.LIGHTBLACK_EX  # Light gray color
color_light_blue = Fore.LIGHTBLUE_EX  # Light blue color
color_player = Style.DIM + Fore.LIGHTGREEN_EX  # Light green color
color_neutral = Style.DIM + Fore.CYAN
color_error = Style.NORMAL + Fore.RED

color_ask_user = Fore.BLUE + Style.BRIGHT


def text(
    text,
    delay=0.2,
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
    colored_text = (color + text if color else text) + Fore.RESET + line_space
    print(colored_text)
    time.sleep(delay)


def paragraph(
    long_string,
    space=1,
    color=default_color
):
    """
    Prints a paragraph of text to the terminal with optional color.
    - long_string: the text to wrap and print as a paragraph
    - space: the number of new lines to print after the paragraph
    - color: the color to apply to the text
    """
    wrapped_text = textwrap.fill(long_string, width=75)
    lines = wrapped_text.split('\n')

    for i, line in enumerate(lines):
        if i == len(lines) - 1:
            text(line, space=space, color=color)
        else:
            text(line, color=color)


def add_space(space: int = 0, delay: float = 0.2):
    """
    This prints a new line to the terminal.
    - space: the number of new lines to print
    - delay: the delay between each new line
    """
    line_space = '\n' * space
    print(' ' + line_space)
    time.sleep(delay)


def clear_terminal():
    """ 
    Clears terminal.
    """
    os.system('clear')


def ask_user(
        type: str = None,
        color=color_ask_user,
        prompt: str = None,
        space: int = 0,
):
    """
    Prompts the user for input with an optional color.
    - type: the type of prompt ('continue' or 'confirm')
    - color: the color to apply to the prompt text
    - prompt: the prompt text to display (optional)
    """
    if type == "continue":
        prompt = prompt if prompt else "Press enter to continue: "
        line_space = '\n' * (space - 1) if space > 0 else ''
        print(color + prompt + Fore.RESET, end="")
        input().strip().lower()
        if space > 0:
            print(line_space)
    elif type == "confirm":
        prompt = prompt if prompt else "Select 'yes' or 'no': "
        while True:
            print(color + prompt + " (yes/no): " + Fore.RESET, end="")
            choice = input().lower().strip()
            if choice in ['yes', 'no']:
                return True
            print("Invalid input. Please enter 'yes' or 'no'.")
    elif type == "combat":
        prompt = "Do you want to 'fight' or 'retreat'? "
        while True:
            print(color + prompt + Fore.RESET, end="")
            choice = input().lower().strip()
            if choice == 'fight':
                return True
            elif choice == 'retreat':
                return False
            print("Invalid input. Please enter 'fight' or 'retreat'.")
    elif type == "retreat":
        prompt = "To continue press enter or 'retreat': "
        while True:
            print(color + prompt + Fore.RESET, end="")
            choice = input().lower().strip()
            if choice == 'retreat':
                return True
            elif choice == '':
                return False
            print("Invalid input. Please enter 'retreat' or enter.")
    else:
        print(color + (prompt if prompt else "") + Fore.RESET, end="")
        return input().strip().lower()
