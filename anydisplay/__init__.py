"""
Classes and functions for displaying anything on anything (in theory).
"""

# ======================================================================

from   abc    import ABC, abstractmethod
from   PIL    import Image
from   typing import Tuple

import logging
import math
import numpy

# ======================================================================

class Display(ABC):
    """
    The interface which all displays must implement. This is the interface to
    the hardware which actually does the displaying.

    It can be used directly or via the `Canvas` class.

    Display origin ``(0,0)`` is the top left.
    """
    def __init__(self):
        self._orientation = 0


    @property
    def width(self) -> int:
        """
        The display width.
        """
        return self.get_shape()[0]


    @property
    def height(self) -> int:
        """
        The display width.
        """
        return self.get_shape()[1]


    @property
    def orientation(self) -> int:
        """
        The display orientation.
        """
        return self._orientation


    @abstractmethod
    def get_shape(self) -> Tuple[int,int]:
        """
        :return: The ``width`` x ``height`` of the display.
        """
        return (0, 0)


    @abstractmethod
    def clear(self) -> None:
        """
        Clear the display contents.
        """
        pass


    @abstractmethod
    def set(self,
            x: int,
            y: int,
            r: float,
            g: float,
            b: float) -> None:
        """
        The the value of the pixel at given coordinates to the given colour. The
        colour is specified as an RGB value with ranges from zero to one
        inclusive.

        :param x: The x coordinate.
        :param y: The y coordinate.
        :param r: The red value, ``[0,1]``.
        :param g: The green value, ``[0,1]``.
        :param b: The blue value, ``[0,1]``.
        """
        pass


    @abstractmethod
    def show(self) -> None:
        """
        Flush any pending `set` and `clear` calls so that they are displayed.
        """
        pass


    def set_orientation(self, orientation: int) -> None:
        """
        Set the orientation of the display to one of ``0``, ``90``, ``180`` or
        ``270`` degrees.

        :param orientation: The new orientation value, in degrees
        """
        if orientation not in (0, 90, 180, 270):
            raise ValueError("Bad orientation: %s" % (orientation,))
        self._orientation = orientation


    def quit(self) -> None:
        """
        Shut down the display.
        """
        self.clear()
        self.show()


    def _orient(self,
                x : int,
                y : int) -> Tuple[int,int]:
        """
        Give back the x and y values according to the orientation value.
        """
        if   self._orientation ==   0:
            return (x,
                    y)
        elif self._orientation ==  90:
            return (y,
                    x)
        elif self._orientation == 180:
            return (self._image.width  - x,
                    self._image.height - y)
        elif self._orientation == 270:
            return (self._image.width  - y,
                    self._image.height - x)
        else:
            raise ValueError("Bad orientation: %s" % (self._orientation,))


class NullDisplay(Display):
    """
    A display which does nothing.
    """
    def __init__(self, width : int, height : int):
        super().__init__()
        self._width  = max(1, int(width))
        self._height = max(1, int(height))


    def get_shape(self) -> Tuple[int,int]:
        return (self._width, self._height)


    def set_orientation(self, orientation: int) -> None:
        pass


    def clear(self):
        pass


    def set(self,
            x: int,
            y: int,
            r: float,
            g: float,
            b: float) -> None:
        pass


    def show(self):
        pass


# ----------------------------------------------------------------------


class Canvas():
    """
    An abstraction layer for using a `Display`. This adds bells and whistles
    which handle things like differences between the logical display and the
    physical one.

    For example, the canvas size may be different from that of the underlying
    display.
    """
    def __init__(self,
                 display : Display,
                 width   : int     = None,
                 height  : int     = None,
                 xwrap   : bool    = False,
                 ywrap   : bool    = False):
        """
        :param display: The display to render to.
        :param width:   The canvas width, in pixels.
        :param height:  The canvas height, in pixels.
        :param xwrap:   Whether the ``x`` values should wrap around.
        :param ywrap:   Whether the ``y`` values should wrap around.
        """
        width  = display.width  if width  is None else width
        height = display.height if height is None else height
        if width <= 0:
            raise ValueError("Bad width: %s" % width)
        if height <= 0:
            raise ValueError("Bad height: %s" % height)

        # The display details
        self._x_sz    = width
        self._y_sz    = height
        self._display = display
        self._scale   = min(display.width  / width,
                            display.height / height)

        # The canvas is the RGB value of each _display_ pixel and what fraction of it has
        # been painted
        self._canvas  = numpy.zeros(shape=(display.width, display.height, 4),
                                    dtype=numpy.float64)

        # Wrapping?
        self._xwrap = xwrap
        self._ywrap = ywrap

        # Hidden debugging toggle. See below for why.
        self._debug = False


    @property
    def width(self) -> int:
        """
        The display width.
        """
        return self._x_sz


    @property
    def height(self) -> int:
        """
        The display width.
        """
        return self._y_sz


    def clear(self):
        """
        Clear the canvas contents.
        """
        self._display.clear()
        self._canvas[:,:,:] = 0.0


    def set(self,
            x: float,
            y: float,
            r: float,
            g: float,
            b: float,
            s: float = 1.0) -> None:
        """
        The the value of the pixel at given coordinates to the given colour. The
        colour is specified as an RGB value with ranges from zero to one
        inclusive.

        :param x: The x coordinate.
        :param y: The y coordinate.
        :param r: The red value, ``[0,1]``.
        :param g: The green value, ``[0,1]``.
        :param b: The blue value, ``[0,1]``.
        :param s: The pixel size.
        """
        # This code needs to be fast so we have a few optimisations:
        #  o Avoid transient tuple creation
        #  o Local versions of constants
        #  o Avoid function calls

        if self._debug:
            logging.debug(f'x={x} y={y} r={r} g={g} b={b} s={s}')

        # Local handles on a few things which we use a lot
        width  = self._display.width
        height = self._display.height
        canvas = self._canvas
        xwrap  = self._xwrap
        ywrap  = self._ywrap

        # Do nothing if the scale was effectively a NOP
        scale = s * self._scale
        if scale <= 0.0:
            return

        # Determine the display's coordinates
        dx = x * self._scale
        dy = y * self._scale
        dr = r if 0 <= r <= 1 else min(max(0.0, r), 1.0)
        dg = g if 0 <= g <= 1 else min(max(0.0, g), 1.0)
        db = b if 0 <= b <= 1 else min(max(0.0, b), 1.0)
        if self._debug:
            logging.debug(f'dx={dx} dy={dy} dr={dr} dg={dg} db={db} scale={scale}')

        # See if we have the simple case of direct setting
        if scale == 1.0                    and \
           int(dx) == dx and int(dy) == dy and \
           0 <= dx < width   and \
           0 <= dy < height:
            # Remember and set everything directly
            dx = int(dx)
            dy = int(dy)
            pixel = canvas[dx][dy]
            pixel[0] = dr
            pixel[1] = dg
            pixel[2] = db
            pixel[3] = 1.0
            self._display.set(dx, dy, dr, dg, db)

        elif scale < 1.0     and \
             0 <= dx < width and \
             0 <= dy < height:
            # Drawing a subpixel, we can try to be quick about this. This is
            # just the code from the inner loop below but pulled out
            px = int(dx)
            py = int(dy)
            pixel = canvas[px][py]
            pr = pixel[0]
            pg = pixel[1]
            pb = pixel[2]
            pf = pixel[3]

            # The area we are drawing, and hence the factor, is the size of the
            # pixel, which is the scale^2.
            factor = scale**2

            # Account for the fact that the area might not have been
            # fully painted previously
            factor1 = 1.0 - factor
            if pf == 0.0 or pf <= factor1:
                # This is a straight addition since we're not "taking
                # away" from the existing space. E.g. if we'd only
                # painted 0.1 of the canvas before and now we're
                # painting 0.7 then there's still 0.2 of unaccounted for
                # space.
                pr = pr + factor * dr
                pg = pg + factor * dg
                pb = pb + factor * db
                pf = factor + pf
            else:
                # Okay, here we're taking away from what was there
                # before. We account for this by scaling the existing
                # colour into the same space before we take the weighted
                # average. We fold this into the factor1 value to save
                # multiple divides. Here pf can't be zero since we
                # checked above.
                pfactor1 = factor1 / pf
                pr = min(pfactor1 * pr + factor * dr, 1.0)
                pg = min(pfactor1 * pg + factor * dg, 1.0)
                pb = min(pfactor1 * pb + factor * db, 1.0)
                pf = 1.0 # <-- fully painted now

            # Remember
            pixel[0] = pr if pr < 1.0 else 1.0
            pixel[1] = pg if pg < 1.0 else 1.0
            pixel[2] = pb if pb < 1.0 else 1.0
            pixel[3] = pf if pf < 1.0 else 1.0

            # And, finally, push those values to the display itself!
            self._display.set(px, py, pr, pg, pb)

        else:
            # Okay, we're going to paint a fractional square which is centered
            # around dx,dy. We need to determine the integer pixels which we are
            # going to set on the display and see what fractional part of them
            # we are setting. We need to get the left and right and top and
            # bottom corners, which we clip against the display edge.
            #
            # Remember that:
            #   0,0 is the top left
            #   We're in a discrete space here (pixels)
            #
            # So a scale of 2 at 5,5 means (5,5) to (6,6). A scale of 3 means
            # (4,4) to (6,6). Of 4 means (4,4) to (7,7). And so on.
            half = max(0.0, (scale - 1.0) / 2.0)
            if int(scale) & 1:
                # Odd scale grows right with the fraction
                l_off = int(half)
                r_off = scale - l_off
            else:
                # Even grows left
                r_off = int(half)
                l_off = scale - r_off
            dxl = dx - l_off
            dxr = dx + r_off
            dyt = dy - l_off
            dyb = dy + r_off

            # Walk each pixel and compute the fraction, then set
            if self._debug:
                logging.debug(f'px=[{dxl},{dxr}] py=[{dyt},{dyb}]')
            for px_ in range(int(dxl), int(dxr) + 1):
                for py_ in range(int(dyt), int(dyb) + 1):
                    # Copy, since we noodle these
                    px = px_
                    py = py_

                    # See how we are clipping the value, to determine the pixel
                    # area. Since the area of a pixel is 1x1=1 the area here is
                    # also the fraction. Here the far corner of the pixel is the
                    # near corner of the adjacent pixel, when it comes to
                    # computing the area.
                    cxl  = max(dxl, px+0)
                    cxr  = min(dxr, px+1)
                    cyt  = max(dyt, py+0)
                    cyb  = min(dyb, py+1)
                    area = abs(cxr - cxl) * abs(cyb - cyt)

                    # The blending factor is the area of the display pixel
                    # covered. 0 means none and 1.0 means all. If this factor
                    # is non-postive then we have nothing to do.
                    factor = area
                    if factor <= 0.0:
                        continue
                    if factor > 1.0:
                        factor = 1.0

                    # Now noodle the pixel x,y if we are wrapping. Else we bail
                    # if it's out of bounds.
                    if px < 0 or px >= width:
                        if xwrap:
                            if px < 0:
                                px += width
                            else:
                                px -= width
                        else:
                            continue
                    if py < 0 or py >= height:
                        if ywrap:
                            if py < 0:
                                py += height
                            else:
                                py -= height
                        else:
                            continue

                    # Finally we can now set it. We do this by blending with
                    # what was there before.
                    pixel = canvas[px][py]
                    pr = pixel[0]
                    pg = pixel[1]
                    pb = pixel[2]
                    pf = pixel[3]
                    if self._debug:
                        logging.debug(
                            f'px={px} py={py} pr={pr} pg={pg} pb={pb} pf={pf} factor={factor}'
                        )

                    # Account for the fact that the area might not have been
                    # fully painted previously
                    factor1 = 1.0 - factor
                    if pf == 0.0 or pf <= factor1:
                        # This is a straight addition since we're not "taking
                        # away" from the existing space. E.g. if we'd only
                        # painted 0.1 of the canvas before and now we're
                        # painting 0.7 then there's still 0.2 of unaccounted for
                        # space.
                        pr = pr + factor * dr
                        pg = pg + factor * dg
                        pb = pb + factor * db
                        pf = factor + pf
                    else:
                        # Okay, here we're taking away from what was there
                        # before. We account for this by scaling the existing
                        # colour into the same space before we take the weighted
                        # average. We fold this into the factor1 value to save
                        # multiple divides. Here pf can't be zero since we
                        # checked above.
                        pfactor1 = factor1 / pf
                        pr = min(pfactor1 * pr + factor * dr, 1.0)
                        pg = min(pfactor1 * pg + factor * dg, 1.0)
                        pb = min(pfactor1 * pb + factor * db, 1.0)
                        pf = 1.0 # <-- fully painted now

                    # Remember
                    pixel[0] = pr if pr < 1.0 else 1.0
                    pixel[1] = pg if pg < 1.0 else 1.0
                    pixel[2] = pb if pb < 1.0 else 1.0
                    pixel[3] = pf if pf < 1.0 else 1.0

                    # And, finally, push those values to the display itself!
                    self._display.set(px, py, pr, pg, pb)


    def set_image(self,
                  image: Image) -> None:
        """
        Display the given image on the display.

        This isn't too fast right now.
        """
        # Get the relative dimensions
        (dw, dh) = self._display.get_shape()
        (iw, ih) = image.size
        if iw <= 0 or ih <= 0:
            raise ValueError("Bad image dimensions: %d x %d" % (iw, ih))

        # Determine the scaling factors, given the dimension ratios
        sw = dw / iw
        sh = dh / ih

        # The pixel size is the max of the two scales, rounded up to the next
        # int if it's a biggy so floating point issues don't give us aliasing
        # artifacts.
        sz = max(sw, sh)
        if sz > 1:
            sz = math.ceil(sz)

        # Now draw it into the display
        for ix in range(iw):
            for iy in range(ih):
                # Get the display coordinates
                dx = round(ix * sw)
                dy = round(iy * sh)

                # Copy out the RGB value we want to set
                rgb = image.getpixel((ix, iy))

                # And set!
                self.set(dx,
                         dy,
                         rgb[0] / 255,
                         rgb[1] / 255,
                         rgb[2] / 255,
                         sz)


    def show(self):
        """
        Flush any `set` calls to the display.
        """
        self._display.show()


    def quit(self):
        """
        Shuts down the display.
        """
        self._display.quit()
