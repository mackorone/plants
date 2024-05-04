#!/usr/bin/env python3

from __future__ import annotations

import abc
import hashlib
import json
import logging
import pathlib
import shutil
from typing import Awaitable, Callable, Dict, Generic, TypeVar

logger: logging.Logger = logging.getLogger(__name__)


class FetchesDisallowedError(Exception):
    pass


TKey = TypeVar("TKey", bound=str)
TValue = TypeVar("TValue")


class Cache(abc.ABC, Generic[TKey, TValue]):
    @abc.abstractmethod
    async def get(self, key: TKey, func: Callable[[TKey], Awaitable[TValue]]) -> TValue:
        raise NotImplementedError()

    @abc.abstractmethod
    def print_summary(self) -> None:
        raise NotImplementedError()


class NoCache(Cache[TKey, TValue]):
    async def get(self, key: TKey, func: Callable[[TKey], Awaitable[TValue]]) -> TValue:
        return await func(key)

    def print_summary(self) -> None:
        pass


class ReadThroughCache(Cache[TKey, TValue]):
    def __init__(
        self,
        cache_dir: pathlib.Path,
        *,
        allow_fetches: bool = True,
        clean_cache_dir: bool = False,
    ) -> None:
        # In-memory cache
        self._cache: Dict[TKey, TValue] = {}

        # On-disk cache
        if cache_dir.exists() and clean_cache_dir:
            shutil.rmtree(cache_dir)
        self._cache_dir: pathlib.Path = cache_dir

        self._allow_fetches: bool = allow_fetches
        self._num_in_memory_cache_hits: int = 0
        self._num_on_disk_cache_hits: int = 0
        self._num_data_fetches: int = 0

    def print_summary(self) -> None:
        width = len(
            str(
                max(
                    self._num_in_memory_cache_hits,
                    self._num_on_disk_cache_hits,
                    self._num_data_fetches,
                )
            )
        )
        logger.info("Cache hit summary")
        for line in [
            f"Mem    {self._num_in_memory_cache_hits:>{width}}",
            f"Disk   {self._num_on_disk_cache_hits:>{width}}",
            f"Fetch  {self._num_data_fetches:>{width}}",
        ]:
            logger.info(f"  {line}")

    async def get(self, key: TKey, func: Callable[[TKey], Awaitable[TValue]]) -> TValue:
        if key in self._cache:
            self._num_in_memory_cache_hits += 1
        else:
            self._cache[key] = await self._read_from_disk(key, func)
        return self._cache[key]

    async def _read_from_disk(
        self, key: TKey, func: Callable[[TKey], Awaitable[TValue]]
    ) -> TValue:
        hashed_url = hashlib.sha256(key.encode()).hexdigest()
        path = self._cache_dir / hashed_url
        if path.exists():
            self._num_on_disk_cache_hits += 1
            with open(path, "r") as f:
                return json.load(f)
        if not self._allow_fetches:
            raise FetchesDisallowedError(key)
        self._num_data_fetches += 1
        data = await func(key)
        path.parent.mkdir(exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f)
        return data
