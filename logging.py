#!/usr/bin/env python3

import enum
import logging
import sys
import traceback
from typing import Optional

from .environment import Environment

logger = logging.getLogger(__name__)


class Color(enum.Enum):
    RESET = 0
    LIGHT_RED = 91
    LIGHT_GREEN = 92
    LIGHT_YELLOW = 93
    LIGHT_BLUE = 94
    LIGHT_PURPLE = 95
    TURQUOISE = 96

    def get_code(self) -> str:
        return f"\u001b[{self.value}m"


class LogFormatter(logging.Formatter):
    def __init__(self, *, colorize: bool, escape_newlines: bool) -> None:
        self._colorize = colorize
        self._escape_newlines = escape_newlines

        asctime_color = ""
        reset_color = ""
        if self._colorize:
            asctime_color = Color.LIGHT_BLUE.get_code()
            reset_color = Color.RESET.get_code()

        self.default_time_format = "%Y-%m-%d %H:%M:%S"
        self.default_msec_format = "%s.%03d"

        super().__init__(
            fmt=(
                asctime_color
                + "(%(asctime)s) "
                + reset_color
                + "%(level_color)s"
                + "[%(levelname)s] "
                + reset_color
                + "%(message)s"
            )
        )

    def format(self, record: logging.LogRecord) -> str:
        level_color = ""
        if self._colorize:
            level_color = self._get_level_color(record.levelno).get_code()
        setattr(record, "level_color", level_color)
        message = super().format(record)
        if self._escape_newlines:
            message = message.replace("\n", "\\n")
        return message

    @classmethod
    def _get_level_color(cls, level: int) -> Color:
        if level >= logging.CRITICAL:
            return Color.LIGHT_PURPLE
        if level >= logging.ERROR:
            return Color.LIGHT_RED
        if level >= logging.WARNING:
            return Color.LIGHT_YELLOW
        if level >= logging.INFO:
            return Color.LIGHT_GREEN
        return Color.TURQUOISE


def configure_root_logger(
    *,
    level: int = logging.INFO,
    colorize: Optional[bool] = None,
    escape_newlines: bool = False,
) -> None:
    handler = logging.StreamHandler()
    if colorize is None:
        colorize = handler.stream.isatty() or Environment.is_github_actions()
    formatter = LogFormatter(colorize=colorize, escape_newlines=escape_newlines)
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(level)

    # Install custom hook via hacky multiline lambda
    sys.excepthook = lambda *args: (
        logger.critical("Unhandled exception"),
        traceback.print_last(),
    )
