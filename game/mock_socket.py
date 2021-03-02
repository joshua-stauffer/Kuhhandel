import asyncio
from collections import deque
import json

class MockSocket:
    """Returns an object which mocks asynchronous network calls"""

    def __init__(self, return_val=None, time_delay=1):
        self.outbound_queue = deque()
        self.inbound_queue = deque()
        self.return_val = json.dumps(return_val)
        self.time_delay = time_delay

    def __aiter__(self):
        self.iqueue = iter(self.inbound_queue)
        return self

    async def __anext__(self):
        try:
            return next(self.iqueue)
        except StopIteration:
            raise StopAsyncIteration

    @property
    def msg_queue(self):
        return self.outbound_queue

    async def send(self, msg):
        """mocks async network call"""

        await asyncio.sleep(self.time_delay)
        self.msg_queue.append(msg)

    async def recv(self):
        """mocks async network return by returning
        val saved during init"""

        await asyncio.sleep(self.time_delay)
        return self.return_val

    def add_recv_val(self, val):
        """Add a value to return from recv if object is already initialized"""
        
        self.return_val = json.dumps(val)

    def push_to_queue(self, iterable):
        """Accepts any iterable and adds contents to the queue"""
        
        self.inbound_queue.extend(iterable)
