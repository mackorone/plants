#!/usr/bin/env python3

import subprocess
from typing import Tuple

from .external import external


class SubprocessError(Exception):
    pass


class SubprocessUtils:
    @classmethod
    def run(
        cls,
        args: Tuple[str, ...],
        *,
        raise_if_nonzero: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        result = cls._run(args)
        # With subprocess.run(check=True), CalledProcessError does not include
        # stderr in the exception message, which makes debugging difficult.
        # Thus we define our own differently-named flag and raise our own
        # exception that *does* include stderr in the exception message.
        if result.returncode != 0 and raise_if_nonzero:
            raise SubprocessError(
                f"{result.args} returned {result.returncode}: {repr(result.stderr)}"
            )
        return result

    @classmethod
    @external
    def _run(
        cls,
        args: Tuple[str, ...],
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            args=args,
            capture_output=True,
            text=True,
        )
