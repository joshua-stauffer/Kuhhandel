from .wallet import Wallet
from .client import Client

class Player:

    # constructor

    def __init__(self, websocket, uuid):
        self.uuid = uuid
        self.name = 'No name yet'
        self.client = Client(websocket)
        self.cards = []
        self.completed_sets = []
        self.wallet = Wallet()

    # accessors

    def can_trade(self):
        """Returns true if player has incomplete sets"""
        if len(self.cards):
            return True
        return False

    def get_global_state(self):
        """returns a dictionary of player's public-facing data"""
        return {
            'wallet': self.wallet.count,
            'cards': self.cards,
            'completed_sets': self.completed_sets
        }

    def get_score(self):
        """Returns the current score of completed cards"""
        return sum([c.value for c in self.completed_sets]) * len(self.completed_sets)

    def verify_bid(self, bid_value):
        """Confirms that a bid amount is less than the total held in wallet."""
        return bid_value <= self.wallet.total
        
    # mutators -- change object state in some way

    def accept_payment(self, payment):
        """Adds money cards from payment to wallet"""
        self.wallet.accept_payment(payment)

    def add_card(self, card):
        """Adds a card to players cards, and completes a set as necessary"""
        self.cards.append(card)
        # check to see if set is completed
        if self.cards.count(card) == 4:
            self.completed_sets.append(card)
            self.cards = [c for c in self.cards if c != card]

    def get_card_by_name(self, card_name):
        """Obtains a card from card list and returns it, removing it from the list"""
        
        cards_by_name = [c.name for c in self.cards]
        try:
            c_index = cards_by_name.index(card_name)
        except ValueError:
            raise ValueError(f'Nonexistent card name {card_name} given.')
        return self.cards.pop(c_index)

    # IO - methods that provide a wrapper for client object

    def buy_option(self, bid):
        """Gives the auctioneer an opportunity to buy the animal at winning bid.
        Returns True if auctioneer has exercised this option, else False."""

        while msg := self.client.get_msg_by_type('auctioneer-bid'):
            if msg['payload']['amount'] >= bid and self.verify_bid(bid):
                return True
        return False

    async def choose_action(self, can_challenge, can_auction):
        """Informs client app that it is their turn and awaits and returns response"""
        
        if not can_challenge and not can_auction:
            await self.client.send_msg({
                'message': 'You have no moves left: wait for everyone to finish their challenges!'
            }, 'message')
            return 'pass'
        
        elif not can_challenge:
            await self.client.send_msg({
                'message': 'You have no challenges available, so you must auction!'
            }, 'message')
            return 'auction'
        
        elif not can_auction:
            await self.client.send_msg({
                'message': 'There are no cards left to auction, so you must challenge!'
            }, 'message')
            return 'challenge'
        
        else:        
            await self.client.send_msg('Please choose auction or challenge', 'query')
            action = await self.client.wait_for_msg('response')
            if action == 'auction':
                return 'auction'
            elif action == 'challenge':
                return 'challenge'
            else:
                raise Exception(f'Unknown action {action} returned to player {self.uuid}')

    async def create_payment(self, total):
        """Requests money card combination from client and waits for a message containing the correct amount."""
        await self.client.send_msg({
                'message': f'Please select payment cards that total at least {total}'
            }, 'query')
        while True:
            payload = await self.client.wait_for_msg('payment')
            try:
                return self.wallet.create_payment(payload)
            except ValueError:
                await self.client.send_msg(f'You don\'t have those cards! Please select payment cards that total at least {total}', 'query')

    def get_bid(self):
        """Checks to see if player has made a bid"""
        msg = self.client.get_msg_by_type('bid')
        if msg:
            if self.verify_bid(msg['payload']['amount']):
                return msg['payload']
        else:
            return None

    async def get_challenge(self):
        """Sends a message to client asking for challenge response, and then waits for the response"""
        await self.client.send_msg({
            'message': 'Please select the player and card you wish to challenge'
        }, 'query')
        return await self.client.wait_for_msg('challenge')

    async def get_challenge_payment(self):
        """Queries client and returns a Payment"""
        return await self.create_payment(0)

    async def get_name(self):
        await self.client.send_msg('Please enter your username', 'query')
        payload = await self.client.wait_for_msg('username')
        self.name = payload['username']

    async def send_card(self, card):
        """Accepts a card object and sends a message containing the card to client"""
        
        await self.client.send_msg({'name': card.name, 'value': card.value}, 'card')
    
    async def update_state(self, global_state):
        """Updates client with current global game state, plus personal game data"""

        state = {
            'my name': self.name,
            'my wallet': self.wallet.to_dict(),
            'global_state': global_state
        }
        await self.client.send_msg(state, 'state')
