"""
Provides various buffer systems.
"""

__all__ = [
    "BufferTarget",
    "Draw",
    "VAO",
    "VBO",
    "BoundBuffer",
    "ArrayBuffer",
    "ElementBuffer",
    "ReadBuffer",
    "WriteBuffer",
    "create_vao",
    "create_vbo",
]

import ctypes
import dataclasses
import enum
from typing import Union

from OpenGL import GL
from numpy.typing import ArrayLike

_vao: int = 0
"""Bound vertex array object."""

_bufferstate: dict[int, int] = {}
"""State of all buffers, used to detect mixed bindings."""

GL_BOOL = Union[GL.GL_TRUE, GL.GL_FALSE]


class Draw(enum.IntEnum):
    """GL_*_DRAW Constant"""

    STATIC = GL.GL_STATIC_DRAW
    """The data store contents will be modified once and used many times."""
    DYNAMIC = GL.GL_DYNAMIC_DRAW
    """The data store contents will be modified repeatedly and used many times."""
    STREAM = GL.GL_STREAM_DRAW
    """The data store contents will be modified once and used at most a few times. """


class BufferTarget(enum.IntEnum):
    """
    Targets for the BindBuffer.
    https://docs.gl/gl3/glBindBuffer
    """

    ARRAY = GL.GL_ARRAY_BUFFER
    READ = GL.GL_COPY_READ_BUFFER
    WRITE = GL.GL_COPY_WRITE_BUFFER
    ELEMENT_ARRAY = GL.GL_ELEMENT_ARRAY_BUFFER
    PIXEL_PACK = GL.GL_PIXEL_PACK_BUFFER
    PIXEL_UNPACK = GL.GL_PIXEL_UNPACK_BUFFER
    TEXTURE = GL.GL_TEXTURE_BUFFER
    TRANSFORM_FEEDBACK = GL.GL_TRANSFORM_FEEDBACK_BUFFER
    UNIFORM = GL.GL_UNIFORM_BUFFER


@dataclasses.dataclass(repr=True)
class VAO:
    """Vertex Array Object"""

    handle: int
    """The name or handle of the VAO."""
    state: dict = dataclasses.field(default_factory=dict)
    """Debug information"""

    def __enter__(self):
        global _vao
        self.bind()
        _vao = self.handle

    def __exit__(self, exc_type, exc_val, exc_tb):
        global _vao
        if _vao == self.handle:
            _vao = 0
        GL.glBindVertexArray(0)

    def bind(self):
        """Explicit binding, please use `__enter__` context instead."""
        global _vao
        GL.glBindVertexArray(self.handle)
        _vao = self.handle

    def enableAttrib(self, index: int):
        """
        Enable Vertex Attribute by index.
        This is commonly annotated with `location` in shader code.
        :param index: Index to enable.
        """
        assert self.handle == _vao, "VAO was not bound."
        GL.glEnableVertexAttribArray(index)

    def disableAttrib(self, index: int):
        """
        Disable Vertex Attribute by index.
        :param index: Index to disable.
        """
        assert self.handle == _vao, "VAO was not bound."
        GL.glDisableVertexAttribArray(index)

    def attribPointer(
        self,
        index: int,
        size: int,
        gl_type: int,
        normalized: GL_BOOL,
        stride: int,
        pointer: int,
    ):
        """
        Define a Vertex Attribute Pointer.
        :param index: Index of the vertex attribute to configure.
        :param size: The size of each entry.
        :param gl_type: The datatype for those entries.
        :param normalized: Normalize according to gl_type.
        :param stride: Space between entries as flat bytes.
        :param pointer: The initial offset for the data.
        """
        assert self.handle == _vao
        # Use a (void*), otherwise it converts poorly.
        if isinstance(pointer, (int, float)):
            pointer = ctypes.c_void_p(int(pointer))
        GL.glVertexAttribPointer(index, size, gl_type, normalized, stride, pointer)


@dataclasses.dataclass(repr=True)
class VBO:
    """Vertex Array Object"""

    handle: int
    """The name or handle of the VBO."""

    def array_buffer(self):
        """
        Provides a context for `glBindBuffer(GL_ARRAY_BUFFER)`.
        :return: ArrayBuffer context.
        """
        return ArrayBuffer(self, BufferTarget.ARRAY)

    def element_buffer(self):
        """
        Provides a context for `glBindBuffer(GL_ARRAY_ELEMENT_BUFFER)`.
        :return: ElementBuffer context.
        """
        return ElementBuffer(self, BufferTarget.ELEMENT_ARRAY)

    def read_buffer(self): ...

    def write_buffer(self): ...

    def uniform_buffer(self): ...

    def __int__(self):
        return self.handle

    def delete(self):
        """Delete the buffer."""
        if self.handle == -1:
            raise RuntimeError("Already deleted")
        GL.glDeleteBuffers(1, [self.handle])
        self.handle = -1


@dataclasses.dataclass(repr=True)
class BoundBuffer:
    """Represents a bound VBO."""

    vbo: VBO
    """Targeted Vertex Buffer Object"""

    target: BufferTarget
    "Buffer Target."

    def __enter__(self):
        if _bufferstate.get(int(self.target), 0) != 0:
            raise RuntimeError("Weird unbinding issue?")
        GL.glBindBuffer(int(self.target), int(self.vbo))
        _bufferstate[int(self.target)] = int(self.vbo)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        GL.glBindBuffer(int(self.target), 0)
        if _bufferstate.get(int(self.target), 0) == int(self.vbo):
            _bufferstate[int(self.target)] = 0

    def buffer_data(self, data: ArrayLike, draw: Draw):
        """
        Put data in the buffer.
        This method always allocates a completely new buffer.
        To replace buffer data, use `buffer_sub_data`.
        :param data: Data to use, `np.array` is advised.
        :param draw: Draw usage.
        """
        assert _bufferstate.get(int(self.target), 0) == int(self.vbo)
        GL.glBufferData(int(self.target), data.nbytes, data, int(draw))

    def buffer_sub_data(self, offset: int, data: ArrayLike, draw: Draw):
        """
        Put data in the buffer.
        :param offset: Offset (in bytes).
        :param data: Data to use, `np.array` is advised.
        :param draw: Draw usage.
        """
        assert _bufferstate.get(int(self.target), 0) == int(self.vbo)
        GL.glBufferSubData(int(self.target), offset, data.nbytes, int(draw))


class ArrayBuffer(BoundBuffer): ...


class ElementBuffer(BoundBuffer): ...


class ReadBuffer(BoundBuffer): ...


class WriteBuffer(BoundBuffer): ...


def create_vao() -> VAO:
    """
    Create a new Vertex Array Object.
    :return: VAO instance.
    """
    name = GL.glGenVertexArrays(1)
    assert 0 < name
    return VAO(int(name))


def create_vbo() -> VBO:
    """
    Create a new Vertex Buffer Object.
    :return: VBO instance.
    """
    name = GL.glGenBuffers(1)
    assert 0 < name
    return VBO(int(name))
