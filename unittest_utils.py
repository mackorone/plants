#!/usr/bin/env python3

from typing import Any, Callable, Sequence, TypeVar, Union
from unittest import TestCase, mock

T = TypeVar("T")


class UnittestUtils:
    @classmethod
    def patch(
        cls,
        test_case: TestCase,
        target: str,
        new_callable: Callable[[], T],
    ) -> T:
        """Convenience for using mock.patch in setUp and asyncSetUp methods"""
        patcher = mock.patch(target, new_callable=new_callable)
        mock_object = patcher.start()
        test_case.addCleanup(patcher.stop)
        return mock_object

    @classmethod
    def side_effect(cls, values: Sequence[Union[T, Exception]]) -> Callable[..., T]:
        """Like side_effect but raises exceptions instead of returning them"""
        call_count: int = 0

        def wrapper(*args: Any, **kwargs: Any) -> T:
            nonlocal call_count
            assert call_count < len(values)
            value = values[call_count]
            call_count += 1
            if isinstance(value, Exception):
                raise value
            return value

        return wrapper
