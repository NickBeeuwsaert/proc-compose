import asyncio
import enum
from functools import cached_property
from typing import AsyncIterator, Iterable


class MergeTaskState(enum.Enum):
    DRAINING = enum.auto()
    FINISHED = enum.auto()


class merge:
    def __init__(self, *aiters: Iterable[AsyncIterator]):
        self._aiters = aiters

    @cached_property
    def _queue(self):
        return asyncio.Queue(1)

    async def _drain(self, aiter):
        async for item in aiter:
            await self._queue.put((MergeTaskState.DRAINING, item))
        await self._queue.put((MergeTaskState.FINISHED, None))

    async def __aiter__(self):
        finished = 0
        for iterable in self._aiters:
            asyncio.create_task(self._drain(iterable))

        while finished < len(self._aiters):
            state, value = await self._queue.get()
            if state == MergeTaskState.FINISHED:
                finished += 1
            else:
                yield value
