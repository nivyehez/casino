import socket
import threading
import random

#_________________Class Card___________________________
class Card:
    def __init__(self, num, kind):
        self.kind = kind
        self.num = num

    def get_num(self):
        return int(self.num)

    def get_card(self):
        return self.symbol() + str(self.kind)

    def symbol(self):   # returns the symbol of the numeric value as string
        if self.num == 11:
            return 'J'
        if self.num == 12:
            return 'Q'
        if self.num == 13:
            return 'K'
        if self.num == 14:
            return 'A'
        return str(self.num)
#______________________________________________________

#_________________Class Dealer_________________________
class Dealer:

    def __init__(self):
        deck = []
        for n in (list(range(2,14))):
            for k in ['c','d','h','s']:
                deck.append(Card(n,k))

        random.shuffle(deck)
        self.deck = deck
        self.prize = 0

    def deal_card(self):
        return self.deck.pop(0)


    def deck_not_empty(self):
        if len(self.deck) > 0:
            return True
        return False
#______________________________________________________

#_________________Game functions START_________________
class Game:
    def __init__(self,client):
        self.client = client
        self.dealer = Dealer()
        self.round_count = 1
        self.player_prize = 0
        self.total_profit = 0
        self.start_Game(client)

    def start_Game(self,client):
        player_card = self.dealer.deal_card()
        dealer_card = self.dealer.deal_card()
        self.client.send(b'request accepted. Starting game:\n  Player Card: '
                    + player_card.get_card().encode())
        while self.dealer.deck_not_empty():
            self.play_round(client)

    def client_comm(self, client, exp):
        msg = client.recv(1024)

    def get_bet(self, client):             # asks the player to send his bet and returns it as int
        client.send(b'send your bet')
        bet = client.recv(1024)
        return bet

    def play_round(self,client):
        bet = self.get_bet(client)




#_________________Game functions END___________________________

#_________________________connections and threads management____________________________
def wait_client():
    s = socket.socket()          # Create a socket object
    host = socket.gethostname()  # Get local machine name
    port = 12345                 # Reserve a port for your service.
    s.bind((host, port))         # Bind to the port

    while True:
        s.listen(5)               # Now wait for client connection.
        client, addr = s.accept()      # Establish connection with client.
        if (threading.active_count() < 3):
            t = threading.Thread(target=Game, args=(client,))# is this legal? can the GC destroy the Game object during its run?
            t.start()
        else:
             client.send("denied".encode())


if __name__ == "__main__":
    wait_client = threading.Thread(wait_client())
    wait_client.start()
#_____________________________________________________________________________________
