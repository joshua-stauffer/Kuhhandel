import asyncio
import unittest
import json
from uuid import uuid4
from collections import deque
from string import ascii_lowercase
from game.client import Client
from game.player import Player
from game.mock_socket import MockSocket
from game.async_test_helper import run_async

class TestClient(unittest.TestCase):

    def setUp(self):
        self.sock = MockSocket(time_delay=0.1)
        self.player = Player(self.sock, uuid4())
        self.client = self.player.client
        self.client.is_testing = True

    def test_client_exists(self):
        self.assertIsNotNone(self.client)

    def test_handle_msgs(self):
        test_message_one = json.dumps({
            "a": "foo",
            "2": "spam"
        })
        test_message_two = json.dumps({
            "flora": "rose",
            "fauna": "muskrat"
        })
        self.sock.push_to_queue([test_message_one, test_message_two])
        run_async(self.client.handle_msgs, False)

    def test_client_receives_websocket(self):
        self.assertEqual(self.sock, self.client._websocket)

    def test_private_send_msg(self):
        msg = {'type': 'test'}
        run_async(self.client._send_msg, msg)
        sent_msg = self.sock.msg_queue[0]
        decoded_msg = json.loads(sent_msg)
        self.assertEqual(decoded_msg['type'], msg['type'])

    def test_public_send_msg(self):
        msg = 'hi, test message here!'
        msg_type = 'test'
        run_async(self.client.send_msg, msg, msg_type)
        sent_msg = self.sock.msg_queue[0]
        decoded_msg = json.loads(sent_msg)
        self.assertEqual(decoded_msg['type'], msg_type)
        self.assertEqual(decoded_msg['payload'], msg)

    def test_get_msg_returns_false_on_index_error(self):
        self.assertFalse(self.client.get_msg())

    def test_get_msg(self):
        msg_dict = {
            "a": "foo",
            "2": "spam"
        }
        msg = json.dumps(msg_dict)
        self.sock.push_to_queue([msg])
        run_async(self.client.handle_msgs, False)
        result = self.client.get_msg()
        self.assertIsNotNone(result)
        self.assertTrue(result)
        self.assertEqual(
            result['a'], msg_dict['a']
        )
        self.assertEqual(
            result['2'], msg_dict['2']
        )

    def test_get_msg_by_type_finds_correct_message(self):
        msgs = [json.dumps({'type': 'test', 'payload': c}) for c in ascii_lowercase]
        msgs.append(json.dumps({'type': 'important', 'payload': '!'}))
        self.sock.push_to_queue(msgs)
        run_async(self.client.handle_msgs, False)
        result = self.client.get_msg_by_type('important')
        self.assertTrue(result)
        self.assertEqual(
            result['type'], 'important'
        )
        self.assertEqual(
            result['payload'], '!'
        )

    def test_get_msg_by_type_returns_false_when_msg_is_missing(self):
        msgs = [json.dumps({'type': 'test', 'payload': c}) for c in ascii_lowercase]
        self.sock.push_to_queue(msgs)
        run_async(self.client.handle_msgs, False)
        result = self.client.get_msg_by_type('important')
        self.assertFalse(result)

    def test_get_msg_by_type_returns_false_on_empty_queue(self):
        run_async(self.client.handle_msgs, False)
        result = self.client.get_msg_by_type('any')
        self.assertFalse(result)       

    def test_wait_for_message(self):
        pass

if __name__ == "__main__":
    unittest.main()