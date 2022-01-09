"""
LED matrix displays.
"""

from   typing import Tuple
from   .      import Display

# ----------------------------------------------------------------------

class SDL(Display):
    """
    Use SDL 2.0 to display images.

    See::
        https://github.com/marcusva/py-sdl2
        pip3 install pysdl2
    """
    def __init__(self,
                 name          : str  = '',
                 width         : int  = 800,
                 height        : int  = 600,
                 full_screen   : bool = False):
        """
        :param name:        The name of the created window/display.
        :param width:       The width.
        :param height:      The height.
        :param full_screen: Whether the display should be full screen or, else,
                            in a window.
        """
        super().__init__()

        # Set up the SDL subsystem
        import sdl2
        import sdl2.ext
        sdl2.ext.init()

        # Save local handles
        self._sdl2     = sdl2
        self._sdl2_ext = sdl2.ext

        # Window creation flags
        flags = sdl2.SDL_WINDOW_SHOWN
        if full_screen:
            flags |= sdl2.SDL_WINDOW_FULLSCREEN

        # Create the window and the associated render
        self._window = sdl2.ext.Window(str(name),
                                       size=(width, height),
                                       flags=flags)
        self._renderer = sdl2.ext.Renderer(self._window)


    def get_shape(self) -> Tuple[int,int]:
        return self._window.size


    def clear(self):
        self._renderer.clear()


    def set(self,
            x: int,
            y: int,
            r: float,
            g: float,
            b: float) -> None:
        # Ensure that they are correctly oriented
        (dx, dy) = self._orient(x, y)

        # Bounds check since the call with throw otherwise
        (max_x, max_y) = self._window.size
        if 0 <= dx < max_x and 0 <= dy < max_y:
            # Okay to set
            self._renderer.draw_point(
                (dx, dy),
                self._sdl2_ext.Color(
                    int(255 * min(max(r, 0.0), 1.0)),
                    int(255 * min(max(g, 0.0), 1.0)),
                    int(255 * min(max(b, 0.0), 1.0))
                )
            )


    def show(self):
        self._renderer.present()
