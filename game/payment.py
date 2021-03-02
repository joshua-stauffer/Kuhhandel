

class Payment:
    """Object to transfer payment from one Wallet to another."""

    def __init__(self, zeros=0, tens=0, twenties=0, fifties=0,
            hundreds=0, twohundreds=0, fivehundreds=0):
        
        self.zeros = zeros
        self.tens = tens
        self.twenties = twenties
        self.fifties = fifties
        self.hundreds = hundreds
        self.twohundreds = twohundreds
        self.fivehundreds = fivehundreds

    @property
    def total(self):
        """Returns the sum of the cards in this Payment"""
        
        return (
            self.tens * 10 + \
            self.twenties * 20 + \
            self.fifties * 50 + \
            self.hundreds * 100 + \
            self.twohundreds * 200 + \
            self.fivehundreds * 500)

    @property
    def count(self):
        """Returns the number of cards in this Payment"""
        
        return sum(
            [self.zeros, self.tens, self.twenties, self.fifties,
            self.hundreds, self.twohundreds, self.fivehundreds]
        )