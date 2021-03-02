import unittest
from game.payment import Payment
from game.wallet import Wallet


class TestPayment(unittest.TestCase):

    def setUp(self):
        self.wallet = Wallet()

    def test_count(self):
        self.assertEqual(self.wallet.count, 7)

    def test_total(self):
        self.assertEqual(self.wallet.total, 100)

    def test_create_payment_equal_to_starting_value(self):
        starting_cash = {
            'zeros': 2,
            'tens': 3,
            'twenties': 1,
            'fifties': 1,
            'hundreds': 0,
            'twohundreds': 0,
            'fivehundreds': 0
        }
        self.wallet.create_payment(starting_cash)
        self.assertEqual(self.wallet.count, 0)
        self.assertEqual(self.wallet.total, 0)

    def test_create_payment_value_error(self):
        with self.assertRaises(ValueError):
            self.wallet.create_payment({'fivehundreds': 1})

    def test_payment_greater_than_starting_value(self):
        big_payment = {
            'zeros': 2,
            'tens': 3,
            'twenties': 1,
            'fifties': 1,
            'hundreds': 1,
            'twohundreds': 0,
            'fivehundreds': 0
        }
        with self.assertRaises(ValueError):
            self.wallet.create_payment(big_payment)

    def test_donkey_played_adds_money_cards(self):
        self.assertEqual(self.wallet.count, 7)
        self.assertEqual(self.wallet.total, 100)
        self.wallet.donkey_played()
        self.assertEqual(self.wallet.count, 8)
        self.assertEqual(self.wallet.total, 150)      
        self.wallet.donkey_played()
        self.assertEqual(self.wallet.count, 9)
        self.assertEqual(self.wallet.total, 250)          
        self.wallet.donkey_played()
        self.assertEqual(self.wallet.count, 10)
        self.assertEqual(self.wallet.total, 450)  
        self.wallet.donkey_played()
        self.assertEqual(self.wallet.count, 11)
        self.assertEqual(self.wallet.total, 950)
        with self.assertRaises(Exception):
            self.wallet.donkey_played()

    def test_accept_payment(self):
        self.assertEqual(self.wallet.count, 7)
        self.assertEqual(self.wallet.total, 100)
        payment = Payment(tens=1, twohundreds=2)
        self.wallet.accept_payment(payment)
        self.assertEqual(self.wallet.count, 10)
        self.assertEqual(self.wallet.total, 510)    

    def test_check_payment(self):
        wrong_total = Payment(fivehundreds=1)
        self.assertFalse(self.wallet.check_payment(wrong_total))
        wrong_count = Payment(zeros=3)

if __name__ == '__main__':
    unittest.main()
