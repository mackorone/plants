#!/usr/bin/env python3

import enum
import inspect
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
    LIGHT_GRAY = 97

    def get_code(self) -> str:
        return f"\u001b[{self.value}m"

    def __call__(self, text: str) -> str:
        # First remove existing colors, then wrap in new color
        text = re.sub("\u001b\\[[0-9]{1,2}m", "", text)
        return self.get_code() + text + Color.RESET.get_code()


class LogFormatter(logging.Formatter):
    def __init__(
        self, *, colorize: bool, escape_newlines: bool, auto_indent: bool
    ) -> None:
        self._colorize = colorize
        self._escape_newlines = escape_newlines
        self._auto_indent = auto_indent

        self.default_time_format = "%Y-%m-%d %H:%M:%S"
        self.default_msec_format = "%s.%03d"

        super().__init__(
            fmt=(
                Color.LIGHT_BLUE.get_code()
                + "(%(asctime)s)"
                + Color.RESET.get_code()
                + " %(level_color)s"
                + "[%(levelname)s]"
                + Color.RESET.get_code()
                + " %(message)s"
            )
        )

    def format(self, record: logging.LogRecord) -> str:
        if self._auto_indent:
            frames = inspect.getouterframes(inspect.currentframe())
            # Ignore the first eight, logging-related frames. Also ignore the
            # last frame so that cumulative indentation is relative to the first
            # code block, usually just the main method. Start indentation level
            # at zero so that lines immediately within that first code block
            # don't get extra-indented.
            indentation = -1
            for frame in frames[8:-1]:
                # pyre-fixme[16]
                line = frame.code_context[frame.index]
                # Assume that each level of indentation if four spaces
                indentation += line.index(line.lstrip()) // 4
            record.msg = " " * indentation + record.msg

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
    auto_indent: bool = False,
) -> None:
    handler = logging.StreamHandler()
    if colorize is None:
        # Use `any` instead of `or` to prevent surprises due to short circuiting
        colorize = any([handler.stream.isatty(), Environment.is_github_actions()])
    formatter = LogFormatter(
        colorize=colorize, escape_newlines=escape_newlines, auto_indent=auto_indent
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
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
