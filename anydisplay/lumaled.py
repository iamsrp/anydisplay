"""
LUMA LED matrix displays.
"""

from   typing import Tuple
from   .      import Display

import numpy

# ----------------------------------------------------------------------

class MAX7219(Display):
    """
    The MAX7219 LED matrix.

    See::
        https://luma-led-matrix.readthedocs.io/en/latest/
    """
    def __init__(self,
                 width  : int  = 8,
                 height : int  = 8):
        super().__init__()

        from luma.led_matrix.device import max7219
        from luma.core.interface.serial import spi, noop
        from luma.core.render import canvas

        self._canvas = canvas

        self._serial = spi(port=0, device=0, gpio=noop())
        self._device = max7219(self._serial,
                               width            =width,
                               height           =height,
                               rotate           =0,
                               block_orientation=0)

        self._bitmap = numpy.ndarray((width, height), dtype=bool)
        self._bitmap[:] = False


    def get_shape(self) -> Tuple[int,int]:
        return (self._device.width, self._device.height)


    def clear(self):
        self._bitmap[:] = False


    def set(self,
            x: int,
            y: int,
            r: float,
            g: float,
            b: float) -> None:
        # Ensure that they are correctly oriented
        (dx, dy) = self._orient(x, y)

        # Bounds check since the call with throw otherwise
        if 0 <= dx < self._device.width and 0 <= dy < self._device.height:
            # Okay to set. Convert to gray and then a boolean.
            v = (r * 0.299 +
                 g * 0.587 +
                 b * 0.114)
            self._bitmap[dx][dy] = v >= 0.5


    def show(self):
        with self._canvas(self._device) as draw:
            for x in range(self._device.width):
                for y in range(self._device.height):
                    draw.point((x, y), int(self._bitmap[x][y]))
