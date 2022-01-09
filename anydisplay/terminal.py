"""
A display using a terminal.
"""

from .      import Display
from typing import Tuple

# ----------------------------------------------------------------------

class Curses(Display):
    """
    Use a terminal to display with Curses.
    """
    def __init__(self):
        super().__init__()

        import curses

        self._curses  = curses
        self._display = curses.initscr()
        curses.start_color()

        # Assume this for now. If it grumbles about only having 8 colours then
        # try setting TERM=xterm-256color in your environment.
        if curses.COLORS < 256:
            # Be kind, rewind^H^H^H^Hset. Do this before we throw so that we
            # don't leave the terminal in a bad state.
            self._curses.endwin()
            raise ValueError(
                "Bad number of colours, need 256: %d" % curses.COLORS
            )

        # Set up curses how we like it
        self._display = curses.initscr()
        self._curses.noecho()
        self._curses.cbreak()
        self._curses.curs_set(False)
        self._display.keypad(True)

        # 8 bit colour! We only have 256 colours to play with so we use a
        # (3,3,2) RGB colour range.
        for i in range(1, 256):
            r = (i >> 5) & 7
            g = (i >> 2) & 7
            b = (i >> 0) & 3
            curses.init_color(i,
                              int(1000.0 * r / 7),
                              int(1000.0 * g / 7),
                              int(1000.0 * b / 3))
            # Remember that 0 is reserved, so start at 1
            curses.init_pair(i, curses.COLOR_WHITE, i)

        # Remember this
        self._max_r = 7
        self._max_g = 7
        self._max_b = 3

        # And remember this
        (max_y, max_x) = self._display.getmaxyx()
        self._max_x = max_x
        self._max_y = max_y


    def get_shape(self) -> Tuple[int,int]:
        return (self._max_x, self._max_y)


    def set_orientation(self, orientation: int) -> None:
        # Not supported -- yet
        pass


    def clear(self) -> None:
        self._display.clear()


    def quit(self) -> None:
        # Tidy up curses and return the terminal to normal use
        self._curses.nocbreak()
        self._display.keypad(False)
        self._curses.echo()
        self._curses.curs_set(True)
        self._curses.endwin()


    def set(self,
            x: int,
            y: int,
            r: float,
            g: float,
            b: float) -> None:
        # Ensure that they are correctly oriented
        (dx, dy) = self._orient(x, y)

        # Bounds check so we only draw if it's on the display
        if 0 <= dx < self._max_x and 0 <= dy < self._max_y:
            # Determine the colour-pair to use. This is just the 332 RGB value,
            # but 1-indexed.
            pair = (((int(round(self._max_r * r)) << 5) |
                     (int(round(self._max_g * g)) << 2) |
                     (int(round(self._max_b * b))     )) & 255)
            if pair >= self._curses.COLORS:
                pair = self._curses.COLORS-1
            try:
                self._display.addstr(dy, dx, ' ', self._curses.color_pair(pair))
            except:
                # Swallow errors for now
                pass


    def show(self):
        self._display.refresh()


class Debug(Display):
    """
    Output what we are called with to the terminal.
    """
    def get_shape(self) -> Tuple[int,int]:
        # Whatever...
        return (32, 32)


    def clear(self) -> None:
        print("/" + "-" * 80)


    def quit(self) -> None:
        pass


    def set(self,
            x: int,
            y: int,
            r: float,
            g: float,
            b: float) -> None:
        (dx, dy) = self._orient(x, y)
        print(f"| x={x} y={y} dx={dx} dy={dy} r={r} g={g} b={b}")


    def show(self):
        print("\\" + "-" * 80)
