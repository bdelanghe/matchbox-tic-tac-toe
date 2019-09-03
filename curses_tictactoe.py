import curses
import time
import math
from pyfiglet import Figlet

f = Figlet(font='slant')


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
    curses.curs_set(0)
    height, width = stdscr.getmaxyx()

    def square_size():
        scale = 2 / 3
        num = 3

        if height < width / 2:
            short = height
        else:
            short = width / 2

        return int((short * scale) / num)

    # function for testing
    def get_board() -> str:
        fill = u"\u2588"
        # fill = '#'
        num = 3
        size = square_size()
        output = ''

        for row in range(1, (size * num) + num):
            line = ''
            for col in range(1, (size * num) + num):
                y_pos = int(row / (size + 1))
                x_pos = int(col / (size + 1))
                grid_pos = str(x_pos + (y_pos * num))[-1]
                if row % (size + 1) == 0:
                    line += fill * 2
                elif col % (size + 1) == 0:
                    line += fill * 2
                else:
                    line += grid_pos * 2
            output += line + '\n'

        return output

    board = get_board()

    def get_cross():
        cross = ''
        sqr_h = square_size()
        sqr_w = sqr_h * 2
        for row in range(sqr_h):
            for col in range(sqr_w):
                if col == row * 2 or col == (sqr_w - 1) - (row * 2):
                    cross += ' '
                else:
                    cross += '&'
            if row != sqr_h - 1:
                cross += '\n'
        return cross

    # function to create a circle
    # Thanks to Anant Agarwal
    def get_circle():
        circle = ''
        sqr_h = square_size()
        radius = (sqr_h / 2)
        for i in range(sqr_h + 1):
            for j in range(sqr_h + 1):
                dist = math.sqrt((i - radius) * (i - radius) +
                                 (j - radius) * (j - radius)) + 1
                if radius - 0.5 < dist < radius + 0.5:
                    circle += "  "
                else:
                    circle += "@@"
        return circle

    def draw_board():

        stdscr.clear()
        lines = board.split("\n")
        board_y = int((height - len(lines)) / 2)
        square_dict = {}
        for line in lines:
            board_x = int((width - len(lines[0])) / 2)
            for col in line:
                if col not in square_dict and col.isdigit():
                    square_dict[col] = []
                if col.isdigit():
                    square_dict[col].append((board_y, board_x))
                    stdscr.addstr(board_y, board_x, col)
                else:
                    stdscr.addstr(board_y, board_x, col)
                board_x += 1
            board_y += 1
            stdscr.refresh()
        stdscr.refresh()
        return square_dict

    squares = draw_board()
    last = ''
    turn = 0
    players = ['x', 'o']

    while True and len(squares) > 0:
        event = stdscr.getch()
        curses.curs_set(2)
        y, x = stdscr.getyx()
        if event == curses.KEY_UP:
            stdscr.move(y - 1, x)
        if event == curses.KEY_DOWN:
            stdscr.move(y + 1, x)
        if event == curses.KEY_LEFT:
            stdscr.move(y, x - 1)
        if event == curses.KEY_RIGHT:
            stdscr.move(y, x + 1)
        if chr(event) in squares:
            c = chr(event)
            if last != '':
                for y, x in squares[last]:
                    stdscr.addch(y, x, ' ', curses.A_NORMAL)
            for y, x in squares[c]:
                stdscr.addch(y, x, ' ', curses.A_BLINK)
                last = c
        if event == ord('p') and last != '':
            for y, x in squares[last]:
                stdscr.addch(y, x, players[turn % 2], curses.A_REVERSE)
            squares.pop(last, None)
            last = ''
            turn += 1

        stdscr.refresh()
        if event == ord("q"):
            break


def main():
    curses.wrapper(title_screen)
    # curses.wrapper(game)


if __name__ == "__main__":
    main()
