import time

import pygame
from OpenGL import GL


def main():
    pygame.init()

    # Create an OpenGL context with Double Buffering
    pygame.display.set_mode((800, 600), pygame.DOUBLEBUF | pygame.OPENGL)
    pygame.display.set_caption("Simple Window")

    # Define an exit timestamp, just in case.
    start = time.time()
    end = start + 60
    total = end - start

    # This only defines the clear color.
    # `glClearColor`(R, G, B, A)`
    # This uses float points range `0.0` to `1.0`.
    GL.glClearColor(0.0, 0, 0.5, 1.0)

    while time.time() < end:
        # Using 'd' between 0.0 and 1.0 based on time.
        # This increases 'red' over time, causing a color shift.
        d = (time.time() - start) / total
        GL.glClearColor(d, 0, 0.5, 1.0)

        # Tell the buffer to be cleared (color & depth buffer)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        # Swap the buffers so the rendered image gets shown.
        pygame.display.flip()

        # Wait for 1 frame (assuming 30fps).
        # GPUs will happily run a million FPS, but makes them run hot.
        # Slow this down for the sake of it.
        pygame.time.wait(1000 // 30)

        # Work the event loop.
        # Pygame events are anything on the event loop.
        for event in pygame.event.get():
            # pygame.QUIT is window closing.
            if event.type == pygame.QUIT:
                end = 0

    # Cleanup, a formality.
    pygame.quit()


if __name__ == "__main__":
    main()
