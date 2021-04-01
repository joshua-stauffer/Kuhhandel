
class GameSupervisor:

    def __init__(self, game):
        self.game = game
        self.players = []
        self.open_places = game.num_players

    def add_player(self, player):
        self.players.append(player)

    def reserve_spot(self):
        self.open_places -= 1

    @property
    def needs_players(self):
        return self.open_places > 0