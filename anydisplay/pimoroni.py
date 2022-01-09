"""
Pimoroni displays.
"""

from   typing import Tuple
from   .      import Display

import math

# ----------------------------------------------------------------------

class _UnicornHat(Display):
    """
    The base class for the RGB HATs.
    """
    def __init__(self,
                 display,
                 brightness : float):
        super().__init__()
        self._display = display
        self._brightness(min(max(brightness, 0.0), 1.0))


    def get_shape(self) -> Tuple[int,int]:
        return self._display.get_shape()


    def set_orientation(self, orientation: int) -> None:
        super().set_orientation(orientation)
        self._display.rotation(orientation)


    def clear(self):
        self._display.clear()


    def set(self,
            x: int,
            y: int,
            r: float,
            g: float,
            b: float) -> None:
        # Bounds check since the call with throw otherwise
        (w, h) = self._display.get_shape()
        if 0 <= x < w and 0 <= y < h:
            # Okay to set
            self._display.set_pixel(
                x,
                y,
                int(255 * min(max(r, 0.0), 1.0)),
                int(255 * min(max(g, 0.0), 1.0)),
                int(255 * min(max(b, 0.0), 1.0))
            )


    def show(self):
        self._display.show()


    def _brightness(self, brightness : float):
        """
        Set the brightness of the display.
        """
        # This is inconsistently named between the github and pip versions
        if hasattr(self._display, "set_brightness"):
            self._display.set_brightness(brightness)
        elif hasattr(self._display, "brightness"):
            self._display.brightness(brightness)


class UnicornHatHD(_UnicornHat):
    """
    The 16x16 RGB Unicorn HAT HD.
    """
    def __init__(self,
                 brightness : float = 0.5):
        """
        :param brightness: The display brightness value, ``[0.0,1.0]``.
        """
        import unicornhathd
        super().__init__(unicornhathd, brightness)


class UnicornHatMini(_UnicornHat):
    """
    The 17x7 Unicorn HAT mini.
    """
    def __init__(self,
                 brightness : float = 0.5):
        """
        :param brightness: The display brightness value, ``[0.0,1.0]``.
        """
        from unicornhatmini import UnicornHATMini
        super().__init__(UnicornHATMini(), brightness)


class UnicornScrollHatMini(_UnicornHat):
    """
    The 17x7 Unicorn grey-scale SCROLL HAT MINI and HD.
    """
    def __init__(self,
                 brightness : float = 0.5):
        """
        :param brightness: The display brightness value, ``[0.0,1.0]``.
        """
        import scrollphathd
        super().__init__(scrollphathd, brightness)


    def set(self,
            x: int,
            y: int,
            r: float,
            g: float,
            b: float) -> None:
        # Bounds check since the call with throw otherwise
        (w, h) = self._display.get_shape()
        if 0 <= x < w and 0 <= y < h:
            # Okay to set. We need to turn the colours into a brightness since
            # the HAT is grey-scale only.
            v = math.sqrt(r**2 + g**2 + b**2)

            # And set
            self._display.pixel(x, y, min(max(v, 0.0), 1.0))

        
