#!/usr/bin/env python3

import enum
import logging
import re
import sys
import traceback
from typing import Optional

from .environment import Environment

logger: logging.Logger = logging.getLogger(__name__)


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

        self.default_time_format = "%Y-%m-%d %H:%M:%S"
        self.default_msec_format = "%s.%03d"

        super().__init__(
            fmt=(
                Color.LIGHT_BLUE.get_code()
                + "(%(asctime)s) "
                + Color.RESET.get_code()
                + "%(level_color)s"
                + "[%(levelname)s] "
                + Color.RESET.get_code()
                + "%(message)s"
            )
        )

    def format(self, record: logging.LogRecord) -> str:
        level_color = self._get_level_color(record.levelno).get_code()
        setattr(record, "level_color", level_color)
        message = super().format(record)
        if self._escape_newlines:
            message = message.replace("\n", "\\n")
        if not self._colorize:
            message = re.sub("\u001b\\[[0-9]{1,2}m", "", message)
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


def configure_logging(
    *,
    level: int = logging.INFO,
    colorize: Optional[bool] = None,
    escape_newlines: bool = False,
) -> None:
    handler = logging.StreamHandler()
    if colorize is None:
        # Use `any` instead of `or` to prevent surprises due to short circuiting
        colorize = any([handler.stream.isatty(), Environment.is_github_actions()])
    formatter = LogFormatter(colorize=colorize, escape_newlines=escape_newlines)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(level)

    # Install custom exception hook
    sys.excepthook = lambda *args: logger.critical(
        "Unhandled exception\n"
        + "".join(
            traceback.format_exception(
                sys.last_type, sys.last_value, sys.last_traceback
            )
        ).strip()
    )
