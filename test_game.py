import asyncio
import unittest
from uuid import uuid4
from game.game import Game
from game.mock_socket import MockSocket
from game.player import Player
from game.deck import make_deck
from game.async_test_helper import run_async

class TestGame(unittest.TestCase):

    def setUp(self):
        self.game = Game()
        self.sock = MockSocket(time_delay=0.1)
        p = Player(self.sock, uuid4())
        self.game.add_player(p)

    def test_add_player(self):
        self.assertEqual(len(self.game.players), 1)

    def test_remove_player(self):
        self.game.remove_player(self.sock)
        self.assertEqual(len(self.game.players), 0)

    def test_deck_exists(self):
        self.assertIsNotNone(self.game.deck)  

    def test_push_all(self):
        pass

    def test_flip_card(self):
        card = run_async(self.game.flip_card)
        self.assertIsNotNone(card)
        self.assertIsNotNone(card.name)
        self.assertIsNotNone(card.value)

    def test_run(self):
        pass

    def test_flip_card_removes_card_from_deck(self):
        start_count = len(self.game.deck)
        for _ in range(15):
            run_async(self.game.flip_card)
        end_count = len(self.game.deck)
        self.assertNotEqual(start_count, end_count)
        self.assertEqual(start_count, end_count+15)

    def test_flip_card_eventually_empties_deck(self):
        card = True
        while card:
            card = run_async(self.game.flip_card)
        self.assertEqual(len(self.game.deck), 0)

    def test_players_can_trade(self):
        # sufficient to test the can_trade method on Player object
        pass

    def test_game_is_ready_to_start_when_enough_players_join(self):
        for _ in range(2):
            p = Player(MockSocket(time_delay=0.1), uuid4())
            self.game.add_player(p)
        self.assertTrue(self.game.is_ready)

    def test_play(self):
        pass

    def test_update_global_state(self):
        self.assertIsNone(self.game.global_state)
        self.game.update_global_state()
        self.assertIsNotNone(self.game.global_state)

    def test_auction(self):
        pass

    def test_challenge(self):
        pass

    def test_has_legal_challenge_with_single_player(self):
        self.assertEqual(
            self.game.has_legal_challenge(self.game.players[0]),
            []
        )

    def test_has_legal_challenge_with_two_players(self):
        new_player = Player(MockSocket(time_delay=0.1), uuid4())
        self.game.add_player(new_player)
        horses = [c for c in make_deck() if c.name == 'horse']
        for p in self.game.players:
            for _ in range(2):
                p.cards.append(horses.pop())
        self.assertEqual(
            self.game.has_legal_challenge(self.game.players[0]),
            [new_player]
        )

    def test_verify_challenge_with_two_cards_each(self):
        new_player = Player(MockSocket(time_delay=0.1), uuid4())
        self.game.add_player(new_player)
        horses = [c for c in make_deck() if c.name == 'horse']
        for p in self.game.players:
            for _ in range(2):
                p.cards.append(horses.pop())
        how_many_cards_can_be_challenged = self.game.verify_challenge(
            self.game.players[0],
            self.game.players[1],
            'horse'
        )
        self.assertEqual(
            how_many_cards_can_be_challenged, 2
        )
    
    def test_verify_challenge_with_one_card_each(self):
        new_player = Player(MockSocket(time_delay=0.1), uuid4())
        self.game.add_player(new_player)
        horses = [c for c in make_deck() if c.name == 'horse']
        for p in self.game.players:
            for _ in range(1):
                p.cards.append(horses.pop())
        how_many_cards_can_be_challenged = self.game.verify_challenge(
            self.game.players[0],
            self.game.players[1],
            'horse'
        )
        self.assertEqual(
            how_many_cards_can_be_challenged, 1
        )

    def test_verify_challenge_with_no_common_cards(self):
        new_player = Player(MockSocket(time_delay=0.1), uuid4())
        self.game.add_player(new_player)
        horses = [c for c in make_deck() if c.name == 'horse']
        dogs = [c for c in make_deck() if c.name == 'dog']
        self.game.players[0].cards.append(horses.pop())
        self.game.players[1].cards.append(dogs.pop())

        horse_challenge = self.game.verify_challenge(
            self.game.players[0],
            self.game.players[1],
            'horse'
        )
        dog_challenge = self.game.verify_challenge(
            self.game.players[0],
            self.game.players[1],
            'dog'
        )
        another_animal_challenge = self.game.verify_challenge(
            self.game.players[0],
            self.game.players[1],
            'cow'
        )
        self.assertFalse(horse_challenge)
        self.assertFalse(dog_challenge)
        self.assertFalse(another_animal_challenge)


if __name__ == '__main__':
    unittest.main()