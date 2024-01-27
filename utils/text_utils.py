from colorama import Fore, Style, init
import os
import time
import textwrap

# Initialize Colorama
init(autoreset=True)

# Define custom colors
color_light_gray = Fore.LIGHTBLACK_EX  # Light gray color
color_light_blue = Fore.LIGHTBLUE_EX  # Light blue color


def text(text, delay=0.2, space=0, color=Fore.RESET):
    """
    Prints text to the terminal with optional color.
    - text: the text to print
    - delay: the delay between each character
    - space: the number of new lines to print after the text
    - color: the color to apply to the text
    """
    line_space = '\n' * space
    print(color + text + Fore.RESET + line_space)
    time.sleep(delay)


def paragraph(long_string, space=1, color=Fore.RESET):
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
            text(line, space=1, color=color)
        else:
            text(line, color=color)


def space(space: int = 0, delay: float = 0.2):
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


def ask_user(type: str, color=Fore.RESET, prompt: str = None):
    """
    Prompts the user for input with an optional color.
    - type: the type of prompt ('continue' or 'confirm')
    - color: the color to apply to the prompt text
    - prompt: the prompt text to display (optional)
    """
    if type == "continue":
        prompt = prompt if prompt else "Press enter to continue: "
        print(color + prompt + Fore.RESET, end="")
        input()
    elif type == "confirm":
        prompt = prompt if prompt else "Select 'yes' or 'no': "
        while True:
            print(color + prompt + " (yes/no): " + Fore.RESET, end="")
            choice = input().lower()
            if choice in ['yes', 'no']:
                return True
            print("Invalid input. Please enter 'yes' or 'no'.")
    elif type == "combat":
        prompt = "Do you want to 'fight' or 'retreat'? "
        while True:
            print(color + prompt + Fore.RESET, end="")
            choice = input().lower()
            if choice == 'fight':
                return 'fight'
            elif choice == 'retreat':
                return 'retreat'
            print("Invalid input. Please enter 'fight' or 'retreat'.")
    elif type == "retreat":
        prompt = "To continue press enter or 'retreat': "
        while True:
            print(color + prompt + Fore.RESET, end="")
            choice = input().lower()
            if choice == 'retreat':
                return 'retreat'
            print("Invalid input. Please enter 'retreat' or enter.")
