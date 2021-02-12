import argparse
from cmd import Cmd
from pyfiglet import Figlet

f = Figlet(font="slant")
print(f.renderText("TIC TAC TOE"))

welcome = "Would you like to play a game of TicTacToe"

parser = argparse.ArgumentParser(description=welcome)
parser.add_argument("--players", "-p", required=False, help="The number of players")
parser.add_argument(
    "--games", "-g", required=False, help="The number of consecutive games"
)

parser.parse_args()

args = parser.parse_args()


class TicTacToe(Cmd):
    intro = "Welcome to my games room.\n"
    prompt = "TicTacToe"
    file = None

    def do_new_game(self, args):
        """Start a new game"""
        if len(args) == 0:
            name = "stranger"
        else:
            name = args
        print(f"Hello, {name}")

    def do_quit(self, args):
        """Quits the program."""
        print("Quitting.")
        raise SystemExit


if __name__ == "__main__":
    TicTacToe().cmdloop()
