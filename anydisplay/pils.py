"""
Displays which use Python's PIL to drive them.
"""

from   PIL    import Image
from   typing import Tuple
from   .      import Display

# ----------------------------------------------------------------------

class _PIL(Display):
    """
    The base class for the PIL-based displays.
    """
    def __init__(self,
                 width  : int,
                 height : int):
        """
        :param width:  The display width.
        :param height: The display height.
        """
        super().__init__()

        self._image = Image.new('RGB',
                                (int(width), int(height)),
                                color=(0,0,0))
        self._clear = (b'\x00' *
                       self._image.width *
                       self._image.height *
                       3)


    def get_shape(self) -> Tuple[int,int]:
        return self._image.size


    def clear(self):
        self._image.frombytes(self._clear)


    def set(self,
            x: int,
            y: int,
            r: float,
            g: float,
            b: float) -> None:
        # Ensure that they are correctly oriented
        (dx, dy) = self._orient(x, y)

        # Bounds check since the call with throw otherwise
        if 0 <= dx < self._image.width and 0 <= dy < self._image.height:
            # Okay to set
            self._image.putpixel(
                (dx, dy),
                (int(255 * min(max(r, 0.0), 1.0)),
                 int(255 * min(max(g, 0.0), 1.0)),
                 int(255 * min(max(b, 0.0), 1.0)))
            )


class ST7789TFT(_PIL):
    """
    The display for a Pimoroni ST7789 TFT display.

    See::
        pip3 install st7789
        https://github.com/pimoroni/st7789-python
    """
    def __init__(self,
                 width       : int = 240,
                 height      : int = 240,
                 offset_left : int =   0,
                 offset_top  : int =   0):
        super().__init__(width, height)

        import ST7789

        # Use our orientation handling since non-square displays don't handle it
        # natively
        self.set_orientation(90)

        self._display = ST7789.ST7789(
            width       =width,
            height      =height,
            port        =0,
            cs          =ST7789.BG_SPI_CS_FRONT,
            dc          =9,
            backlight   =19,
            rotation    =0, # Handled locally
            spi_speed_hz=80 * 1000 * 1000,
            offset_left =offset_left,
            offset_top  =offset_top
        )
        self._display.begin()


    def show(self) -> None:
        self._display.display(self._image)


    def quit(self) -> None:
        super().quit()
        self._display.reset()


class _MiniPiTFT(_PIL):
    """
    Display class for the Adafruit miniPiTFT displays.

    See:
        https://learn.adafruit.com/adafruit-mini-pitft-135x240-color-tft-add-on-for-raspberry-pi    
    """
    def __init__(self,
                 width    : int,
                 height   : int,
                 x_offset : int,
                 y_offset : int,
                 rotation : int):
        super().__init__(width, height)

        self._rotation = rotation

        # Imports for this board
        from   adafruit_rgb_display import st7789
        import digitalio
        import board
        
        # Create the display
        self._display = st7789.ST7789(
            board.SPI(),
            cs      =digitalio.DigitalInOut(board.CE0),
            dc      =digitalio.DigitalInOut(board.D25),
            rst     =None,
            baudrate=64000000, # Max is 24mhz
            width   =height,   # Reoriented when we...
            height  =width,    #  ...call image() below
            x_offset=x_offset,
            y_offset=y_offset,
        )


    def show(self) -> None:
        self._display.image(self._image, self._rotation)


    def quit(self) -> None:
        super().quit()
        self._display.reset()


class MiniPiTFT114(_MiniPiTFT):
    """
    Display class for the Adafruit miniPiTFT 1.14" display.

    See:
        https://learn.adafruit.com/adafruit-mini-pitft-135x240-color-tft-add-on-for-raspberry-pi    
    """
    def __init__(self):
        super().__init__(240, 135, 53, 40, 90)


class MiniPiTFT13(_MiniPiTFT):
    """
    Display class for the Adafruit miniPiTFT 1.3" display.

    See:
        https://learn.adafruit.com/adafruit-mini-pitft-135x240-color-tft-add-on-for-raspberry-pi    
    """
    def __init__(self):
        super().__init__(240, 240, 0, 80, 180)


class I2CPiOLED(_PIL):
    """
    The display for the monochrome Adafruit i2c Pi OLED display.

    See::
        https://learn.adafruit.com/adafruit-pioled-128x32-mini-oled-for-raspberry-pi/usage
        pip3 install adafruit-circuitpython-ssd1306
    """
    def __init__(self,
                 dither : bool = True):
        """
        :param dither: Whether to dither when converting to monochrome. Without
                       it you get a very flat transform. With it you get noise
                       "artifacts" from frame to frame.
        """
        super().__init__(128, 32)

        from   board             import SCL, SDA
        import adafruit_ssd1306
        import busio

        i2c = busio.I2C(SCL, SDA)
        self._display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

        if dither:
            self._dither = Image.FLOYDSTEINBERG
        else:
            self._dither = Image.NONE


    def show(self) -> None:
        mono = self._image.convert('1', dither=self._dither)
        self._display.image(mono)
        self._display.show()


    def quit(self) -> None:
        super().quit()
        self._display.reset()
