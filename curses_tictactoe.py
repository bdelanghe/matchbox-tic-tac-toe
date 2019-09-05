import curses
import time
import math
# import numpy as np
from pyfiglet import Figlet
from collections import namedtuple
from typing import NamedTuple

f = Figlet(font='slant')
Square = namedtuple('Square', ['y', 'x'])

settings = {
    'board_lines': u'\u2588'
}

player_scores = {
    1: 0,
    2: 0
}
# class Player:
#     pass
#
# class Board:
#     pass
#
# class Move:
#
# class Game:
#     def is_win_move(a, y, x, dim=3):
#         if np.sum(a[y]) == dim:
#             return True
#         if np.sum(a, axis=0)[x] == dim:
#             return True
#         if x == y:
#             if sum(np.diagonal(a)) == dim:
#                 return True
#         if x + y == dim - 2:
#             if sum(np.diag(np.fliplr(a))) == dim:
#                 return True
#         return False
#
#     def new_player_matrix(dim=3):
#         return np.zeros((dim, dim), dtype=int)

games = 0


def title_screen(stdscr: curses.initscr) -> None:
    # Set properties
    curses.curs_set(0)
    stdscr.nodelay(True)

    # Get key input
    k = stdscr.getch()

    # Get window params
    win_h, win_w = stdscr.getmaxyx()

    def wipe_text(text: str) -> int:
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
        title = f.renderText('TIC TAC TOE')
        sub_title = 'produced by: robert delanghe studio'
        any_key = 'press any key to continue'

        y = wipe_text(title)

        stdscr.addstr(y, int((win_w - len(sub_title)) / 2), sub_title)
        stdscr.refresh()

        time.sleep(1)

        stdscr.addstr(win_h - 1, win_w - len(any_key) - 2, any_key, curses.A_BLINK + curses.A_DIM)

        stdscr.refresh()

    load_title()

    while k == -1:
        k = stdscr.getch()


def game(stdscr: curses.initscr) -> None:
    # clear terminal
    stdscr.clear()
    stdscr.refresh()

    # Set curses preferences
    curses.curs_set(0)

    # Get window size
    win_y, win_x = stdscr.getmaxyx()

    # Game settings
    n_by = 3

    def get_square_size() -> NamedTuple:

        if win_y < win_x / 2:
            short = win_y
        else:
            short = win_x / 2

        scale = 2 / 3
        sqr_y = int((short * scale) / n_by)
        sqr_x = sqr_y * 2
        size = Square(sqr_y, sqr_x)
        return size

    # function for testing
    def make_board(sqr: Square) -> str:
        fill = u"\u2588"
        # fill = '#'
        output = ''

        for row in range(1, (sqr.y * n_by) + n_by):
            line = ''
            for col in range(1, (sqr.y * n_by) + n_by):
                y_pos = int(row / (sqr.y + 1))
                x_pos = int(col / (sqr.y + 1))
                grid_pos = str(x_pos + (y_pos * n_by))[-1]
                if row % (sqr.y + 1) == 0:
                    line += fill * 2
                elif col % (sqr.y + 1) == 0:
                    line += fill * 2
                else:
                    line += grid_pos * 2
            output += line + '\n'

        return output

    def get_cross(sqr: Square, invert=False):
        cross = ''
        fill = '?'
        for row in range(sqr.y):
            for col in range(sqr.x):
                if col == row * 2 or col == (sqr.x - 1) - (row * 2):
                    if invert:
                        cross += ' '
                    else:
                        cross += fill
                else:
                    if invert:
                        cross += fill
                    else:
                        cross += ' '
        return cross

    # function to create a circle
    # Thanks to Anant Agarwal
    def get_circle(sqr: Square, invert=False):
        circle = ''
        fill = '@'
        radius = sqr.y / 2 - .5
        for c in range(sqr.y):
            for j in range(sqr.y):
                dist = math.sqrt((c - radius) * (c - radius) +
                                 (j - radius) * (j - radius)) + 1
                if radius - 0.5 < dist < radius + 0.5:
                    if invert:
                        circle += ' ' * 2
                    else:
                        circle += fill * 2
                else:
                    if invert:
                        circle += fill * 2
                    else:
                        circle += ' ' * 2
        return circle

    def draw_board():
        board = make_board(get_square_size())
        lines = board.split("\n")
        board_y = int((win_y - len(lines)) / 2)
        square_dict = {}
        for line in lines:
            board_x = int((win_x - len(lines[0])) / 2)
            for col in line:
                if col not in square_dict and col.isdigit():
                    square_dict[col] = []
                if col.isdigit():
                    square_dict[col].append((board_y, board_x))
                    stdscr.addstr(board_y, board_x, ' ')
                else:
                    stdscr.addstr(board_y, board_x, col, curses.A_DIM)
                board_x += 1
            board_y += 1
            stdscr.refresh()
        stdscr.refresh()
        return square_dict

    square = get_square_size()
    squares = draw_board()
    last = ''
    turn = 0
    players = ['x', 'o']
    player_squares = {
        'x': {
            'blink': get_cross(square, True),
            'select': get_cross(square)
        },
        'o': {
            'blink': get_circle(square, True),
            'select': get_circle(square)
        }
    }
    keymap = {
        'q': '0',
        'w': '1',
        'e': '2',
        'a': '3',
        's': '4',
        'd': '5',
        'z': '6',
        'x': '7',
        'c': '8'
    }
    endgame = False
    while True and len(keymap) > 0:
        event = stdscr.getch()
        try:
            char = chr(event)
        except ValueError:
            char = 0
        # y, x = stdscr.getyx()
        # if event == curses.KEY_UP:
        #     stdscr.move(y - 1, x)
        # if event == curses.KEY_DOWN:
        #     stdscr.move(y + 1, x)
        # if event == curses.KEY_LEFT:
        #     stdscr.move(y, x - 1)
        # if event == curses.KEY_RIGHT:
        #     stdscr.move(y, x + 1)
        play_square = player_squares[players[turn % 2]]
        if char in keymap:
            sq = keymap[char]
            if last != '':
                for y, x in squares[keymap[last]]:
                    stdscr.addch(y, x, ' ', curses.A_NORMAL)
            for i, cord in enumerate(squares[sq]):
                y, x = cord
                stdscr.addch(y, x, play_square['blink'][i], curses.A_BLINK)
                last = char
        if event == ord(' ') and last != '':
            for i, cord in enumerate(squares[keymap[last]]):
                y, x = cord
                stdscr.addch(y, x, play_square['select'][i], curses.A_NORMAL)
            keymap.pop(last, None)
            last = ''
            turn += 1

        stdscr.refresh()
        if event == ord('`'):
            endgame = True
            break

    if endgame is False:
        curses.wrapper(game)


def main():
    curses.wrapper(title_screen)
    curses.wrapper(game)


if __name__ == "__main__":
    main()
