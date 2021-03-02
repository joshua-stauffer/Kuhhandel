# Kuhhandel
## The Animal Auction Game
This project is a web implementation of the game [Kuhhandel](http://www.gamecabinet.com/rules/Kuhhandel.html). The larger goal in building this project was to create a framework-free program that relied primarily on the Python standard library. This game in particular interested me for the challenge posed by managing an asynchronous auction, and offered a chance to work on a project incorporating websockets and asyncio. There is a rather austere front end client for basic testing and use, however the primary focus of this project has been the server side code.

### Setup
The game can be played on web browsers by running the server and opening `client/index.html` in three tabs (or potentially on three web browsers across a local network). Dummy players can also be set up by running the three `auto_player_....py` files in test_clients -- starting the server followed by those three auto_players will run the game to completion.

### Running the server and opening the clients (Mac)
- Clone the project and navigate into project directory in terminal
- Create a new virtual environment by running `python3 -m venv env` in the root directory (first time only)
- Start virtual environment with `source env/bin/activate`
- Install project dependency with `pip install -r requirements.txt` (also first time only)
- Start the server with `python server.py`
- Open the `client/index.html` file in three separate tabs of a web browser, and the game will start after the third connects.

### Running the tests
The unittests of this project can be tested by running the following command in the project's root directory: `python3 -m unittest`. In addition, the game can be run end-to-end by starting the server and running the following three commands from the root project directory in three separate terminal tabs (after starting the virtual environment in each tab):
- `python test_clients/auto_player_one.py`
- `python test_clients/auto_player_two.py`
- `python test_clients/auto_player_three.py`
For testing, it is convenient to set the auction timeout to as low as possible - something like 0.001 seconds works well. The auction timeout is passed in as a parameter when the game object is initialized, in `server.py`, and defaults to 15 seconds.