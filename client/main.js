
const websocket = new WebSocket('ws://127.0.0.1:9876/');
const feed = document.getElementById('feed');

// update feed for all events received
websocket.onmessage = event => {
  const msg = document.createElement('li');
  const msgContent = document.createTextNode(event.data)
  msg.appendChild(msgContent)
  feed.prepend(msg)

  if (event.data.type === 'bid') {
    currentBid.textContent = event.data.payload.bid
  }
}

// name input
const username = document.getElementById('username');
const submitUsername = document.getElementById('name-submit');
submitUsername.onclick = () => {
  websocket.send(JSON.stringify({
    "type": "username",
    "payload": {
      "username": username.value
    }
  }))
}

// Start turn controls
const auctionButton = document.getElementById('auctionButton');
const challengeButton = document.getElementById('challengeButton');
auctionButton.addEventListener('click', () => {
  websocket.send(JSON.stringify({
    "type": "response",
    "payload": "auction"
  }))
})
challengeButton.addEventListener('click', () => {
  websocket.send(JSON.stringify({
    "type": "response",
    "payload": "challenge"
  }))
})

// Auction Controls
const currentBid = document.getElementById('bid');
const bidInput = document.getElementById('bid-input');
const auctionSubmitButton = document.getElementById('auction-submit');
const auctionBuy = document.getElementById('auction-buy');
const auctionBuyPrice = document.getElementById('auction-buy-price');
const placeBid = () => {
  websocket.send(JSON.stringify({
    "type": "bid",
    "payload": {
      "amount": +bidInput.value
    }
  }));
}
auctionSubmitButton.onclick = () => placeBid();
auctionBuy.onclick = () => {
  websocket.send(JSON.stringify({
    "type": "auctioneer-bid",
    "payload": {
      "amount": +auctionBuyPrice.value
    }
  }))
}

// Challenge Controls
const playerToChallenge = document.getElementById('challenge-player');
const cardToChallenge = document.getElementById('challenge-card');
const challengeSubmitButton = document.getElementById('challenge-submit');
const placeChallenge = () => {
  websocket.send(JSON.stringify({
    "type": "challenge",
    "payload": {
      "player": playerToChallenge.value,
      "card": cardToChallenge.value
    }
  }));
}
challengeSubmitButton.onclick = () => placeChallenge();

// Payment Controls
const zeros = document.getElementById('payment-0');
const tens = document.getElementById('payment-10');
const twenties = document.getElementById('payment-20');
const fifties = document.getElementById('payment-50');
const hundreds = document.getElementById('payment-100');
const twohundreds = document.getElementById('payment-200');
const fivehundreds = document.getElementById('payment-500');
const submitPayment = document.getElementById('payment-submit');
const sendPayment = () => {
  const payment = {
    zeros: +zeros.value,
    tens: +tens.value,
    twenties: +twenties.value,
    fifties: +fifties.value,
    hundreds: +hundreds.value,
    twohundreds: +twohundreds.value,
    fivehundreds: +fivehundreds.value
  };
  websocket.send(JSON.stringify({
    "type": "payment",
    "payload": payment
  }));
}
submitPayment.onclick = () => sendPayment();