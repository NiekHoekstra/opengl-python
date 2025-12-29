"""
https://www.khronos.org/opengl/wiki/Shader_Compilation
"""

__all__ = ["Shader", "ShaderType", "ShaderSource", "ShaderError", "Program"]

import dataclasses
import enum
import inspect

from OpenGL import GL


class ShaderError(Exception):
    pass


@dataclasses.dataclass(repr=True, slots=True)
class ShaderSource:
    """
    Annotated Shader Source.
    """

    source: str
    """
    Source Code.
    """
    name: str
    """
    Name (for debugging).
    """

    def __init__(self, source: str, name: str | None = None):
        """
        Initialize a new ShaderSource instance.
        :param source: Source Code.
        :param name: Name (for debugging), derives from caller if None.
        """
        self.source = source
        if name is None:
            frame = inspect.currentframe().f_back
            name = frame.f_code.co_filename + ":" + str(frame.f_lineno)
        self.name = name


class ShaderType(enum.IntEnum):
    """
    Shader Types.
    """

    VERTEX_SHADER = GL.GL_VERTEX_SHADER
    """Vertex Shader"""
    FRAGMENT_SHADER = GL.GL_FRAGMENT_SHADER
    """Fragment Shader"""


@dataclasses.dataclass(slots=True, repr=True)
class Program:
    """
    Represents a compiled program.
    """

    handle: int
    """Program Handle/Name."""

    def __int__(self):
        return int(self.handle)

    def setInt(self, name: str | int, *values: int):
        if isinstance(name, str):
            name = GL.glGetUniformLocation(self.handle, name)
        getattr(GL, f"glUniform{len(values)}i")(name, *values)

    def setBool(self, name: str, value: bool):
        if isinstance(name, str):
            name = GL.glGetUniformLocation(self.handle, name)
        GL.glUniform1i(name, value)

    def setFloat(self, name: str, *values: float):
        if isinstance(name, str):
            name = GL.glGetUniformLocation(self.handle, name)
        getattr(GL, f"glUniform{len(values)}f")(name, *values)

    def use(self):
        GL.glUseProgram(self.handle)

    def delete(self):
        GL.glDeleteProgram(self.handle)

    def getAttribLocation(self, name: str) -> int | None:
        idx = GL.glGetAttribLocation(self.handle, name)
        return None if idx == -1 else idx

    def getUniformLocation(self, name: str) -> int | None:
        idx = GL.glGetUniformLocation(self.handle, name)
        return None if idx == -1 else idx


@dataclasses.dataclass(slots=True, repr=True)
class Shader:
    """
    Represents a compiled shader.
    """

    handle: int
    """Shader Handle/Name."""
    type: ShaderType
    """Shader Type (Vertex, Fragment, etc.)."""

    # source: str | None = None

    def __int__(self):
        return self.handle
