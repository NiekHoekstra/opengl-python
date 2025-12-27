"""
Basic windowing system.
"""

__all__ = ["GLWindow"]

import pygame
from OpenGL import GL

from framework.debug import start_opengl_logger

RGB = tuple[float, float, float]
RGBA = tuple[float, float, float, float]
_PINK: RGBA = 1.0, 0.0, 1.0, 1.0


class GLWindow:
    """
    Basic OpenGL Window.
    """

    __slots__ = ("title", "size", "clearColor", "clearMask", "mode", "debug")
    title: str
    """Window title"""
    size: tuple[int, int]
    """Window size (width, height)"""
    clearColor: RGBA
    """OpenGL Clear color."""
    clearMask: int
    """OpenGL Clear mask"""
    mode: int
    """Mode flags (Double Buffer, etc.)"""

    def __init__(
        self,
        title: str = "untitled",
        size: tuple[int, int] = (800, 600),
        clear: RGB | RGBA = _PINK,
        debug: bool = False,
    ):
        """
        Initialize window.
        :param title: Window title.
        :param size: Window size.
        :param clear:Clear color in RGB(A).
        :param debug: When True, enable the OpenGL debugger.
        """
        self.title = title
        self.size = size
        if len(clear) == 3:
            clear = tuple(clear) + (1.0,)
        self.clearColor = clear
        self.clearMask = GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT
        self.mode = pygame.DOUBLEBUF | pygame.OPENGL
        self.debug = debug

    def __enter__(self):
        """Initialize and show."""
        if not pygame.get_init():
            pygame.init()
        pygame.display.set_mode(self.size, self.mode)
        pygame.display.set_caption(self.title)
        GL.glClearColor(*self.clearColor)
        if self.debug:
            start_opengl_logger()
        return self

    def clear(self):
        """
        Perform glClear operation.
        :return:
        """
        GL.glClear(self.clearMask)

    def flip(self):
        """
        Perform glFlip operation.
        :return:
        """
        pygame.display.flip()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close and exit."""
        if exc_val is None:
            pygame.quit()
