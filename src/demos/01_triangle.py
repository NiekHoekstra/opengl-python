import ctypes
from functools import partial

import numpy as np
import pygame.time

from framework.easy import Easy

vs = """#version 330 core
layout (location = 0) in vec3 aPos;
out vec3 iPos;
void main()
{
    gl_Position = vec4(aPos, 1.0);
    iPos = aPos;
}
"""

fs = """#version 330 core
out vec4 FragColor;
void main() {
    FragColor = vec4(1.0f, 0.5f, 0.2f, 1.0f);
} 
"""
z = 0
vertices = np.array([
    0.0, 1.0, z,  # Top vertex
    -1.0, -1.0, z,  # Bottom left vertex
    1.0, -1.0, z  # Bottom right vertex
], dtype='float32')

import pygame
from OpenGL import GL


def _render(vao: int, vbo: int):
    GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3)


def compile_shader(gl_type, source) -> int:
    shader = GL.glCreateShader(gl_type)
    GL.glShaderSource(shader, source)
    GL.glCompileShader(shader)
    result: int = GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS)
    if result != 1:
        error = GL.glGetShaderInfoLog(shader)
        if isinstance(error, bytes):
            error = error.decode('utf-8')
        raise RuntimeError(error)
    return shader


def compile_program():
    p = GL.glCreateProgram()
    GL.glAttachShader(p, compile_shader(GL.GL_VERTEX_SHADER, vs))
    GL.glAttachShader(p, compile_shader(GL.GL_FRAGMENT_SHADER, fs))
    GL.glValidateProgram(p)
    GL.glLinkProgram(p)
    result: int = GL.glGetProgramiv(p, GL.GL_LINK_STATUS)
    if result != 1:
        error = GL.glGetProgramInfoLog(p)
        if isinstance(error, bytes):
            error = error.decode('utf-8')
        raise RuntimeError(error)
    return p


def main():
    demo = Easy()
    demo.setup()
    # ---
    vao = GL.glGenVertexArrays(1)
    vbo = GL.glGenBuffers(1)
    # ---
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
    GL.glBufferData(
        GL.GL_ARRAY_BUFFER,  # target
        vertices.nbytes,  # size
        vertices,  # data
        GL.GL_STATIC_DRAW  # usage
    )
    GL.glBindVertexArray(vao)
    GL.glEnableVertexAttribArray(0)
    GL.glVertexAttribPointer(
        0,  # index
        3,  # size
        GL.GL_FLOAT,  # type
        GL.GL_FALSE,  # normalized
        3 * 4,  # stride
        ctypes.c_void_p(0),  # pointer
    )
    # ---
    p = compile_program()
    GL.glUseProgram(p)
    #
    demo.loop(
        None,
        partial(_render, vao, vbo)
    )
    # Cleanup, a formality.
    pygame.quit()


if __name__ == "__main__":
    main()
