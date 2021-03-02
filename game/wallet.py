from .payment import Payment

class Wallet:
    """object to track money, and send and receive Payment objects"""

    def __init__(self):
        self.zeros = 2        
        self.tens = 3
        self.twenties = 1
        self.fifties = 1
        self.hundreds = 0
        self.twohundreds = 0
        self.fivehundreds = 0
        self._donkey_count = 0

    @property
    def total(self):
        
        return (
            self.tens * 10 + \
            self.twenties * 20 + \
            self.fifties * 50 + \
            self.hundreds * 100 + \
            self.twohundreds * 200 + \
            self.fivehundreds * 500
        )

    @property
    def count(self):

        return sum(
            [self.zeros, self.tens, self.twenties, self.fifties,
            self.hundreds, self.twohundreds, self.fivehundreds]
        )

    def donkey_played(self):
        """Call each time a donkey card appears to add extra money card"""
        
        if self._donkey_count == 0:
            self.fifties += 1
        elif self._donkey_count == 1:
            self.hundreds += 1
        elif self._donkey_count == 2:
            self.twohundreds += 1
        elif self._donkey_count == 3:
            self.fivehundreds += 1
        else:
            raise Exception('Donkey played too many times')
        self._donkey_count += 1

    def create_payment(self, money_dict):
        """Moves money cards specified in money_dict into a Payment object and returns it. Raises ValueError when trying to spend more money than wallet contains."""
        
        payment = Payment(**money_dict)
        if not self.check_payment(payment):
            raise ValueError('Not enough money cards in wallet for this transaction.')
        self.zeros -= payment.zeros
        self.tens -= payment.tens
        self.twenties -= payment.twenties
        self.fifties -= payment.fifties
        self.hundreds -= payment.hundreds
        self.twohundreds -= payment.twohundreds
        self.fivehundreds -= payment.fivehundreds
        return payment
        
    def accept_payment(self, payment):
        """Moves money from payment object into wallet"""
        
        self.zeros += payment.zeros
        self.tens += payment.tens
        self.twenties += payment.twenties
        self.fifties += payment.fifties
        self.hundreds += payment.hundreds
        self.twohundreds += payment.twohundreds
        self.fivehundreds += payment.fivehundreds

    def check_payment(self, payment):
        """Checks that payment request is available in this wallet and returns bool"""
        
        if self.total < payment.total \
            or self.count < payment.count \
            or self.zeros < payment.zeros \
            or self.tens < payment.tens \
            or self.twenties < payment.twenties \
            or self.fifties < payment.fifties \
            or self.hundreds < payment.hundreds \
            or self.twohundreds < payment.twohundreds \
            or self.fivehundreds < payment.fivehundreds:
            return False
        return True

    def to_dict(self):
        """Returns contents of wallet as dict"""

        return {
            'zeros': self.zeros,
            'tens': self.tens,
            'twenties': self.twenties,
            'fifties': self.fifties,
            'hundreds': self.hundreds,
            'twohundreds': self.twohundreds,
            'fivehundreds': self.fivehundreds
        }
