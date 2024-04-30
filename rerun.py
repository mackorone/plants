#!/usr/bin/env python3

import importlib
import logging
from typing import Awaitable, Callable, ParamSpec, TypeVar

logger: logging.Logger = logging.getLogger(__name__)

TParams = ParamSpec("TParams")
TReturn = TypeVar("TReturn")


class IncompatibleFunctionError(Exception):
    pass


async def rerun_interactively(
    func: Callable[TParams, Awaitable[None]],
    *args: TParams.args,
    **kwargs: TParams.kwargs,
) -> None:
    module_name = func.__module__
    function_name = func.__name__
    if module_name == "__main__":
        raise IncompatibleFunctionError(
            "Cannot reload '{function_name}' because it lives in the main module"
        )

    module = None
    while True:
        try:
            if not module:
                module = importlib.import_module(module_name)
            importlib.reload(module)
        except Exception:
            logger.exception(f"Failed to reload module '{module_name}'")
        else:
            try:
                await getattr(module, function_name)(*args, **kwargs)
            except Exception:
                logger.exception(f"Function '{function_name}' raised an exception")
        input("Press ENTER to continue")
