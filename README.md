# 🎲 Matchbox TicTacToe 🎲

## 📖 Table of Contents
- [About](#about)
- [Key Features](#key-features)
- [Installation](#installation)
- [How to Play](#how-to-play)
- [Code Structure](#code-structure)
- [Contributing](#contributing)

## 🧐 About

Welcome to Matchbox TicTacToe, a command-line interface (CLI) based game that adds a smart twist to the classic TicTacToe! The AI opponent in this game is trained using the MENACE (Matchbox Educable Naughts and Crosses Engine) algorithm, a pioneering machine learning algorithm invented by Donald Michie in the 1960s. Learn more about MENACE [here](https://en.wikipedia.org/wiki/Matchbox_Educable_Noughts_and_Crosses_Engine).

## 🌟 Key Features
- **Interactive CLI**: Intuitive and user-friendly command-line interface.
- **MENACE Inspired AI**: The AI opponent gradually learns and improves its game strategy based on the MENACE algorithm.
- **Easy to Install and Play**: Straightforward installation and simple game mechanics for all players.

## 🔧 Installation
To install Matchbox TicTacToe, follow the steps below:

1. Clone this repository.
2. Navigate to the project's directory in your terminal.

## 🎮 How to Play
To play Matchbox TicTacToe:

1. Run the game script in your terminal.
2. The game will guide you through the process.

## 🏗️ Code Structure

The main game logic is divided into two Python files:

1. `tictactoe_cli.py`:
This script handles the CLI using the argparse and cmd libraries, providing an interactive command-line interface for the game.

2. `tictactoe_game.py`:
This script takes care of the actual game logic, the visual rendering using the curses library, and the MENACE inspired AI logic.

The AI opponent's performance is based on the MENACE algorithm and "learns" over time. The more games it plays, the more challenging it will become.

## 🤝 Contributing
Contributions to improve this project are always welcome. Please feel free to create an issue or pull request.

Note: As the AI learns over time, the challenge level increases with each game. Good luck, and may the best player win! 🏆
