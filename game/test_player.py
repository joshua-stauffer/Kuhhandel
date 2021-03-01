import asyncio
import json
from string import ascii_lowercase
import unittest
from uuid import uuid4
from game.async_test_helper import run_async
from game.deck import make_deck
from game.mock_socket import MockSocket
from game.payment import Payment
from game.player import Player


class TestPlayer(unittest.TestCase):

    def setUp(self):
        self.sock = MockSocket(time_delay=0.1)
        self.player = Player(self.sock, str(uuid4()))
        self.player.client.is_testing = True
        self.deck = make_deck()

    # test accessors

    def test_can_trade_without_cards(self):
        self.assertFalse(self.player.can_trade())

    def test_can_trade_with_cards(self):
        cows = [c for c in self.deck if c.name == 'cow']
        horses = [c for c in self.deck if c.name == 'horse']
        for _ in range(2):
            self.player.add_card(cows.pop())
            self.player.add_card(horses.pop())
        self.assertTrue(self.player.can_trade())

    def test_get_global_state(self):
        state = self.player.get_global_state()
        # expect the default 7 money cards at start
        self.assertEqual(state['wallet'], 7)
        self.assertEqual(state['cards'], [])
        self.assertEqual(state['completed_sets'], [])

    def test_get_score(self):
        cows = [c for c in self.deck if c.name == 'cow']
        cow_value = cows[0].value
        horses = [c for c in self.deck if c.name == 'horse']
        horse_value = horses[0].value
        cows.extend(horses)
        for a in cows:
            self.player.add_card(a)
        self.assertEqual(
            self.player.get_score(),
            (cow_value + horse_value) * 2
        )

    def test_verify_bid(self):
        total = self.player.wallet.total
        self.assertTrue(self.player.verify_bid(total - 20))
        self.assertTrue(self.player.verify_bid(total))
        self.assertFalse(self.player.verify_bid(total + 20))

    # test manipulators

    def test_accept_payment(self):
        payment = Payment(fifties=1)
        total = self.player.wallet.total
        count = self.player.wallet.count
        self.player.accept_payment(payment)
        self.assertEqual(
            self.player.wallet.count,
            count + 1
        )
        self.assertEqual(
            self.player.wallet.total,
            total + 50
        )

    def test_add_card(self):
        self.assertEqual(len(self.player.cards), 0)
        card = self.deck[0]
        self.player.add_card(card)
        self.assertEqual(len(self.player.cards), 1)
        self.assertEqual(card, self.player.cards[0])

    def test_add_card_completes_set(self):
        self.assertEqual(len(self.player.cards), 0)
        self.assertEqual(len(self.player.completed_sets), 0)
        # choose any card to make a set of
        card = self.deck[25]
        for i in range(1,4):
            self.player.add_card(card)
            self.assertEqual(len(self.player.cards), i)
        # add the 4th card, which completes the set
        self.player.add_card(card)
        self.assertEqual(len(self.player.cards), 0)
        self.assertEqual(len(self.player.completed_sets), 1)
        self.assertEqual(self.player.completed_sets[0], card)

    def test_get_card_by_name(self):
        cows = [c for c in self.deck if c.name == 'cow']
        cow_card = cows.pop()
        self.player.add_card(cow_card)
        card = self.player.get_card_by_name('cow')
        self.assertEqual(
            card,
            cow_card
        )

    def test_get_card_by_name_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.player.get_card_by_name('pheonix')

    # test IO

    def test_buy_option_with_no_message(self):
        self.assertFalse(self.player.buy_option(0))

    def test_buy_option_with_message(self):
        msg = json.dumps({
            'type': 'auctioneer-bid',
            'payload': {'amount': 50}
        })
        self.sock.push_to_queue([msg])
        run_async(self.player.client.handle_msgs, False)
        self.assertTrue(self.player.buy_option(50))

    def test_buy_option_with_messages(self):
        msgs = [json.dumps({'type': 'test', 'payload': c}) for c in ascii_lowercase]
        msgs.append(json.dumps({
            'type': 'auctioneer-bid',
            'payload': {'amount': 50}
        }))
        self.sock.push_to_queue(msgs)
        run_async(self.player.client.handle_msgs, False)
        self.assertTrue(self.player.buy_option(50))

    def test_choose_action_sends_request(self):
        response = json.dumps({
            'type': 'response',
            'payload': 'auction'
        })
        self.sock.push_to_queue([response])
        run_async(self.player.client.handle_msgs, False)
        action = run_async(self.player.choose_action, can_challenge=True, can_auction=True)

        msg = json.loads(self.sock.msg_queue.popleft())
        self.assertEqual(msg['type'], 'query')
        self.assertEqual(msg['payload'], 'Please choose auction or challenge')

    def test_choose_action_auction(self):
        response = json.dumps({
            'type': 'response',
            'payload': 'auction'
        })
        self.sock.push_to_queue([response])
        run_async(self.player.client.handle_msgs, False)
        action = run_async(self.player.choose_action, can_challenge=True, can_auction=True)
        self.assertEqual(action, 'auction')


    def test_choose_action_challenge(self):
        response = json.dumps({
            'type': 'response',
            'payload': 'challenge'
        })
        self.sock.push_to_queue([response])
        run_async(self.player.client.handle_msgs, False)
        action = run_async(self.player.choose_action, can_challenge=True, can_auction=True)
        self.assertEqual(action, 'challenge')

    def test_choose_action_error(self):
        response = {
            'type': 'response',
            'payload': 'spam'
        }
        self.sock.add_recv_val(response)
        with self.assertRaises(Exception):
            run_async(self.player.choose_action)

    def test_choose_action_when_cannot_challenge(self):
        action = run_async(self.player.choose_action, can_challenge=False, can_auction=True)
        self.assertEqual(action, 'auction')

    def test_choose_action_when_cannot_auction(self):
        action = run_async(self.player.choose_action, can_challenge=True, can_auction=False)
        self.assertEqual(action, 'challenge')

    def test_choose_action_returns_pass_with_no_moves(self):
        action = run_async(self.player.choose_action, can_challenge=False, can_auction=False)
        self.assertEqual(action, 'pass')

    def test_create_payment_sends_query(self):
        msg = json.dumps({
            'type': 'payment',
            'payload': {'tens': 2}
        })
        self.sock.push_to_queue([msg])
        run_async(self.player.client.handle_msgs, False)
        run_async(self.player.create_payment, 20)
        sent_msg = json.loads(self.sock.outbound_queue.popleft())
        self.assertEqual(
            sent_msg['type'], 'query'
        )

    def test_create_payment_returns_correct_payment(self):
        msg = json.dumps({
            'type': 'payment',
            'payload': {'tens': 2}
        })
        self.sock.push_to_queue([msg])
        run_async(self.player.client.handle_msgs, False)
        payment = run_async(self.player.create_payment, 20)
        expected_payment = Payment(tens=2)
        self.assertEqual(
            payment.total, expected_payment.total
        )
        self.assertEqual(
            payment.count, expected_payment.count
        )

    def test_get_bid_returns_amount_on_valid_bid(self):
        msg = json.dumps({
            'type': 'bid',
            'payload': {'amount': 100}
        })
        self.sock.push_to_queue([msg])
        run_async(self.player.client.handle_msgs, False)
        bid = self.player.get_bid()
        self.assertEqual(
            bid['amount'], 100
        )

    def test_get_bid_returns_none_on_invalid_bid(self):
        self.assertIsNone(self.player.get_bid())

    def test_get_challenge(self):
        msg = json.dumps({
            'type': 'challenge',
            'payload': {'player': 'frodo', 'card': 'the ring'}
        })
        self.sock.push_to_queue([msg])
        run_async(self.player.client.handle_msgs, False)
        payload = run_async(self.player.get_challenge)
        sent_msg = json.loads(self.sock.outbound_queue.popleft())
        self.assertEqual(
            sent_msg['type'], 'query'
        )
        self.assertEqual(
            payload['player'], 'frodo'
        )
        self.assertEqual(
            payload['card'], 'the ring'
        )

    def test_get_challenge_payment_accepts_zero_payment(self):
        msg = json.dumps({
            'type': 'payment',
            'payload': {}
        })
        self.sock.push_to_queue([msg])
        run_async(self.player.client.handle_msgs, False)  
        payment = run_async(self.player.get_challenge_payment)
        self.assertEqual(payment.count, 0)
        self.assertEqual(payment.total, 0)

    def test_get_name(self):
        msg = json.dumps({
            'type': 'username',
            'payload': {'username': 'sauron'}
        })
        self.sock.push_to_queue([msg])
        run_async(self.player.client.handle_msgs, False)
        run_async(self.player.get_name)
        sent_msg = json.loads(self.sock.outbound_queue.popleft())
        self.assertEqual(
            sent_msg['type'], 'query'
        )
        self.assertEqual(
            self.player.name, 'sauron'
        )

    def test_send_card(self):
        card = self.deck[25]
        run_async(self.player.send_card, card)
        sent_msg = json.loads(self.sock.outbound_queue.popleft())
        self.assertEqual(
            sent_msg['type'], 'card'
        )        
        self.assertEqual(
            sent_msg['payload']['name'], card.name
        )
        self.assertEqual(
            sent_msg['payload']['value'], card.value
        )

    def test_update_state(self):
        global_state = {
            'foo': 'spam'
        }
        run_async(self.player.update_state, global_state)
        returned_state = json.loads(self.sock.msg_queue.popleft())
        self.assertEqual(returned_state['type'], 'state')
        self.assertEqual(returned_state['payload']['global_state'], global_state)
        self.assertEqual(returned_state['payload']['my name'], self.player.name)
        self.assertEqual(returned_state['payload']['my wallet'], self.player.wallet.to_dict())
