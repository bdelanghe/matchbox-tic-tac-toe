"""
TIC TAC TOE GAME

Play a simple game inside python's cmd module. The board is drawn to match the curses module layout:
```
  0 1 2 x
0| | | |
1| | | |
2| | | |
y
```
Play multiple session and keep track of score. Future versions will have curses graphics and an AI.
Currently considering created a MENACE machine in which all learning is done from beads inside matchboxes.
"""

from __future__ import annotations

from cmd import Cmd
from collections import namedtuple
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from pyfiglet import Figlet

fig = Figlet(font='slant')
Square = namedtuple('Square', ['y', 'x'])


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
        """feel like rage quitting? or try 'new_game 10'"""
        n_by = 3
        if line is not None:
            try:
                number = int(line)
                if 0 < number < 101:
                    n_by = number
            except ValueError:
                pass
        self.session.new_game(n_by)
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
        line = line
        if line == '':
            self._do_last = True
        elif line == 'help':
            self._do_last = False
            self.do_help('')
        elif line == 'stop':
            self._do_last = False
            # nonlocal li
        else:
            if 'move ' in line:
                line = line.replace('move ', '')
            self._do_last = True
            try:
                y, x = [int(s) for s in line.split()]
                sqr = Square(y=y, x=x)
                self.message_handler(self.session.current_game.square_input(sqr))
            except ValueError:
                if self._do_last is False:
                    print('\nAlert: Format must be: "move y x"')
                else:
                    print('\nAlert: Format must be: "y x" or type "stop"')

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
        print(fig.renderText('TIC TAC TOE'))
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
        print(fig.renderText('thanks for playing\n'))

    def _print_board(self) -> None:
        """print the current board to console"""
        print()
        for l in self.session.current_game.board:
            line = ''
            for e in l:
                line += '|' + e
            print(line + '|')
        print('\n')

    def _print_scores(self) -> None:
        """display the current player scores to console"""
        scores = []
        for player in self.players.values():
            scores.append(f'{player.name}: {player.wins} wins')
        scores.append(f'Ties: {self.players[0].ties}')
        print(str.join('   |   ', scores) + '\n')

    @staticmethod
    def _print_cats() -> None:
        """let players know the cat always wins"""
        print(fig.renderText("Cat's Game"))

    @staticmethod
    def _print_square_not_free():
        """Can't sit here"""
        print('\nAlert: Square is not open')

    @staticmethod
    def _print_winner(name: str) -> None:
        """congrats are due"""
        print(fig.renderText(f'{name} Wins!!!!'))

    def message_handler(self, message: tuple):
        """unpack messages from game"""
        if message is not None:
            if message[0] == 'Not Open':
                self._print_square_not_free()
            elif message[0] == 'Winner':
                self._print_board()
                self._print_winner(message[1])
                self._print_scores()
                self.session.new_game()
            elif message[0] == 'Cats':
                self._print_board()
                self._print_cats()
                self._print_scores()
                self.session.new_game()
            elif message[0] == 'Out of range':
                print(f'\nAlert: Range is 0 => {message[1]}')


class Player:
    """player object to hold moves and score"""

    def __init__(self, number: int) -> None:
        self.number = number
        self.name = f'Player {self.number + 1}'
        self.wins = 0
        self.ties = 0


class Session:
    """sessions help keep track score"""

    def new_game(self, n_by: int = 3) -> None:
        """create a new game"""
        if self.current_game is not None:
            self.play_count += 1
            del self.current_game
        self.current_game = Game(self, n_by)

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

    marks = {0: 'x', 1: 'o'}

    def square_input(self, sqr: Square) -> Optional[Tuple]:
        """input from square object"""
        message = self._is_open(sqr)
        if message[0] == "Open":
            return self._play_move(sqr)
        return message

    def __init__(self, session, n_by=3) -> None:
        self.n_by: int = n_by
        self.session: Optional[Session] = session
        self.players: Dict[int, Player] = self.session.players
        self.board: List[List[str]] = [[' ' for _ in range(self.n_by)] for _ in range(self.n_by)]
        self.moves: Dict[int, Moves] = {0: Moves(self.n_by), 1: Moves(self.n_by)}
        self.turns: int = 0

    @property
    def current_player(self) -> Player:
        """the player who's turn it is"""
        start = self.session.first_move
        return self.session.players[(start + self.turns) % 2]

    @property
    def open_squares(self) -> np.matrix:
        """the inverse of all squares played"""
        moves = self.moves[0].matrix + self.moves[1].matrix
        return 1 - moves

    @property
    def _waiting_player(self) -> Player:
        """the player who's turn it is"""
        start = self.session.first_move
        return self.session.players[(start + self.turns - 1) % 2]

    def _add_to_board(self, sqr: Square) -> None:
        """keeping track of moves"""
        if self.current_player.number == self.session.first_move:
            mark = self.marks[0]
        else:
            mark = self.marks[1]
        self.board[sqr.y][sqr.x] = mark

    def _cats(self) -> Tuple[str, list]:
        """better luck next time"""
        for player in self.players.values():
            player.ties += 1
        return 'Cats', self.board

    def _end(self) -> None:
        self.session.new_game()
        """called if winner or tie"""

    def _is_open(self, sqr: Square) -> Tuple[str, Any]:
        """this is not the square you are looking for"""
        last_index = len(self.open_squares) - 1
        if sqr.y > last_index or sqr.x > last_index or sqr.y < 0 or sqr.x < 0:
            return 'Out of range', last_index
        elif self.open_squares[sqr.y][sqr.x] == 0:
            return 'Not Open', sqr
        return 'Open', sqr

    def _is_last(self) -> bool:
        """are there any spots left to play"""
        for line in self.open_squares:
            for e in line:
                if e == 1:
                    return False
        return True

    def _new_winner(self) -> Tuple[str, str]:
        """increment play score"""
        self.current_player.wins += 1
        return 'Winner', self.current_player.name

    def _play_move(self, sqr: Square) -> None:
        """commit a move and return if winner"""
        self._add_to_board(sqr)
        message = self.moves[self.current_player.number].move(sqr)
        if message is not None and message[0] == "Winner":
            message = self._new_winner()
        elif self._is_last() is True:
            message = self._cats()
        self.turns += 1
        return message


class Moves:
    """store all the moves a player has made"""

    def move(self, sqr: Square) -> Optional[Tuple[str, Square]]:
        """add a move to np matrix return win"""
        self.matrix[sqr.y][sqr.x] = 1
        win = self._is_win_move(sqr)
        if win is True:
            return 'Winner', sqr

    def reset_moves(self):
        """reset after end of game"""
        self.matrix: np.ndarray = np.zeros((self.n_by, self.n_by), dtype=int)

    def __init__(self, n_by):
        self.n_by: int = n_by
        self.matrix: np.ndarray = np.zeros((self.n_by, self.n_by), dtype=int)

    def __repr__(self) -> str:
        return str(self.matrix)

    def _is_win_move(self, sqr: Square) -> bool:
        """check if the last move was the winning move"""
        # todo return which line contributed to the win
        #  maybe make a win tuple?

        if np.sum(self.matrix[sqr.y]) == self.n_by:
            return True
        if sum([l[sqr.x] for l in self.matrix]) == self.n_by:
            return True
        if sqr.x == sqr.y and sum(np.diagonal(self.matrix)) == self.n_by:
            return True
        if sqr.x == (self.n_by - 1) - sqr.y and sum(np.diag(np.fliplr(self.matrix))) == self.n_by:
            return True
        return False


def main() -> None:
    """want to play a game of tic tac toe?"""
    CmdMode().cmdloop()


if __name__ == "__main__":
    main()
