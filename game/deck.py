from collections import namedtuple

card = namedtuple('card', ['name', 'value'])
animals = ('rooster', 'duck', 'cat', 'dog', 'sheep', 'goat', 'donkey', 'pig', 'cow', 'horse') * 4
values = (10, 40, 90, 160, 250, 350, 500, 650, 800, 1000) * 4

def make_deck():
    """Returns a deck of 40 KuhHandel Animal Card tuples.
    Each Card has name and value attributes."""
    
    return [
        card(name=name, value=value)
        for name, value in zip(animals, values)
        ]
