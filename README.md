# Yolkaris Odyssey - CI Project 3

[Deployed Yolkaris Odyssey Game Link](https://yolkaris-odyssey-1ec6546cf850.herokuapp.com/)

## Deploying the Game to Heroku

## Running the game with Docker

1. Build the container `docker build -t yolkaris-odyssey .`
2. Run the container `docker run -p 3000:8000 yolkaris-odyssey`

## Instalation

## How to play

Yolkaris Odyssey is a text-based adventure game where you explore the vibrant planet of Yolkaris, unravel mysteries, and embark on quests to restore the Grand Clock. Follow these steps to start your adventure:

### Starting the Game
Launch the Game: After installing, run the game using Python in your terminal or command prompt:

```python run.py```

Enter Your Name: You'll be prompted to enter a name for your character. This name will be used throughout your adventure.

### Game Commands

- `map`: Displays the map of your current location, showing areas you can explore.
- `north`: Move to the area north of your current location.
- `south`: Move to the area south of your current location.
- `east`: Move to the area east of your current location.
- `west`: Move to the area west of your current location.
- `stats`: View your character's health, attack, defense, and other vital stats.
- `inventory`: Access the items you've collected on your journey. Here, you can inspect items or use them.
- `potion`: Displays your potion options. Use this command when you need to restore health.
- `search`: Investigate your current location for hidden items or secrets.
- `reset`: Resets the game, allowing you to start over from the main screen.
- `quit`: Exits the game.

## Features

## Issues

### Unresolved Issues

- [Issue 1 - Input execution timing issue during text output](https://github.com/patrickhladun/yolkaris-odyssey/issues/1)
