import os
import time
import textwrap

def text(text, delay=0.2, space=0):
    """
    This prints text to the terminal.
    - text: the text to print
    - delay: the delay between each character
    - space: the number of new lines to print after the text
    """
    line_space = '\n' * space
    print(text + line_space)
    time.sleep(delay)


def paragraph(long_string, space=1):
    wrapped_text = textwrap.fill(long_string, width=75)
    lines = wrapped_text.split('\n')

    for i, line in enumerate(lines):
        if i == len(lines) - 1:
            text(line, space=1)
        else:
            text(line)


def space(space=1, delay=0.2):
    """
    This prints a new line to the terminal.
    - space: the number of new lines to print
    - delay: the delay between each new line
    """
    print('\n')
    time.sleep(delay)

def clear_terminal():
    """ 
    Clears terminal.
    """
    os.system('clear')
