# Framework Part 1

The triangle demo was a lot of code, so let's framework it.
Look at :material-file-code: `02_triangle_window.py` to see how much
code is reduced and how readable it becomes.

## Vertex Arrays

Simplifying VAOs is pretty useful.
Instead of using `glBindVertexArray` everywhere, let's give it a context decorator.
The `glEnableVertexAttribArray` and `glVertexAttribPointer` functions can become methods.
Those functions do require the VAO be bound before being called,
which is something the methods could verify.

```python title="Prototype VAO use case"
from OpenGL import GL

vao: VAO = create_vao()
with vao:
    vao.enableAttrib(0)
    vao.attribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 3 * 4, 0)
```

Implementation can seem funky considering globals are being used to track state.
Globals aren't always bad, they exist for a reason.

```python title="frameworks/buffers.py"
import ctypes
from dataclasses import dataclass

from OpenGL import GL

# This 'global' can track the state.
# Only one VAO can be active at a time, so methods can error when the state does not match.
_vao: int = 0


@dataclass(slots=True)
class VAO:
    handle: int

    def __enter__(self):
        global _vao
        assert _vao == 0
        GL.glBindVertexArray(self.handle)
        _vao = self.handle
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        global _vao
        assert _vao == self.handle
        # Unbind
        GL.glBindVertexArray(0)
        _vao = 0

    def enableAttrib(self, index: int):
        assert _vao == self.handle, "VAO was not bound."
        GL.glEnableVertexAttribArray(index)

    def disableAttrib(self, index: int):
        assert _vao == self.handle, "VAO was not bound."
        GL.glDisableVertexAttribArray(index)

    def attribPointer(self, index, size, gl_type, normalized, stride, pointer):
        assert _vao == self.handle, "VAO was not bound."
        # The pointer is funky because integer 0 works fine,
        # but any value higher than that converts badly.
        # This is why it needs manually conversion to a pointer.
        if isinstance(pointer, (int, float)):
            pointer = ctypes.c_void_p(int(pointer))
        GL.glVertexAttribPointer(index, size, gl_type, normalized, stride, pointer)

    def __int__(self):
        return self.handle


def create_vao():
    handle: int = GL.glGenVertexArrays(1)
    assert handle > 0
    return VAO(handle)
```

## Vertex Buffers

The Vertex Buffer is a bit more complicated because it can exist in multiple contexts.
The initial setup with `create_vao` can be replicated to `create_vbo`.
The `VBO` does not need its own `__enter__` and `__exit__` because
Instead, it can have methods for each target.
For example, the call of  `GL.glBindBuffer(vbo, GL.GL_ARRAY_BUFFER)` can be
implemented as `with vbo.array_buffer() as buffer: ...`.

That contextualized the buffer and makes its lifetime explicit.
This BoundBuffer can then implement `glBindBuffer` on the `__enter__`,
unbind it on the `__exit__` and implement `glBufferData` in a controlled manner.

```python 
from dataclasses import dataclass
from OpenGL import GL


@dataclass(slots=True, repr=True)
class VBO:
    handle: int

    def array_buffer(self):
        return BoundBuffer(self, GL.GL_ARRAY_BUFFER)

    def __int__(self):
        return self.handle


@dataclass(slots=True, repr=True)
class BoundBuffer:
    vbo: VBO
    target: int

    def __enter__(self):
        GL.glBindBuffer(self.target, int(self.vbo))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        GL.glBindBuffer(self.target, 0)  # unbind

    def buffer_data(self, data, draw):
        # (GL.GL_ARRAY_BUFFER, n_bytes, data, GL.GL_*_DRAW)
        GL.glBufferData(int(self.target), data.nbytes, data, int(draw))
```

## Vertex Data

Vertex Data (at this stage) is still pretty simple.
Introducing a build is *slightly* excessive.
Methods give context to data, even if it is little to no data.
In later sections, things will get more complicated.
Only XYZ coordinates have been used so far, so only an `xyz` method is needed.
For simplicity, the 'z' can default to `0`.

```python title="Usage sketch"
vertices = (
    VertexData()
    # top
    .xyz(0.0, 1.0)
    # bottom-left
    .xyz(0.0, -1.0)
    # bottom-right
    .xyz(1.0, -1.0)
    # ---
    .to_array()
)
```

The imlementation is dead simple.

```python
from dataclasses import dataclass, field
from typing import Self

import numpy as np

@dataclass(slots=True, repr=True)
class VertexData:
    # Storage might change later in order to support different types.
    _data: list[float] = field(default_factory=list) 

    def xyz(self, x: float, y: float, z: float = 0) -> Self:
        self._data.extend((x, y, z))
        return self

    def to_array(self):
        # This might get flattened to np.uint8 later on.
        return np.array(self._data, dtype=np.float32)
```

## Shaders

Shaders can be complicated, so in this chapter is laid the foundation
for future code. 

### Objects

The `Shader` class is just a shell of `handle:int`, `shader_type: int` and `__int__`.
That's almost nothing, which is fine considering it may get deleted later.

The `Program` class is a skeleton, containing a `handle: int` and
implementing `__int__`, `use()` and `delete()`.

### Helpers

The shaders can be loaded from files.
First, update the `compile_shader(...)` to accept a `pathlib.Path` as code.
This can be done with a simple `isinstance` check.
Make it easy on yourself and integrate the filename into error messages.
The return type should become a `Shader` instance.

Second, write a `compile_program(shaders: list) -> Program` to make it easier.
Remember that `glAttachShader` does not need a 'type' and simply uses an integer.
In order to make integers and `Shader` objects interchangeable,
simply use `int(...)` to cast the type of `Shader` instances. 
Anything which is already an integer will remain unaffected.

Thirdly, create a `ShaderBuilder`.
This has a "Fluent Interface", meaning the method calls can be chained.
That syntax should be pretty explicit and easy to read.

```python
from pathlib import Path

program: Program = (
    ShaderBuilder()
    .vertex(Path('vertex.vs'))
    .fragment(Path('fragment.fs'))
    .to_array()
)
```

This makes it pretty clear `vertex(...)` is loading a vertex shader, 
`fragment(...)` is a fragment shader,
and `compile()` should result in a Program.

The code itself should be structure (roughly) like this:

```python
from pathlib import Path
from OpenGL import GL


def compile_shader(typed: int, code: str | Path) -> Shader:
    ...


def compile_program(shaders: list[Shader | int]) -> Program:
    ...


class ShaderBuilder:
    def __init__(self):
        self.shaders = {}

    def vertex(self, path: Path):
        self.shaders[GL.GL_VERTEX_SHADER] = compile_shader(GL.GL_VERTEX_SHADER, path)
        return self

    def fragment(self, path: Path):
        self.shaders[GL.GL_FRAGMENT_SHADER] = compile_shader(GL.GL_FRAGMENT_SHADER, path)
        return self

    def compile(self) -> int:
        return compile_program(self.shaders.values())
```
