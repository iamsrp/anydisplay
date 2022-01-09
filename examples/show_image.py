#!/usr/bin/env python3
"""
Display an image.
"""

from   anydisplay               import Canvas, NullDisplay
from   anydisplay.pimoroni      import UnicornHatHD
from   anydisplay.rgbledmatrix  import RGBLEDMatrix
from   anydisplay.terminal      import Curses
from   PIL                      import Image

import sys
import time

# Args?
if len(sys.argv) != 2:
    print("Usage: %s <image>" % sys.argv[0])
    sys.exit(1)

# What we display on
display = Curses()
#display = NullDisplay(64, 64)
#display = RGBLEDMatrix()
#display = UnicornHatHD()
canvas  = Canvas(display, xwrap=False, ywrap=False)

try:
    # Load in the image
    image = Image.open(sys.argv[1])

    # Display the image
    canvas.set_image(image)
    canvas.show()

    # Wait for a bit
    time.sleep(60)

finally:
    # Tidy and rethrow
    canvas.clear()
    canvas.show()
    canvas.quit()
