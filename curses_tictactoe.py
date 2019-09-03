import curses
import time
import math
from pyfiglet import Figlet

from typing import *

f = Figlet(font='slant')


def key_break(func, window):
    k = 0
    while k == 0 or k == curses.KEY_RESIZE:
        output = func()
        k = window.getch()
    return output


def wipe_text(window, text, win_size):
    height, width = win_size
    lines = text.split("\n")
    x = int((width - len(lines[0])) / 2)
    for i in range(len(lines[0])):
        y = int((height - len(lines)) / 2)
        for line in lines[:-1]:
            window.addstr(y, x, line[i])
            y += 1
        window.refresh()
        time.sleep(.1)

        x += 1
    return y

# real function here
# def get_board(win_size):
#     height, width = win_size
#     fill = '#'
#     if height < width / 2:
#         short = height
#     else:
#         short = width / 2
#     scale = 2 / 3
#     y_space = int((short * scale) / 3) + 2
#     x_space = y_space * 2
#     output = ''
#     for y in range(y_space * 3):
#         for x in range(x_space * 3):
#             if (x % x_space == 0 or y % y_space == 0) and y != 0 and x != 0:
#                 output += fill
#             else:
#                 output += ' '
#         output += '\n'
#     return output


# function for testing
def get_board(win_size):
    height, width = win_size
    fill = u"\u2588"
    # fill = '#'
    if height < width / 2:
        short = height
    else:
        short = width / 2
    scale = 2 / 3
    num = 3
    square_size = int((short * scale) / num)
    output = ''

    for y in range(1, (square_size * num) + num):
        line = ''
        for x in range(1, (square_size * num) + num):
            y_pos = int(y / (square_size + 1))
            x_pos = int(x / (square_size + 1))
            grid_pos = str(x_pos + (y_pos * num))[-1]
            if y % (square_size + 1) == 0:
                line += fill * 2
            elif x % (square_size + 1) == 0:
                line += fill * 2
            else:
                line += grid_pos * 2
        output += line + '\n'

    return output


def title_screen(window):

    # clear terminal
    window.clear()
    window.refresh()
    curses.curs_set(0)
    win_size = height, width = window.getmaxyx()

    title = f.renderText('TIC TAC TOE')
    sub_title = 'produced by: robert delanghe studio'
    any_key = 'press any key to continue'

    # add resizing wrapper to prompt redrawing if screen is re-sized

    def load_title():
        y = wipe_text(window, title, win_size)

        window.addstr(y, int((width - len(sub_title)) / 2), sub_title)
        window.refresh()

        time.sleep(2)

        window.attron(curses.A_BLINK)
        window.attron(curses.A_DIM)
        window.addstr(height - 1, width - len(any_key) - 2, any_key)
        window.attroff(curses.A_BLINK)
        window.attroff(curses.A_DIM)

        window.refresh()

    key_break(load_title, window)


# # function to create a circle
# # Thanks to Anant Agarwal:
# def get_circle(height):
#     circle = ''
#     radius = (height / 2)
#     for i in range(height + 1):
#         for j in range(height + 1):
#             dist = math.sqrt((i - radius) * (i - radius) +
#                              (j - radius) * (j - radius)) + 1
#             if radius - 0.5 < dist < radius + 0.5:
#                 circle += "  "
#             else:
#                 circle += "@@"
#     return circle

def get_cross(height):
    cross = ''
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


def game(window):
    # clear terminal
    window.clear()
    window.refresh()
    curses.curs_set(0)
    win_size = window.getmaxyx()
    board = get_board(win_size)

    def draw_board():

        window.clear()
        height, width = win_size
        lines = board.split("\n")
        y = int((height - len(lines)) / 2)
        squares = {}
        for line in lines:
            x = int((width - len(lines[0])) / 2)
            for c in line:
                if c not in squares and c.isdigit():
                    squares[c] = []
                if c.isdigit():
                    squares[c].append((y, x))
                    window.addstr(y, x, c)
                else:
                    window.addstr(y, x, c)
                x += 1
            y += 1
            window.refresh()
        window.refresh()
        return squares


    squares = draw_board()
    last = ''
    turn = 0
    players = ['x','o']


    while True and len(squares) > 0:
        event = window.getch()
        curses.curs_set(2)
        y, x = window.getyx()
        if event == curses.KEY_UP:
            window.move(y - 1, x)
        if event == curses.KEY_DOWN:
            window.move(y + 1, x)
        if event == curses.KEY_LEFT:
            window.move(y, x - 1)
        if event == curses.KEY_RIGHT:
            window.move(y, x + 1)
        if chr(event) in squares:
            c = chr(event)
            if last != '':
                for y, x in squares[last]:
                    window.addch(y, x, ' ', curses.A_NORMAL)
            for y, x in squares[c]:
                window.addch(y, x, ' ', curses.A_BLINK)
                last = c
        if event == ord('p') and last != '':
            for y, x in squares[last]:
                window.addch(y, x, players[turn % 2], curses.A_REVERSE)
            squares.pop(last, None)
            last = ''
            turn += 1

        window.refresh()
        if event == ord("q"): break


def main():
    # curses.wrapper(title_screen)
    curses.wrapper(game)


if __name__== "__main__":
    main()
