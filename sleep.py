#!/usr/bin/env python3

import asyncio

from .external import external


@external
async def sleep(seconds: float) -> None:
    await asyncio.sleep(seconds)
