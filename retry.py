#!/usr/bin/env python3

import contextlib
import functools
import itertools
import logging
from typing import Awaitable, Callable, Iterator, ParamSpec, TypeVar

from .sleep import sleep

logger: logging.Logger = logging.getLogger(__name__)

TParams = ParamSpec("TParams")
TReturn = TypeVar("TReturn")


@contextlib.contextmanager
def retry(
    func: Callable[TParams, Awaitable[TReturn]],
    *,
    num_attempts: int,
    sleep_seconds: float,
) -> Iterator[Callable[TParams, Awaitable[TReturn]]]:
    assert num_attempts >= 2
    assert sleep_seconds > 0

    @functools.wraps(func)
    async def wrapper(*args: TParams.args, **kwargs: TParams.kwargs) -> TReturn:
        for i in itertools.count():
            try:
                return await func(*args, **kwargs)
            except Exception:
                if i == num_attempts - 1:
                    raise
                logger.exception("Caught retryable exception")
                logger.info(
                    f"Sleeping for {sleep_seconds} second(s), "
                    f"{num_attempts - 1 - i} attempt(s) remaining..."
                )
                await sleep(sleep_seconds)
        assert False

    yield wrapper
