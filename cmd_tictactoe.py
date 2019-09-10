"""
TIC TAC TOE GAME

Play a simple game inside python's cmd module. The board is drawn to match the curses module layout:

  0 1 2 x
0| | | |
1| | | |
2| | | |
y

Play multiple session and keep track of score. Future versions will have curses graphics and an AI.
Currently considering created a MENACE machine in which all learning is done from beads inside matchboxes.
"""

from __future__ import annotations

from cmd import Cmd
from collections import namedtuple
from typing import List, Dict, Optional

import numpy as np
from pyfiglet import Figlet

f: Figlet = Figlet(font='slant')

Size = namedtuple('Size', ['y', 'x'])
Square = namedtuple('Square', ['y', 'x'])
CursesCords = namedtuple('Cords', ['y', 'x'])


class CmdMode(Cmd):
    """cmd wrapper for interactions"""
    doc_leader = """
    
Play a simple game inside python's cmd module. The board coordinates are:

              0 1 2 x
            0| | | |
            1| | | |
            2| | | |
            y
            
    """
    doc_header = 'everything you can do (more info: type ?<cmd>)'
    ruler = '~'

    # noinspection PyUnusedLocal
    def do_bye(self, line):
        """all good things come to an end"""
        self._end = True
        self._print_bye()
        return True

    # noinspection PyUnusedLocal
    def do_new_game(self, line):
        """feel like rage quitting?"""
        self.session.new_game()
        self._print_board()

    def do_name(self, line):
        """give the current player a name"""
        if line == '':
            print('enter a name')
            self._do_last = True
        else:
            self.session.current_game.current_player.name = line
            self._do_last = False

    def do_move(self, line):
        """make a move, format must be: 'move y x''"""
        if line == '':
            self._do_last = True
        elif line == 'help':
            self._do_last = False
            self.do_help('')
        elif line == 'stop':
            self._do_last = False
        else:
            self._do_last = True
            try:
                y, x = [int(s) for s in line.split()]
                sqr = Square(y=y, x=x)
                self.session.current_game.square_input(sqr)
            except ValueError:
                if self._do_last is False:
                    print('format must be: "move y x"')
                else:
                    print('format must be: "y x" or type "stop"')

    # noinspection PyUnusedLocal
    def do_score(self, line):
        """I wonder who's winning"""
        self._print_scores()

    def __init__(self):
        super().__init__()
        self.session = Session()
        self.players = self.session.players
        self._end = False
        self._do_last = False

    @property
    def prompt(self):
        """add the current player to prompt"""
        p = str(self.session.current_game.current_player.name)
        if self._do_last is True and self.last_simple is not None:
            p += f': {self.last_simple}'
        return f'({p})'

    @property
    def last_simple(self):
        """there is no try only do"""
        if self._do_last is True:
            trim = self.lastcmd.split()[0]
            try:
                getattr(self, 'do_' + trim)
                return trim
            except AttributeError:
                pass

    def emptyline(self):
        """rewriting so it's more fun"""
        print("Why so quiet?")

    def default(self, line):
        """making errors more fun"""
        print("I'm sorry I'm a bit confused. Maybe ask for 'help'?")

    def preloop(self):
        """Hook method executed once when the cmdloop() method is called."""
        print(f.renderText('TIC TAC TOE'))
        self.session.new_game()
        self._print_scores()
        self._print_board()

    def postloop(self):
        """After it's over"""
        pass

    def precmd(self, line):
        """Hook method executed just before the command line is
        interpreted, but after the input prompt is generated and issued.
        """
        if self._do_last is True and self.last_simple is not None:
            return f'{self.last_simple} {line}'
        else:
            return line

    def postcmd(self, stop, line):
        """Hook method executed just after a command dispatch is finished."""
        if self._end is False and self.last_simple == 'move':
            self._print_board()
        return stop

    @staticmethod
    def _print_bye() -> None:
        """"print bye"""
        print(f.renderText('thanks for playing\n'))

    def _print_board(self) -> None:
        """print the current board to console"""
        print()
        for l in self.session.current_game.current_board:
            line = ''
            for e in l:
                line += '|' + e
            print(line + '|')
        print('\n')

    def _print_scores(self) -> None:
        """display the current player scores to console"""
        scores = []
        for player in self.players.values():
            scores.append(f'Player {player.name}: {player.wins} wins')
        scores.append(f'Ties: {self.players[0].ties}')
        print(str.join('   |   ', scores) + '\n')


class Player:
    """player object to hold moves and score"""

    def move(self, sqr: Square) -> bool:
        """add move to player moves"""
        return self.moves.move(sqr)

    def __init__(self, number: int) -> None:
        self.moves: Moves = Moves()
        self.number = number
        self.name = f'Player {self.number + 1}'
        self.wins = 0
        self.ties = 0


class Session:
    """sessions help keep track score"""

    def new_game(self) -> None:
        """create a new game"""
        if self.current_game is not None:
            self.play_count += 1
            del self.current_game
        self.current_game = Game(self)

    def __init__(self) -> None:
        self.players: Dict[int, Player] = {0: Player(0), 1: Player(1)}
        self.current_game: Optional[Game] = None
        self.play_count: int = 0

    @property
    def first_move(self) -> int:
        """which player gets to go first"""
        return self.play_count % 2


class Game:
    """simple class for playing in cmd"""

    n_by = 3
    marks = {0: 'x', 1: 'o'}

    def square_input(self, sqr: Square) -> Optional[bool]:
        """input from square object"""
        if self._is_open(sqr):
            return self._play_move(sqr)

    def __init__(self, session) -> None:
        self.session: Optional[Session] = session
        self.players: Dict[int, Player] = self.session.players
        self.turns: int = 0

    def __del__(self) -> None:
        """clean house on game end"""
        for player in self.players.values():
            player.moves.reset_moves()

    @property
    def current_board(self) -> List[List[str]]:
        """add the view of both players"""
        board = [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]
        for _, player in self.players.items():
            for y, row in enumerate(player.moves.matrix):
                for x, e in enumerate(row):
                    if e == 1:
                        board[y][x] = self.marks[player.number != self.session.first_move]
            return board

    @property
    def current_player(self) -> Player:
        """the player who's turn it is"""
        start = self.session.first_move
        return self.session.players[(start + self.turns) % 2]

    @property
    def open_squares(self) -> np.matrix:
        """the inverse of all squares played"""
        moves = self.players[0].moves.matrix + self.players[1].moves.matrix
        return 1 - moves

    @property
    def _waiting_player(self) -> Player:
        """the player who's turn it is"""
        start = self.session.first_move
        return self.session.players[(start + self.turns - 1) % 2]

    def _cats(self) -> None:
        """better luck next time"""
        for player in self.players.values():
            player.ties += 1
        self._print_cats()
        self._end()

    def _end(self) -> None:
        self.session.new_game()
        """called if winner or tie"""

    def _is_open(self, sqr: Square) -> bool:
        """this is not the square you are looking for"""
        free = self.open_squares[sqr.y][sqr.x]
        if free == 0:
            self._print_square_not_free()
        return free

    def _is_last(self) -> bool:
        """are there any spots left to play"""
        for line in self.open_squares:
            for e in line:
                if e == 1:
                    return False
        return True

    def _new_winner(self) -> None:
        """increment play score"""
        self.current_player.wins += 1
        self._print_winner(self.current_player)
        self._end()

    def _play_move(self, sqr: Square) -> None:
        """commit a move and return if winner"""
        win = self.current_player.move(sqr)
        if win is True:
            self._new_winner()
        if self._is_last() is True:
            self._cats()
        self.turns += 1

    # todo remove printing from class
    @staticmethod
    def _print_cats() -> None:
        """let players know the cat always wins"""
        print(f.renderText("Cat's Game"))

    @staticmethod
    def _print_square_not_free():
        """Can't sit here"""
        print('Square is not open')

    @staticmethod
    def _print_winner(player: Player) -> None:
        """congrats are due"""
        print(f.renderText(f'{player.name} Wins!!!!'))


class Moves:
    """store all the moves a player has made"""
    n_by = 3

    def move(self, sqr: Square) -> bool:
        """add a move to np matrix return win"""
        self.matrix[sqr.y][sqr.x] = 1
        return self._is_win_move(sqr)

    def reset_moves(self):
        """reset after end of game"""
        self.matrix: np.ndarray = np.zeros((self.n_by, self.n_by), dtype=int)

    def __init__(self):
        self.matrix: np.ndarray = np.zeros((self.n_by, self.n_by), dtype=int)

    def __repr__(self) -> str:
        return str(self.matrix)

    def _is_win_move(self, sqr: Square) -> bool:
        """check if the last move was the winning move"""
        # todo return which line contributed to the win
        #  maybe make a win tuple?

        if np.sum(self.matrix[sqr.y]) == self.n_by:
            return True
        elif sum([l[sqr.x] for l in self.matrix]) == self.n_by:
            return True
        elif sqr.x == sqr.y:
            if sum(np.diagonal(self.matrix)) == self.n_by:
                return True
        else:
            if sum(np.diag(np.fliplr(self.matrix))) == self.n_by:
                return True
        return False


def main() -> None:
    """want to play a game of tic tac toe?"""
    CmdMode().cmdloop()


if __name__ == "__main__":
    main()
