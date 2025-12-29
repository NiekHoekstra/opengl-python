"""
https://www.khronos.org/opengl/wiki/Shader_Compilation
"""

__all__ = [
    "ShaderBuilder",
    "compile_program",
    "compile_shader",
]

import inspect
import logging
from pathlib import Path

from OpenGL import GL

from .objects import Program, Shader, ShaderError, ShaderSource, ShaderType

logger = logging.getLogger("framework.shaders")


def compile_shader(
    typed: ShaderType | int, source: str | Path | ShaderSource, name: str | None = None
) -> Shader:
    """
    Compile a shader program.
    :param typed: Shader Type.
    :param source: Shader source code or file Path.
    :param name: Filename (optional).
    :return: Compiled Shader.
    """
    if isinstance(source, str):
        name = name or "untitled"
    elif isinstance(source, ShaderSource):
        name = source.name
        source = source.source
    else:
        if name is None:
            name = str(source.absolute())
        source = source.read_text()

    shader: int = GL.glCreateShader(int(typed))
    GL.glShaderSource(shader, source)
    GL.glCompileShader(shader)
    result: int = GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS)
    if result != 1:
        error = GL.glGetShaderInfoLog(shader)
        if isinstance(error, bytes):
            error = error.decode("utf-8")
        typename: str
        if isinstance(typed, ShaderType):
            typename = typed.name
        else:
            typename = f"shader({hex(typed)})"
        raise ShaderError(f'Error in {typename} "{name}"\n' + error)
    return Shader(handle=shader, type=ShaderType(typed))


def compile_program(shaders: list[int | Shader], name: str | None = None) -> Program:
    """
    Compile a shader program based on Shader names and instances.
    :param shaders: Shaders to attach.
    :param name: Name of the program (for debugging).
    :return: Compiled Program.
    """
    program: int = GL.glCreateProgram()
    for entry in shaders:
        GL.glAttachShader(program, int(entry))

    GL.glValidateProgram(program)
    GL.glLinkProgram(program)
    result: int = GL.glGetProgramiv(program, GL.GL_LINK_STATUS)

    for entry in shaders:
        GL.glDetachShader(program, int(entry))

    if result != 1:
        error = GL.glGetProgramInfoLog(program)
        if isinstance(error, bytes):
            error = error.decode("utf-8")

        name = f"ShaderProgram:{name}" if name else "ShaderProgram"
        raise ShaderError(f"Error in {name}:\n{error}")

    return Program(program)


class ShaderBuilder:
    """
    Builder for a ShaderProgram.
    """

    def __init__(self):
        self.shaders = {}

    def vertex(self, shader: str | ShaderSource | Shader | Path):
        """
        Set the Vertex Shader.
        :param shader: Shader, source or file Path.
        :return: Self.
        """
        self._load(ShaderType.VERTEX_SHADER, shader)
        return self

    def fragment(self, shader: str | ShaderSource | Shader | Path):
        """
        Set the Fragment Shader.
        :param shader: Shader, source or file Path.
        :return: Self.
        """
        self._load(ShaderType.FRAGMENT_SHADER, shader)
        return self

    def _load(self, typed: ShaderType, value: str | ShaderSource | Shader | Path):
        """
        Load a shader with a specific type.
        :param typed: Shader type.
        :param value: Shader Value
        :return:
        """
        shader = value
        if isinstance(value, str):
            # Raw source code: Track down the origin in case of errors.
            frame = inspect.currentframe().f_back.f_back
            name = frame.f_code.co_filename + ":" + str(frame.f_lineno)
            shader = compile_shader(typed, value, name=name)
        elif isinstance(value, ShaderSource):
            # Annotated Shader Source: compile it.
            shader = compile_shader(typed, value)
        elif isinstance(value, Path):
            # File, double-check the suffix (if applicable).
            _expected = {
                ".fs": ShaderType.FRAGMENT_SHADER,
                ".vs": ShaderType.VERTEX_SHADER,
            }.get(value.suffix.lower())
            if _expected and _expected != typed:
                logger.warning(
                    f"Shader type {typed} had unexpected suffix {value.suffix}."
                )
            shader = compile_shader(typed, value.read_text(), name=str(value))

        if not isinstance(shader, Shader):
            raise TypeError(f"Expected shader {typed!r}, got {value!r}")
        self.shaders[shader.type] = shader

    def compile(self, name: str | None = None) -> Program:
        """
        Compile the shaders and return the program
        :param name: Name (for debugging).
        :return: Shader Program.
        """
        shaders = list(self.shaders.values())
        return compile_program(shaders, name)

    def clear(self):
        self.shaders.clear()
