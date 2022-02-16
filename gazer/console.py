import curses
import time
from gazer import Gazer


def draw_menu(stdscr: curses.window):
    k = 0
    cursor_x = 0
    cursor_y = 0

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()
    stdscr.nodelay(True)
    # curses.delay_output(100)

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # Loop where k is the last character pressed
    while k != ord('q'):
        try:
            # Initialization
            stdscr.clear()
            height, width = stdscr.getmaxyx()

            if k == curses.KEY_DOWN:
                cursor_y = cursor_y + 1
            elif k == curses.KEY_UP:
                cursor_y = cursor_y - 1
            elif k == curses.KEY_RIGHT:
                cursor_x = cursor_x + 1
            elif k == curses.KEY_LEFT:
                cursor_x = cursor_x - 1

            cursor_x = max(0, cursor_x)
            cursor_x = min(width - 1, cursor_x)

            cursor_y = max(0, cursor_y)
            cursor_y = min(height - 1, cursor_y)

            statusbarstr = "Press 'q' to exit | STATUS BAR | Pos: {}, {}".format(cursor_x, cursor_y)

            stdscr.addstr(0, 0, "Requests", curses.color_pair(1))
            stdscr.addstr(2, 0, gazer.request_log_text(), curses.color_pair(1))
            stdscr.addstr(15, 0, gazer.syn_backlog_text(), curses.color_pair(1))

            # Render status bar
            stdscr.attron(curses.color_pair(3))
            stdscr.addstr(height - 1, 0, statusbarstr)
            stdscr.addstr(height - 1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
            stdscr.attroff(curses.color_pair(3))

            stdscr.move(cursor_y, cursor_x)

            # Refresh the screen
            stdscr.refresh()

            # Wait for next input
            k = stdscr.getch()
            time.sleep(1 / 30)
        except:
            # Refresh the screen
            stdscr.refresh()

            # Wait for next input
            k = stdscr.getch()


gazer = Gazer(console_mode=True)
gazer.poll_data_in_bg()

curses.wrapper(draw_menu)
