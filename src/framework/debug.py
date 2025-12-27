"""
Debug tooling.
"""

__all__ = ["start_opengl_logger"]

import logging

from OpenGL import GL

logger = logging.getLogger("OpenGL")
_severity = {
    GL.GL_DEBUG_SEVERITY_NOTIFICATION: "NOTIFICATION",
    GL.GL_DEBUG_SEVERITY_LOW: "LOW",
    GL.GL_DEBUG_SEVERITY_MEDIUM: "MEDIUM",
    GL.GL_DEBUG_SEVERITY_HIGH: "HIGH",
}
_levels = {
    GL.GL_DEBUG_SEVERITY_NOTIFICATION: logging.DEBUG,
    GL.GL_DEBUG_SEVERITY_LOW: logging.INFO,
    GL.GL_DEBUG_SEVERITY_MEDIUM: logging.WARNING,
    GL.GL_DEBUG_SEVERITY_HIGH: logging.ERROR,
}


def _debug_callback(source, type, id, severity, length, message, userParam, *a, **k):
    log_level = _levels.get(severity, logging.ERROR)
    severity = _severity.get(severity, hex(severity))
    logger.log(
        log_level,
        f"[{severity}]" + message.decode("utf-8", errors="ignore"),
        extra={
            "severity": _severity.get(severity, "UNKNOWN"),
        },
    )


_CALLBACK = GL.GLDEBUGPROC(_debug_callback)


def start_opengl_logger(severity=GL.GL_DONT_CARE):
    """
    Start the OpenGL logger, should be called after `pygame.set_mode`.
    :param severity: GL_DEBUG_SEVERITY_* enum or GL_DONT_CARE.
    """
    GL.glEnable(GL.GL_DEBUG_OUTPUT)
    # for synchronous immediate messages (helpful while debugging)
    GL.glEnable(GL.GL_DEBUG_OUTPUT_SYNCHRONOUS)
    if not GL.glDebugMessageCallback:
        logger.critical("Failed to start OpenGL logger, called too soon?")
        return
    GL.glDebugMessageCallback(_CALLBACK, None)
    # optionally control which messages to receive:
    GL.glDebugMessageControl(
        GL.GL_DONT_CARE, GL.GL_DONT_CARE, severity or GL.GL_DONT_CARE, 0, None, True
    )
