import unittest
from game import payment

Payment = payment.Payment

class TestPayment(unittest.TestCase):

    def test_defaults(self):
        test_payment = payment.Payment()
        self.assertEqual(test_payment.count, 0)
        self.assertEqual(test_payment.total, 0)

    def test_zeros(self):
        zero = Payment(zeros=1)
        self.assertEqual(zero.total, 0)
        self.assertEqual(zero.count, 1)

    def test_tens(self):
        ten = Payment(tens=1)
        self.assertEqual(ten.total, 10)
        self.assertEqual(ten.count, 1)

    def test_twenties(self):
        twenty = Payment(twenties=1)
        self.assertEqual(twenty.total, 20)
        self.assertEqual(twenty.count, 1)

    def test_fifties(self):
        fifty = Payment(fifties=1)
        self.assertEqual(fifty.total, 50)
        self.assertEqual(fifty.count, 1)

    def test_hundreds(self):
        hundred = Payment(hundreds=1)
        self.assertEqual(hundred.total, 100)
        self.assertEqual(hundred.count, 1)

    def test_twohundreds(self):
        twohundred = Payment(twohundreds=1)
        self.assertEqual(twohundred.total, 200)
        self.assertEqual(twohundred.count, 1)

    def test_fivehundreds(self):
        fivehundred = Payment(fivehundreds=1)
        self.assertEqual(fivehundred.total, 500)
        self.assertEqual(fivehundred.count, 1)

    def test_count(self):
        many_money = Payment(
            zeros=1,
            tens=1,
            twenties=1,
            fifties=1,
            hundreds=1,
            twohundreds=1,
            fivehundreds=1
        )
        self.assertEqual(many_money.count, 7)

    def test_total(self):
        much_money = Payment(
            zeros=1,
            tens=1,
            twenties=1,
            fifties=1,
            hundreds=1,
            twohundreds=1,
            fivehundreds=1
        )
        total = 0 + 10 + 20 + 50 + 100 + 200 + 500
        self.assertEqual(much_money.total, total)

if __name__ == '__main__':
    unittest.main()
