"""TIC TAC TOE GAME"""

import cmd
import curses
import math
import time
from collections import namedtuple
from typing import List, Dict, Optional

import numpy as np
from pyfiglet import Figlet

f: Figlet = Figlet(font='slant')

Size = namedtuple('Size', ['y', 'x'])
Square = namedtuple('Square', ['y', 'x'])
CursesCords = namedtuple('Cords', ['y', 'x'])


# todo make keymap namedtuple?

class CmdMode(cmd.Cmd):
    """cmd wrapper for interactions"""
    intro = f.renderText('TIC TAC TOE')
    prompt = '(play)'
    file = None

    def __init__(self):
        super().__init__()
        self.session = Session
        self.player = 0

    def precmd(self, line):
        """Hook method executed just before the command line is
        interpreted, but after the input prompt is generated and issued.

        """
        return 'pie'

    def do_bye(self, arg):
        """all good things come to an end"""
        print('thanks for playing')
        self.close()
        return True

    def close(self):
        """all good things come to an end"""
        if self.file:
            self.file.close()
            self.file = None


class Window:
    """Curses Window extension"""

    # todo create a check for seeing if the window has been re-sized
    # todo add a func buffer for all objects that are currently displayed
    # todo function to re-draw all objects in buffer on re-size
    def __init__(self, func: object) -> None:
        self.stdscr: curses.initscr() = curses.wrapper(func)
        # self.buffer = None
        # self.mode = curses.def_prog_mode()
        # self.sub_wins = []

    @property
    def size(self) -> Size:
        """tuple of the curses window size"""
        y, x = self.stdscr.getmaxyx()
        return Size(y=y, x=x)

    @property
    def short_side(self) -> int:
        """find the short side of the current window"""

        # char ratio is 2x:1y
        if self.size.y < self.size.x / 2:
            return self.size.y
        else:
            return self.size.x / 2

    def _find_start_center(self, strings: List[str]) -> CursesCords:
        """the upper left corner for drawing a list of strings centered"""
        begin_y = int((self.size.y - len(strings)) / 2)
        begin_x = int((self.size.x - len(strings[0])) / 2)
        return CursesCords(y=begin_y, x=begin_x)

    def draw_centered(self, strings: List[str]) -> None:
        """given a list of strings of equal length draw them centered"""
        begin_y, begin_x = self._find_start_center(strings)
        for i, line in enumerate(strings):
            self.stdscr.addstr(begin_y + i, begin_x, line)
        self.stdscr.refresh()

    def clear_cords(self, cords: List[CursesCords]) -> None:
        """clear all characters at cords"""
        for cord in cords:
            y, x = cord
            self.stdscr.addch(y, x, ' ', curses.A_NORMAL)

    def draw_select(self, cords: List[CursesCords], string: str) -> None:
        """draw given text blinking"""
        for i, cord in enumerate(cords):
            y, x = cord
            self.stdscr.addch(y, x, string[i], curses.A_BLINK)

    def draw_commit(self, cords: List[CursesCords], string: str) -> None:
        """draw given text not blinking"""
        for i, cord in enumerate(cords):
            y, x = cord
            self.stdscr.addch(y, x, string[i], curses.A_NORMAL)

    def get_input(self) -> str:
        """get input from terminal window"""
        try:
            return chr(self.stdscr.getch())
        except ValueError:
            return ''

    @staticmethod
    def delay(ms: int) -> None:
        """delay output"""
        curses.delay_output(ms)

    @staticmethod
    def reset() -> None:
        """set window back to where is started"""
        curses.reset_prog_mode()

    @staticmethod
    def flash() -> None:
        """flash the terminal screen"""
        curses.flash()


class Player:
    """player object to hold score"""

    def __init__(self, number: int) -> None:
        self.moves: Moves = Moves()
        self.number = number
        self.keymap: Dict[str, Square] = KeymapLib.from_player(self).keys
        self.score = 0

    def get_square(self, char: str) -> Square:
        """given player input look for corresponding square"""
        if char in self.keymap:
            return self.keymap[char]

    def move(self, sqr: Square) -> bool:
        """add move to player moves"""
        return self.moves.move(sqr)


class Session:
    """sessions help keep track score"""

    def __init__(self) -> None:
        self.players: Dict[int, Player] = {0: Player(0), 1: Player(1)}
        self.current_game: Optional[Game] = None
        self.play_count: int = 0
        self.quit: bool = False

    @property
    def first_move(self) -> int:
        """which player gets to go first"""
        return self.play_count % 2

    def _new_game(self) -> None:
        """create a new game"""
        self.current_game = Game(self)

    def _print_scores(self) -> None:
        """display the current player scores to console"""
        scores = ''
        for player in self.players.values():
            scores += f'Player {player.number + 1}: {player.score}      '
        print(scores + '\n')

    @staticmethod
    def _print_exit_message() -> None:
        """saying goodbye is always hard"""
        print('Thanks for playing!!')

    def play(self):
        """keep playing games until quit"""
        while self.quit is False:
            self._print_scores()
            self._new_game()
            self.current_game.play()
        self._print_exit_message()


class Game:
    """simple class for playing in cmd"""
    n_by = 3
    marks = {0: 'x', 1: 'o'}

    def __init__(self, session) -> None:
        self.session: Optional[Session] = session
        self.players: Dict[int, Player] = self.session.players
        self.end: bool = False
        self.turns: int = 0
        self.previous_move: Optional[Square] = None
        # self.winner: Optional[Player] = None
        # self.selected: Optional[Square] = None

    @property
    def _current_player(self) -> Player:
        """the player who's turn it is"""
        start = self.session.first_move
        return self.session.players[(start + self.turns) % 2]

    @property
    def _waiting_player(self) -> Player:
        """the player who's turn it is"""
        start = self.session.first_move
        return self.session.players[(start + self.turns - 1) % 2]

    @property
    def current_board(self) -> List[List[str]]:
        """add the view of both players"""
        board = [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]
        for n, player in self.players.items():
            for y, row in enumerate(player.moves.matrix):
                for x, e in enumerate(row):
                    if e == 1:
                        board[y][x] = self.marks[n]
        return board

    @property
    def open_squares(self) -> np.matrix:
        """the inverse of all squares played"""
        moves = self.players[0].moves.matrix + self.players[1].moves.matrix
        return 1 - moves

    def _print_board(self) -> None:
        """print the current board to console"""
        for l in self.current_board:
            line = ''
            for e in l:
                line += '|' + e
            print(line + '|')

    def _end_cleanup(self) -> None:
        """clean house on game end"""
        for player in self.players.values():
            player.moves.reset_moves()

    @staticmethod
    def _print_winner(player) -> None:
        """congrats are due"""
        print(f'Player {player + 1} Wins!!!!')

    def _new_winner(self) -> Player:
        """increment play score"""
        winner = self._current_player
        winner.score += 1
        player = winner.number
        self._print_winner(player)
        self.end = True

        return winner

    def _print_keymap(self) -> None:
        """what are the current keys"""
        print(f'Not a valid key Player {self._current_player.number + 1} keys are:')
        print(self._current_player.keymap)

    def _get_square(self, char: str) -> Optional[Square]:
        """look to see if the char is a key"""
        if char in self._current_player.keymap:
            return self._current_player.keymap[char]
        else:
            self._print_keymap()

    @staticmethod
    def _print_square_not_free():
        print('Square is not open')

    def _is_open(self, sqr: Square) -> bool:
        free = self.open_squares[sqr.y][sqr.x]
        if free == 0:
            self._print_square_not_free()
        return free

    def _input(self, char: str) -> bool:
        """look up square if in player keymap"""
        sqr = self._get_square(char)
        valid = False
        if sqr is not None:
            if self._is_open(sqr):
                self.selected = sqr
                valid = True
        return valid

    def console_input(self) -> None:
        """keep asking for input"""
        move = False
        while move is False:
            move = self._input(input())

    def play_move(self, sqr: Square) -> None:
        """commit a move"""
        win = self._current_player.move(sqr)
        if win is True:
            self._new_winner()
        else:
            self.previous_move = sqr
            self.turns += 1

    def play(self) -> None:
        """start a play session"""
        while self.end is False:
            self._print_board()
            self.console_input()
            self.play_move(self.selected)
        self._end_cleanup()


class KeymapLib:
    """mapping characters to squares"""

    def __init__(self, keys=None) -> None:
        self.keys = keys

    @classmethod
    def from_player(cls, player: Player):
        """each player has their own keys"""
        keys_dict = {}
        chars = None
        if player.number == 0:
            chars = ['q', 'w', 'e', 'a', 's', 'd', 'z', 'x', 'c']
        if player.number == 1:
            chars = ['u', 'i', 'o', 'j', 'k', 'l', 'm', ',', '.']
        for i, c in enumerate(chars):
            y = int(i / 3)
            x = i % 3
            keys_dict[c] = Square(y=y, x=x)
        return cls(keys_dict)

    # @property
    # def arrow_keys(self) -> Dict[str, tuple]:
    #     """movement with arrows"""
    #     # todo add an input method so a player can move with keys
    #     return {curses.KEY_UP: (-1, 0), curses.KEY_DOWN: (1, 0), curses.KEY_LEFT: (0, -1), curses.KEY_RIGHT: (0, 1)}


class Moves:
    """store all the moves a player has made"""
    n_by = 3

    def __init__(self):
        self.matrix: np.ndarray = np.zeros((self.n_by, self.n_by), dtype=int)

    def __repr__(self) -> str:
        return str(self.matrix)

    def reset_moves(self):
        """reset after end of game"""
        self.matrix: np.ndarray = np.zeros((self.n_by, self.n_by), dtype=int)

    def move(self, sqr: Square) -> bool:
        """add a move to np matrix return win"""
        self.matrix[sqr.y][sqr.x] = 1
        return self._is_win_move(sqr)

    def _is_win_move(self, sqr: Square) -> bool:
        """check if the last move was the winning move"""
        # todo return which squares contributed to the win
        # todo maybe make a win tuple?

        if np.sum(self.matrix[sqr.y]) == self.n_by:
            return True
        elif sum([l[sqr.x] for l in self.matrix]) == self.n_by:
            return True
        elif sqr.x == sqr.y:
            if sum(np.diagonal(self.matrix)) == self.n_by:
                return True
        elif sqr.x + sqr.y == self.n_by - 2:
            if sum(np.diag(np.fliplr(self.matrix))) == self.n_by:
                return True
        return False


class CursesSession(Session):
    """a class extension to include curses"""

    def __init__(self) -> None:
        super().__init__()
        self.quit_char = '`'
        self.window = Window(self.play())

    def play(self) -> None:
        """while loop for playing in curses"""
        curses.curs_set(0)

        while self.quit is False:
            self._new_game()
            self.current_game.play()


class AiPlayer(Player):
    """smart player extension"""

    # todo add AI class
    def __init__(self, number) -> None:
        super().__init__(number)


class CursesGame(Game):
    """extended Game class for Curses"""

    def __init__(self, session: CursesSession) -> None:
        super().__init__(session)
        self.session = session
        self.board: BoardLib = BoardLib(self.session.window)

    def play(self) -> None:
        """display loop for curses"""
        # fixme after simplifying play
        # self.stdscr.clear()
        # self.stdscr.refresh()
        #
        # self.draw_board()
        #
        # while self.end is False:
        #     # todo make one call
        #     move = self.input()
        #
        #     stdscr.refresh()

    def _draw_board(self) -> None:
        """draw board in curses window"""
        str_list = self.board.board_grid
        self.session.window.draw_centered(str_list)

    def _curses_input(self) -> None:
        """overwrite game func to allow for quiting"""
        char: str = self.session.window.get_input()
        if char == self.session.quit_char:
            self.end = True
            self.session.quit = True
        else:
            self._input(char)


class BoardLib:
    """extended library object for curses"""

    def __init__(self, window: Window = None):
        self._window = window
        self.n_by: int = 3
        self.scale: float = 2 / 3
        self.line_fill: str = u'\u2588'
        self.cross_fill: str = '?'
        self.nought_fill: str = '@'
        self.square_map: dict = {}

    @property
    def _window(self) -> Window:
        """Current curses window for obj"""
        return self._window

    @_window.setter
    def _window(self, value: Optional[Window]) -> None:
        """allow for no window object for debugging"""
        if value is not None:
            self._window = value

    @property
    def _square_size(self) -> Size:
        """find the pixel box size for each square"""
        sqr_y = int((self._window.short_side * self.scale) / self.n_by)
        sqr_x = sqr_y * 2
        return Size(y=sqr_y, x=sqr_x)

    @property
    def board_grid(self) -> List[str]:
        """creating a string for printing the TicTacToe grid"""
        # todo: rewrite to just give cords of lines
        lines = []
        size = self._square_size
        self.square_map = {}

        for row in range(1, (size.y * self.n_by) + self.n_by):
            line = ''
            for col in range(1, (size.y * self.n_by) + self.n_by):
                y = int(row / self.n_by)
                x = int(col / self.n_by)
                sqr_cord = Square(y=y, x=x)
                curse_cord = CursesCords(y=row, x=col)
                if row % (size.y + 1) == 0:
                    line += self.line_fill * 2
                elif col % (size.y + 1) == 0:
                    line += self.line_fill * 2
                else:
                    if sqr_cord not in self.square_map:
                        self.square_map[sqr_cord] = []
                    self.square_map[sqr_cord].append(curse_cord)
            lines.append(line)

        return lines

    @staticmethod
    def invert(string) -> str:
        """invert the characters of a square"""
        fill = max([c for c in string])
        return str([' ' if fill else fill for _ in string])

    @property
    def cross(self) -> str:
        """create a string for a cross"""
        string = ''
        sqr = self._square_size

        for row in range(sqr.y):
            for col in range(sqr.x):
                if col == row * 2 or col == (sqr.x - 1) - (row * 2):
                    string += self.cross_fill
                else:
                    string += ' '
        return string

    @property
    def nought(self) -> str:
        """create a string for a nought"""
        string = ''
        sqr = self._square_size

        # Needed to add a boarder to get it to look right
        border = 1 / 2
        radius = sqr.y / 2 - border
        for row in range(sqr.y):
            for col in range(sqr.y):
                dist = math.sqrt((row - radius) * (row - radius) +
                                 (col - radius) * (col - radius)) + 1
                if radius - border < dist < radius + border:
                    string += self.nought_fill * 2
                else:

                    string += ' ' * 2
        return string


def title_screen(stdscr: curses.initscr) -> None:
    """a fun title screen"""
    # todo turn this into an object?
    # Set properties
    curses.curs_set(0)
    stdscr.nodelay(True)

    # Get key input
    k = stdscr.getch()

    # Get window params
    win_h, win_w = stdscr.getmaxyx()

    def wipe_text(text: str) -> int:
        """load multi-line text from left to right"""
        lines = text.split("\n")

        # Get dimensions for text
        x_len = len(lines[0])
        y_len = len(lines)

        # Find center for text
        x = int((win_w - x_len) / 2)
        y = y_start = int((win_h - y_len) / 2)

        for i in range(x_len):
            y = y_start
            for line in lines[:-1]:
                stdscr.addstr(y, x, line[i])
                y += 1
            stdscr.refresh()
            time.sleep(.05)
            x += 1
        return y

    def load_title() -> None:
        """add title to window"""
        title = f.renderText('TIC TAC TOE')
        sub_title = 'produced by: robert delanghe studio'
        any_key = 'press any key to continue'

        y: int = wipe_text(title)

        stdscr.addstr(y, int((win_w - len(sub_title)) / 2), sub_title)
        stdscr.refresh()

        time.sleep(1)

        stdscr.addstr(win_h - 1, win_w - len(any_key) - 2, any_key, curses.A_BLINK + curses.A_DIM)

        stdscr.refresh()

    load_title()

    while k == -1:
        k = stdscr.getch()


def play() -> None:
    """lets play tic tac toe"""
    sess = Session()
    sess.play()


def main() -> None:
    """want to play a game of tic tac toe?"""
    # curses.wrapper(title_screen)
    play()
    # CmdMode().cmdloop()


if __name__ == "__main__":
    main()
