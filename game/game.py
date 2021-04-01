import asyncio
from collections import deque
import datetime
import random
from .deck import make_deck
from game.client import ClientDisconnectError


class Game:
    """Primary class for implementing Kuh Handel gameplay.
    param num_players: Game can't start until this many players join
    param auction_timeout: time (in seconds) players have before auction closes after each bid 
    """
    
    # constructor

    def __init__(self, num_players=3, auction_timeout=15):
        self.players = deque()
        self.deck = make_deck()
        self.num_players = num_players
        self.auction_timeout = auction_timeout
        self.global_state = None
        self.is_ready = False
        self.is_complete = False

    # accessors

    def players_can_trade(self):
        """returns true if any player has a trade available"""

        return len([1 for p in self.players if p.can_trade()]) > 0

    # mutators

    def add_player(self, player):
        """Add a player object to this game"""

        self.players.append(player)
        if len(self.players) == self.num_players:
            self.is_ready = True

    def remove_player(self, ws):
        """Remove player object from this game by passing the websocket connection
        to be removed."""

        player = None
        for p in self.players:
            if p.client._websocket == ws:
                player = p
                break
        if not player:
            raise Exception('couldnt find player to unregister')
        self.players.remove(player)

    async def flip_card(self):
        """returns a random card from the deck. If it is a donkey, updates each player's wallet accordingly and pushes global state"""
        
        if not len(self.deck):
            return False
        card = self.deck.pop(random.randrange(0, len(self.deck)))
        if card.name == 'donkey':
            for player in self.players:
                player.wallet.donkey_played()
            self.update_global_state()
            for player in self.players:
                await player.update_state(self.global_state)
        return card

    def update_global_state(self):
        """update the global state property to latest state"""
        
        self.global_state = {
            'players': [p.name for p in self.players],
            **{p.name: p.get_global_state() for p in self.players},
            'deck_count': len(self.deck)
        }

    # IO - methods that provide a wrapper for the player object

    async def push_all(self, msg):
        """send a message to each player in game"""
        
        #TODO: build this out and refactor all group calls to use it
        raise Exception('Game.push_all is not implemented yet')

    async def _push_bid(self, bid, player):
        """utility auction function to send latest bid to players.
            bid: int
            player: Player object"""

        for p in self.players:
            await p.client.send_msg({
                    'bid': bid,
                    'player': player.name
                }, 'bid')

    # Gameplay - core methods for running the game

    async def run(self):
        """Waits for enough players to join, then starts the game"""
        
        try:
            while not self.is_ready:
                await asyncio.sleep(1)
            await self._play()
        except ClientDisconnectError:
            for p in self.players:
                
                try:
                    await p.client.send_msg(
                        'Sorry, the game has been ended because a player disconnected',
                        'error'
                    )
                    
                except ClientDisconnectError:
                    continue
            self.is_complete = True

    async def _play(self):
        """function implementing main gameplay"""
        
        while len(self.deck) or self.players_can_trade():

            # synchronize game state
            self.update_global_state()
            for p in self.players:
                await p.update_state(self.global_state)

            player = self.players[0]
            
            # player decides to auction card or challenge
            challenge_list = self.has_legal_challenge(player)
            action = await player.choose_action(can_challenge=len(challenge_list), can_auction=len(self.deck))
            
            if action == 'auction':
                card = await self.flip_card()
                for p in self.players:
                    await p.send_card(card)
                auction_results, bidwinner, payee = await self.auction()
                
                # push results to players
                for p in self.players:
                    await p.client.send_msg(auction_results, 'auction-complete')
                
                # clean up after auction
                if not auction_results['bid'] > 0:
                    # no one bid, auctioneer keeps card for free
                    player.add_card(card)
                else:
                    payment = await bidwinner.create_payment(auction_results['bid'])
                    payee.accept_payment(payment)
                    bidwinner.add_card(card)
                    
            elif action == 'challenge':
                await self.challenge(player, challenge_list)

            elif action == 'pass':
                pass

            else:
                raise Exception(f'unknown action {action} passed to game')

            self.players.rotate()

        # find the winner
        score = {p.get_score(): p.name for p in self.players}
        score_list = list(score.keys())
        score_list.sort(reverse=True)
        ordered_score = {score[s]: s for s in score_list}
        for p in self.players:
            await p.client.send_msg(ordered_score, 'game-over')
        
        # allow client socket to close
        self.is_complete = True

    async def auction(self):
        """runs an auction between players[1:], defaulting to players[0] at cost of 0. Auction is open for param timeout seconds after the last successful bid, after which it returns the bidwinner and winning bid amount"""
        
        auction_end = datetime.datetime.utcnow() + datetime.timedelta(seconds=self.auction_timeout)
        bid = 0
        # auctioneer wins the bid, unless someone else bids
        auctioneer = bidholder = self.players[0]
        await self._push_bid(bid, auctioneer)
        # can't slice a deque, so create a list here
        bidding_players = [p for p in self.players if p != auctioneer]
        
        while datetime.datetime.utcnow() < auction_end:
            for player in bidding_players:
                msg = player.get_bid()
                if msg and int(msg['amount']) > bid:
                    bidholder = player
                    auction_end = datetime.datetime.utcnow() + datetime.timedelta(seconds=self.auction_timeout)
                    bid = msg['amount']
                    await self._push_bid(bid, player)
            await asyncio.sleep(0.1)

        # check if auctioneer wishes to buy card at bidwinning price
        if bid > 0:
            will_buy = auctioneer.buy_option(bid)
            if will_buy:
                # bidholder will now receive payment from auctioneer
                payee = bidholder
                bidholder = auctioneer
            else:
                payee = auctioneer
        else:
            payee = None

        return {
            'bidwinner': bidholder.name,
            'bid': bid
        }, bidholder, payee

    async def challenge(self, player, challenge_list):
        """Creates a challenge between two players"""

        # get challenge from player to move
        payload = None
        while not payload:
            payload = await player.get_challenge()
            player_to_challenge = [p for p in self.players if p.name == payload['player']][0]
            if player_to_challenge not in challenge_list:
                await player.client.send_msg({
                    'message': 'You can\'t challenge that person'
                }, 'error')
                payload = None
                continue
            else:
                card_name = payload['card']
                if num_cards_to_challenge := self.verify_challenge(player, player_to_challenge, card_name):
                    break
                else:
                    await player.client.send_msg({
                        'message': 'Your challenge was not valid'
                    }, 'error')
                    payload = None
        
        # put cards in question to the side
        card_holder = []
        for _ in range(num_cards_to_challenge):
            card_holder.append(player.get_card_by_name(card_name))
            card_holder.append(player_to_challenge.get_card_by_name(card_name))

        # get payment from challenging player and update everyone on challenge
        payment1 = await player.get_challenge_payment()
        for p in self.players:
            if num_cards_to_challenge == 2:
                msg = {
                'message': f'{player.name} has challenged {player_to_challenge.name} for all the {card_name}s with {payment1.count} money cards.'
            }
            else:
                msg = {
                'message': f'{player.name} has challenged {player_to_challenge.name} for a {card_name} with {payment1.count} money cards.'
            }
            await p.client.send_msg(msg, 'message')

        # get payment from challenged player
        payment2 = await player_to_challenge.get_challenge_payment()
        for p in self.players:
            await p.client.send_msg({
                'message': f'{player_to_challenge.name} has responded to the challenge with {payment2.count} money cards.'
            }, 'message')

        if payment1.total >= payment2.total:
            buyer = player
        else:
            buyer = player_to_challenge

        # exchange payments
        player.wallet.accept_payment(payment2)
        player_to_challenge.accept_payment(payment1)
        
        for p in self.players:
            await p.client.send_msg({
                'message': f'{buyer.name} has won the challenge!'
            }, 'message')

        for card in card_holder:
            buyer.add_card(card)
    
    def has_legal_challenge(self, player):
        """returns a list of players that player can challenge"""
        
        others = [p for p in self.players if p != player]
        can_challenge = []
        player_cards = set(player.cards)
        for p in others:
            other_cards = set(p.cards)
            if player_cards.intersection(other_cards):
                can_challenge.append(p)
        return can_challenge

    def verify_challenge(self, player, target_player, card_name):
        """Confirms that player can make challenge to player and card in msg dict.
        Returns False if challenge is not valid. In case challenge is valid returns number of cards that are being challenged for."""
        
        # check challenge validity
        if not target_player:
            return False
        player_hand = [c.name for c in player.cards]
        if not card_name in player_hand:
            return False
        target_player_hand = [c.name for c in target_player.cards]
        if not card_name in target_player_hand:
            return False

        #challenge is valid, find how many cards can be challenged
        if player_hand.count(card_name) == 2 and target_player_hand.count(card_name) == 2:
            return 2
        return 1

class GameEndedError(Exception):
    """Error for game ending before completion"""