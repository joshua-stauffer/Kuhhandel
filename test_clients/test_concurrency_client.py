import asyncio
import datetime
import json
import websockets
from uuid import uuid4
import random

animal_names = ['rooster', 'duck', 'cat', 'dog', 'sheep', 'goat', 'donkey', 'pig', 'cow', 'horse']

def test_concurrent_games(num_games=10):
    """Tests concurrency load by spinning up multiple games at once"""
    
    loop = asyncio.get_event_loop()
    start = datetime.datetime.utcnow()
    task_list = []
    for _ in range(num_games * 3):
        name = str(uuid4())
        task = loop.create_task(client(name))
        task_list.append(task)
    fut = asyncio.gather(*task_list)
    loop.run_until_complete(fut)
    return datetime.datetime.utcnow() - start, num_games


async def client(user_id):
    """Network interface for player"""

    uri = 'ws://localhost:9876'
    opponent_list = []
    async with websockets.connect(uri) as websocket:
        async for msg in websocket:
            response = handle_msg(msg, user_id, opponent_list)
            if response:
                await websocket.send(response)


def handle_msg(msg, user_id, opponent_list):
    """Mocks the appropriate client response to queries"""

    msg_dict = json.loads(msg)

    # if this is the first state message, get the list of opponent names
    if not opponent_list and msg_dict['type'] == 'state':
        try:
            for name in msg_dict['payload']['global_state']['players']:
                if name != user_id:
                    opponent_list.append(name)
        except KeyError:
            pass

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
                    'player': random.choice(opponent_list),
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
            return None

        return msg

if __name__ == '__main__':
    time_delta, game_count = test_concurrent_games()
    print(f'Ran {game_count} games in {time_delta}')