#!/usr/bin/env python3

from __future__ import annotations

import contextlib
import functools
import itertools
import logging
from types import TracebackType
from typing import (
    Awaitable,
    Callable,
    Iterator,
    Optional,
    ParamSpec,
    Type,
    TypeVar,
)

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
    """
    Retry a function.

    Usage:

        with retry(func, num_attempts=3, sleep_seconds=1) as wrapper:
            await wrapper(...)
    """
    assert num_attempts >= 2
    assert sleep_seconds > 0

    @functools.wraps(func)
    async def wrapper(*args: TParams.args, **kwargs: TParams.kwargs) -> TReturn:
        for i in itertools.count():
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if i == num_attempts - 1:
                    raise
                await _log_exception_and_sleep(
                    exception=e,
                    sleep_seconds=sleep_seconds,
                    num_remaining=num_attempts - 1 - i,
                )
        assert False

    yield wrapper


class AttemptFactory:
    """
    Retry an arbitrary block of code.

    Usage:

        for attempt in AttemptFactory(num_attempts=3, sleep_seconds=1):
            async with attempt:
                # Do something
    """

    def __init__(self, *, num_attempts: int, sleep_seconds: float) -> None:
        self.num_attempts = num_attempts
        self.sleep_seconds = sleep_seconds
        self.current_attempt = 0
        self.success = False

    def __iter__(self) -> AttemptFactory:
        return self

    def __next__(self) -> Attempt:
        if self.success:
            raise StopIteration
        self.current_attempt += 1
        return Attempt(self)

    def num_remaining(self) -> int:
        assert self.current_attempt <= self.num_attempts
        return self.num_attempts - self.current_attempt


class Attempt:
    def __init__(self, factory: AttemptFactory) -> None:
        self.factory = factory

    async def __aenter__(self) -> Attempt:
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> bool:
        if exc is None:
            self.factory.success = True
            return False
        elif self.factory.num_remaining() == 0:
            return False
        await _log_exception_and_sleep(
            exception=exc,
            sleep_seconds=self.factory.sleep_seconds,
            num_remaining=self.factory.num_remaining(),
        )
        # Suppress the exception
        return True


async def _log_exception_and_sleep(
    exception: BaseException,
    sleep_seconds: float,
    num_remaining: int,
) -> None:
    logger.exception("Caught retryable exception", exc_info=exception)
    logger.info(
        f"Sleeping for {sleep_seconds} second(s), "
        f"{num_remaining} attempt(s) remaining..."
    )
    await sleep(sleep_seconds)
