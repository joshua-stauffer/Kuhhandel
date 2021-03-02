import asyncio
import json
import websockets
from uuid import uuid4
import random

player_names = ['Player Two', 'Player Three']
animal_names = ['rooster', 'duck', 'cat', 'dog', 'sheep', 'goat', 'donkey', 'pig', 'cow', 'horse']

async def client():
    """Network interface for player"""

    uri = 'ws://localhost:9876'
    user_id = 'Player One'
    async with websockets.connect(uri) as websocket:
        async for msg in websocket:
            response = handle_msg(msg, user_id)
            if response:
                await websocket.send(response)


def handle_msg(msg, user_id):
    """Mocks the appropriate client response to queries"""

    msg_dict = json.loads(msg)
    print(f'{user_id} got a message: {msg_dict}')

    if msg_dict['type'] == 'query':

        if msg_dict['payload'] == 'Please choose auction or challenge':
            msg = json.dumps({
                'type': 'response',
                'payload': 'auction'
            })
        elif msg_dict['payload'] == {'message': 'Please select the player and card you wish to challenge'}:
            msg = json.dumps({
                'type': 'challenge',
                'payload': {
                    'player': random.choice(player_names),
                    'card': random.choice(animal_names)
                }
            })
        elif msg_dict['payload'] == {'message': 'Please select payment cards that total at least 0'}:
            msg = json.dumps({
                'type': 'payment',
                'payload': {}
            })
        elif msg_dict['payload'] == 'Please enter your username':
            msg = json.dumps({
                'type': 'username',
                'payload': {'username': user_id}
            })
        else:
            print('not responding to this message')
            return None
        print(f'{user_id} responding to this message with {msg}')

        return msg

asyncio.get_event_loop().run_until_complete(client())