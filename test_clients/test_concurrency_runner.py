from test_concurrency_client import test_concurrent_games 

def main():
    for game_count in [1, 10, 100, 1000]:
        delta, num_games = test_concurrent_games(game_count)
        time_per_game = delta / num_games
        print(f'Ran {num_games} in {delta}: {time_per_game} per game')

if __name__ == '__main__':
    main()