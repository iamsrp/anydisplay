#!/usr/bin/env python3
"""
Simple smoketests for the AnyDisplay code.
"""

import math
import pytest

def test_null():
    from anydisplay import Canvas, NullDisplay

    # Create a display which goes nowhere
    display = NullDisplay(64, 64)
    canvas  = Canvas(display)

    # Drive the mechanics of it
    for x in range(display.width):
        for y in range(display.height):
            r = x / display.width
            g = y / display.height
            b = (math.sqrt(            x ** 2 +              y ** 2) /
                 math.sqrt(display.width ** 2 + display.height ** 2))
            canvas.set(x, y, r, g, b, 2.0)


if __name__ == "__main__":
    test_null()
