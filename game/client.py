import asyncio
import json
from collections import deque


class Client:
    """Class to manage network connection between Player and remote client"""

    def __init__(self, websocket):
        self._websocket = websocket
        self.msg_queue = deque()
        self.is_testing = False

    async def handle_msgs(self, is_complete):
        """Asynchronously receives incoming messages for the lifetime of a single client and forwards them to msg_queue.
        This method must be running for any other methods on this class to work.
        All messages placed in queue are dicts. Continues receiving messages until is_complete is True"""
        
        if self.is_testing:
            # don't loop infinitely
            async for message in self._websocket:
                self.msg_queue.append(json.loads(message))

        else:
            while not is_complete:
                async for message in self._websocket:
                    self.msg_queue.append(json.loads(message))

    async def send_msg(self, msg, msg_type):
        """Public method to send generic message (msg) of type msg_type"""
        
        await self._send_msg({
            'type': msg_type,
            'payload': msg
        })

    async def _send_msg(self, msg):
        """Accepts a dictionary and sends a JSON string"""
        
        await self._websocket.send(json.dumps(msg))

    def get_msg(self):
        """Checks message queue and returns the oldest message in its entirety, else returns False."""
        
        try:
            msg = self.msg_queue.popleft()
            return msg
        except IndexError:
            return False

    def get_msg_by_type(self, msg_type):
        """Checks message queue and discards messages until finding one matching the msg_type, then returns.
        If no message is found returns False"""
        
        try:
            msg = None
            while not msg:
                msg = self.msg_queue.popleft()
                if msg['type'] != msg_type:
                    msg = None
            return msg
        except IndexError:
            return False

    async def wait_for_msg(self, msg_type):
        """Listens to queue until a message of type msg_type arrives, then returns payload"""
        
        while True:
            msg = self.get_msg_by_type(msg_type)
            if msg:
                return msg['payload']
            else:
                await asyncio.sleep(0.1)
