import socket
import threading
import random

#_________________Class Card___________________________
class Card:
    def __init__(self, num, kind): #initializing the "card" instantiation
        self.kind = kind
        self.num = num

    #getters
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

    def __init__(self): #initializing the dealer
        deck = [] #setting up the deck as an array of cards
        for n in (list(range(2,14))):
            for k in ['c','d','h','s']:
                deck.append(Card(n,k))

            random.shuffle(deck) #in order to keep it in random order
        self.deck = deck #assign it for the current instantiation
        self.prize = 0 #initializing the player winning pool

    # attempt to deal the first card (first element in the "deck" array
    def deal_card(self):
        try:
            self.deck.pop(0)
        except:
            return False    # deck is empty
    #attempts to discard three cards. returns true if succeeded
    def discard_three(self):
        try:
            self.deck.pop(0)
            self.deck.pop(0)
            self.deck.pop(0)
        except:
            return False #in case the discard failed
    #returns true if the dealer's deck is not empty.
    def deck_not_empty(self):
        if len(self.deck) > 0:
            return True
        return False
#______________________________________________________

#_________________Game functions START_________________
class Game:
    #initializing the game
    def __init__(self, client):
        self.client = client
        self.dealer = Dealer()
        self.player_card = Card()
        self.dealer_card = Card()
        self.round_count = 1
        self.player_prize = 0
        self.total_profit = 0
        self.start_Game(client) #start the game after initializing

    #starting the game
    def start_Game(self, client):
        self.player_card = self.dealer.deal_card() #dealing a card for the player
        self.dealer_card = self.dealer.deal_card() #dealing a card for the dealer
        self.client.send("request accepted. Starting game:\n  Player Card: ".encode()
                            + player_card.get_card().encode()+"\n".encode()) #sending the player his card
        while self.dealer.deck_not_empty():
            self.play_round(client) #as long as the deck is not empty, keep playing the next round

        self.print_finish_game() #finish the game once the deck is empty.

    #communication between client and server.
    def client_comm(self, exp):
        #exp is the expected type of message. The type is sent in the 1st letter of the msg. avalable types:
        #'s' = status
        #'b' = bet
        #'o' = war options. The next char can be 'w' or 'f' ( war or forfeit)
        #'q' = quit
        msg = self.client.recv(1024).decode() # get the message from client
        #if the player chose to view his status
        while( msg[0] == 's' ):
            self.send_status()
            msg = self.client.recv(1024).decode()  # get the message from client
        #if the player chose to quit
        if( msg[0] == 'q'):
            self.quit()
        #if the player chose an invalid option
        while( exp != msg[0]):
            self.request_msg_again()
            msg = self.client.recv(1024).decode()  # get the message from client
        #handle one of the expected responses
        if( exp == msg[0] ):
            #in case the player chose to bet
            if( exp == 'b' ):
                bet = msg[1: end]
                return int(bet)
            #in case the player chose a war option (forfeit or go to war)
            if( exp == 'o' ):
                return msg[1]   # the second char will have to be 'w' or 'f'. It is a part of the protocol
    #quit the game
    def quit(self):
        self.client.send("The game has ended on round: ".encode() + self.round_count.encode() + "!\n".encode()
                            + "The player has quit.\n".encode() + self.print_player_profit()
                         + "Thanks for playing.\n".encode()) #print the game status
        close(self.client)  # close socket
        sys.exit()          # close current thread
    #print the player profit
    def print_player_profit(self):
        if( self.player_prize >= 0 ):
            return "Player won: ".encode() + self.player_prize.encode() + "$\n".encode()

        return "Player lost: ".encode() + abs(self.player_prize).encode() + "$\n".encode()
    #in case the player picked chose the wrong option
    def request_msg_again(self):
        self.client.send("Invalid value. please try again\n".encode())
    #in case the player wanted to view the status of the game
    def sendStatus(self):
        self.client.send("Current round: ".encode() + self.round_count.encode() + "\n".encode()
                         + "Player won: ".encode() + self.player_prize.encode()+"\n".encode())

    # asks the player to send his bet and returns it as int
    def get_bet(self):
        client.send("send your bet\n".encode())
        return self.client_comm(self, "b")
    #plays the round
    def play_round(self):
        bet = self.get_bet(client)

        if( calc_winner == "player" ):
            self.player_prize += bet
            self.client.send("The results of round ".encode() + self.round_count.encode() + ":\n".encode()
                             + "Player won: ".encode() + bet.encode() + "$\n"
                             + "Player's card: ".encode() + self.player_card.get_card().encode()
                             + "Dealer's card: ".encode() + self.dealer_card.get_card().encode()+"\n".encode())

        if ( calc_winner == "dealer" ):
            self.player_prize -= bet
            self.client.send("The results of round ".encode() + self.round_count.encode() + ":\n".encode()
                             + "Dealer won: ".encode() + bet.encode() + "$\n"
                             + "Dealer's card: ".encode() + self.dealer_card.get_card().encode() + "\n".encode()
                             + "Player's card: ".encode() + self.player_card.get_card().encode()+"\n".encode())

        if( calc_winner == "tie" ):
            self.client.send("The results of round ".encode() + self.round_count.encode() + "is a tie!\n".encode()
                             + "Dealer's card: ".encode() + self.dealer_card.get_card().encode() + "\n".encode()
                             + "Player's card: ".encode() + self.player_card.get_card().encode()
                             + "The bet: ".encode() + bet.encode() + "$\n".encode()
                             + "Do you wish to surrender or go to war?".encode()+"\n".encode())
            #in case the player chose to go to war
            if( self.client_comm("o") == "w"):
                if( self.dealer.discard_three() == False ):   # if discard failed (deck is empty), end game.
                    self.finish_game()
            

    #calculates the winner based on the value of the cards
    def calc_winner(self):
        if(self.player_card.get_num() > self.dealer_card.get_num()):
            return "player"
        if (self.player_card.get_num() < self.dealer_card.get_num()):
            return "dealer"

        return "tie"

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
            t = threading.Thread(target=Game, args=(client,))
            t.start()
        else:
             client.send("denied\n".encode())


if __name__ == "__main__":
    wait_client = threading.Thread(wait_client())
    wait_client.start()
#_____________________________________________________________________________________
