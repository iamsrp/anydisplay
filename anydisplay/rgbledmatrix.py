"""
LED matrix displays.
"""

from   typing import Tuple
from   .      import Display

# ----------------------------------------------------------------------

class RGBLEDMatrix(Display):
    """
    A RGB LED matrix, driven by the Pi RGB LED Matrix software.

    Some options are needed to make things work okay with a Pi4.

    See::
        https://github.com/hzeller/rpi-rgb-led-matrix
    """
    def __init__(self,
                 rows          : int  = 32,
                 columns       : int  = 32,
                 chain_length  : int  = 1,
                 gpio_slowdown : int  = 2,
                 hw_pulsing    : bool = False):
        super().__init__()

        from rgbmatrix import RGBMatrix, RGBMatrixOptions
        options = RGBMatrixOptions()
        options.rows                     = int(rows)
        options.cols                     = int(columns)
        options.chain_length             = int(chain_length)
        options.gpio_slowdown            = int(gpio_slowdown)
        options.disable_hardware_pulsing = not hw_pulsing
        self._matrix = RGBMatrix(options=options)
        self._canvas = self._matrix.CreateFrameCanvas()


    def get_shape(self) -> Tuple[int,int]:
        return (self._matrix.width, self._matrix.height)


    def clear(self):
        self._canvas.Clear()


    def set(self,
            x: int,
            y: int,
            r: float,
            g: float,
            b: float) -> None:
        # Ensure that they are correctly oriented
        (dx, dy) = self._orient(x, y)

        # Bounds check since the call with throw otherwise
        if 0 <= dx < self._matrix.width and 0 <= dy < self._matrix.height:
            # Okay to set
            self._canvas.SetPixel(
                dx,
                dy,
                int(255 * min(max(r, 0.0), 1.0)),
                int(255 * min(max(g, 0.0), 1.0)),
                int(255 * min(max(b, 0.0), 1.0))
            )


    def show(self):
        self._canvas = self._matrix.SwapOnVSync(self._canvas)
