import asyncio
import json
import logging
import websockets
from uuid import uuid4
from game.game import Game
from game.player import Player

game = Game(auction_timeout=0.001)

async def lobby(websocket, path):
    player = Player(websocket, str(uuid4()))
    task = asyncio.create_task(player.client.handle_msgs(game.is_complete))
    await player.get_name()
    game.add_player(player)

    # add message listener
    await player.client.send_msg('You\'ve been successfully added to the game! The game will start when enough players join', 'message')
    
    # when this function returns, the player websocket is closed
    while not game.is_complete:
        await asyncio.sleep(1)

start_server = websockets.serve(lobby, 'localhost', 9876)

loop = asyncio.get_event_loop()
loop.run_until_complete(start_server)
print('started server at port 9876')
loop.create_task(game.run())
loop.run_forever()
