import unittest
from game import deck

class TestDeck(unittest.TestCase):

    def setUp(self):
        self.deck = deck.make_deck()

    def test_card_count(self):
        self.assertEqual(len(self.deck), 44)
    
    def test_card_names(self):
        name_set = set([card.name for card in self.deck])
        self.assertEqual(len(name_set), 11)

    def test_card_values(self):
        value_set = set([card.value for card in self.deck])
        self.assertEqual(len(value_set), 11)

if __name__ == '__main__':
    unittest.main()