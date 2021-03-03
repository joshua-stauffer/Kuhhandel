import asyncio
import json
import websockets
from uuid import uuid4
from game.game import Game
from game.player import Player


current_games = []

def main():
    """Creates and destroys the event loop and server"""

    start_server = websockets.serve(lobby, 'localhost', 9876)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server)
    print('started server at port 9876')
    loop.create_task(cleanup_games())
    try:
        loop.run_forever()
    except Exception as e:
        print(f'shutting down server for exception {e}')
    except KeyboardInterrupt:
        print('shutting down server manually')
    tasks = asyncio.all_tasks(loop=loop)
    for t in tasks:
        t.cancel()
    group = asyncio.gather(*tasks, return_exceptions=True)
    loop.run_until_complete(group)
    loop.close()
    print('Server stopped')

def get_game():
    """Returns a game with open spots"""

    if not len(current_games) or current_games[-1].is_ready:
        game = Game(auction_timeout=15)
        current_games.append(game)
        loop = asyncio.get_running_loop()
        asyncio.create_task(game.run())
        return game
    else:
        #TODO: autocancel a game if a client disconnects
        return current_games[-1]

async def lobby(websocket, path):
    """Entry point for a client to join game"""

    game = get_game()
    player = Player(websocket, str(uuid4()))
    sock_handler = asyncio.create_task(player.client.handle_msgs(game.is_complete))
    await player.get_name()
    game.add_player(player)
    await player.client.send_msg(
        'You\'ve been successfully added to the game! The game will start when enough players join',
        'message'
    )
    
    # when this function returns, the player websocket is closed
    while not game.is_complete:
        await asyncio.sleep(10)

async def cleanup_games():
    """Check currently running games for completed games and remove them"""

    while True:
        for game in current_games:
            if game.is_complete:
                current_games.remove(game)
        await asyncio.sleep(60)


if __name__ == '__main__':
    main()
