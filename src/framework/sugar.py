"""
Sugar Syntax for *some* clarity.
"""

__all__ = ["VertexData"]

from dataclasses import dataclass, field
from typing import Self

import numpy as np


@dataclass()
class VertexData:
    """
    VertexData Object for sugar syntax.
    """
    _data: list = field(default_factory=list)

    def xyz(self, x: float, y: float, z: float = 0.0) -> Self:
        """
        Add XYZ point to the internal buffer.
        :param x: X coordinate.
        :param y: Y coordinate.
        :param z: Z coordinate.
        :return: Self
        """
        self._data.extend((x, y, z))
        return self

    def rgb(self, r: float, g: float, b: float) -> Self:
        """
        Add an RGB color to the internal buffer.
        :param r: Red (0.0-1.0)
        :param g: Green (0.0-1.0)
        :param b: Blue (0.0-1.0)
        :return: Self
        """
        self._data.extend((r, g, b))
        return self

    def rgba(self, r: float, g: float, b: float, a: float = 1.0) -> Self:
        """
        Add an RGBA color to the internal buffer.
        :param r: Red (0.0-1.0)
        :param g: Green (0.0-1.0)
        :param b: Blue (0.0-1.0)
        :param a: Alpha (0.0-1.0)
        :return: Self
        """
        self._data.extend((r, g, b, a))
        return self

    def uv(self, u: float, v: float) -> Self:
        """
        Add UV (texture) coordinates to the internal buffer.
        :param u: U coordinate.
        :param v: V coordinate.
        :return: Self
        """
        self._data.extend((u, v))
        return self

    def to_array(self):
        """
        Compile the data to array and return it.
        :return: Data.
        """
        return np.array(self._data, np.float32)
