import curses
import time
import math
from pyfiglet import Figlet

f = Figlet(font='slant')


def title_screen(stdscr: object) -> None:

    # clear terminal
    stdscr.nodelay(True)
    stdscr.clear()
    stdscr.refresh()
    curses.curs_set(0)
    height, width = stdscr.getmaxyx()

    title = f.renderText('TIC TAC TOE')
    sub_title = 'produced by: robert delanghe studio'
    any_key = 'press any key to continue'

    def key_break(func):
        k = 0
        while k == 0 or k == curses.KEY_RESIZE:
            output = func()
            k = stdscr.getch()
        return output

    def wipe_text(text):
        lines = text.split("\n")
        x = int((width - len(lines[0])) / 2)
        for i in range(len(lines[0])):
            y = int((height - len(lines)) / 2)
            for line in lines[:-1]:
                stdscr.addstr(y, x, line[i])
                y += 1
            stdscr.refresh()
            time.sleep(.1)

            x += 1
        return y

    def load_title():
        y = wipe_text(title)

        stdscr.addstr(y, int((width - len(sub_title)) / 2), sub_title)
        stdscr.refresh()

        time.sleep(2)

        stdscr.attron(curses.A_BLINK)
        stdscr.attron(curses.A_DIM)
        stdscr.addstr(height - 1, width - len(any_key) - 2, any_key)
        stdscr.attroff(curses.A_BLINK)
        stdscr.attroff(curses.A_DIM)

        stdscr.refresh()

    key_break(load_title)


def game(stdscr):
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
    def get_board():
        fill = u"\u2588"
        # fill = '#'
        num = 3
        size = square_size()
        output = ''

        for y in range(1, (size * num) + num):
            line = ''
            for x in range(1, (size * num) + num):
                y_pos = int(y / (size + 1))
                x_pos = int(x / (size + 1))
                grid_pos = str(x_pos + (y_pos * num))[-1]
                if y % (size + 1) == 0:
                    line += fill * 2
                elif x % (size + 1) == 0:
                    line += fill * 2
                else:
                    line += grid_pos * 2
            output += line + '\n'

        return output

    board = get_board()

    def get_cross():
        cross = ''
        height = square_size()
        width = height * 2
        for li in range(height):
            for c in range(width):
                if c == li * 2 or c == (width - 1) - (li * 2):
                    cross += ' '
                else:
                    cross += '&'
            if li != height - 1:
                cross += '\n'
        return cross

    # function to create a circle
    # Thanks to Anant Agarwal
    def get_circle(height):
        circle = ''
        radius = (height / 2)
        for i in range(height + 1):
            for j in range(height + 1):
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
        y = int((height - len(lines)) / 2)
        sqrs = {}
        for line in lines:
            x = int((width - len(lines[0])) / 2)
            for c in line:
                if c not in sqrs and c.isdigit():
                    sqrs[c] = []
                if c.isdigit():
                    sqrs[c].append((y, x))
                    stdscr.addstr(y, x, c)
                else:
                    stdscr.addstr(y, x, c)
                x += 1
            y += 1
            stdscr.refresh()
        stdscr.refresh()
        return sqrs

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
        if event == ord("q"): break


def main():
    curses.wrapper(title_screen)
    curses.wrapper(game)


if __name__== "__main__":
    main()
