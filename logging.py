#!/usr/bin/env python3

import enum
import logging


class Color(enum.Enum):
    RESET = 0
    LIGHT_RED = 91
    LIGHT_GREEN = 92
    LIGHT_YELLOW = 93
    LIGHT_BLUE = 94
    TURQUOISE = 96

    def get_code(self) -> str:
        return f"\u001b[{self.value}m"


class LogFormatter(logging.Formatter):
    def __init__(self, *, colorful_output: bool, escape_newlines: bool) -> None:
        self._colorful_output = colorful_output
        self._escape_newlines = escape_newlines

        asctime_color = ""
        if self._colorful_output:
            asctime_color = Color.LIGHT_BLUE.get_code()
        self.default_time_format = "%Y-%m-%d %H:%M:%S"
        self.default_msec_format = "%s.%03d"

        super().__init__(
            fmt=(
                asctime_color
                + "(%(asctime)s) "
                + Color.RESET.get_code()
                + "%(level_color)s"
                + "[%(levelname)s] "
                + Color.RESET.get_code()
                + "%(message)s"
            )
        )

    def format(self, record: logging.LogRecord) -> str:
        level_color = ""
        if self._colorful_output:
            level_color = self._get_level_color(record.levelno).get_code()
        setattr(record, "level_color", level_color)
        message = super().format(record)
        if self._escape_newlines:
            message = message.replace("\n", "\\n")
        return message

    @classmethod
    def _get_level_color(cls, level: int) -> Color:
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
    colorful_output: bool = True,
    escape_newlines: bool = False,
) -> None:
    formatter = LogFormatter(
        colorful_output=colorful_output, escape_newlines=escape_newlines
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(level)
