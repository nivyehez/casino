import socket
import threading
import random
import sys
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

#_________________Class Dealer________________________________________________________
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
        try:
            return self.deck.pop(0)
        except:
            return False    # deck is empty

    def discard_three(self):
        try:
            self.deck.pop(0)
            self.deck.pop(0)
            self.deck.pop(0)
        except:
            return False

    def deck_not_empty(self):
        if len(self.deck) > 0:
            return True
        return False
#_____________________________________________________________________________________________

#_________________Game class START_________________________________________________
class Game:
    def __init__(self, client):
        self.client = client
        self.dealer = Dealer()
        self.round_count = 1
        self.player_prize = 0
        self.start_Game()

    def start_Game(self):
        self.player_card = self.dealer.deal_card()
        self.dealer_card = self.dealer.deal_card()
        self.client.send("!request accepted. Starting game:\n  Player Card: ".encode()
                        + self.player_card.get_card().encode() +'\n'.encode())
        while self.dealer.deck_not_empty():
            self.play_round()
            self.player_card = self.dealer.deal_card()
            self.dealer_card = self.dealer.deal_card()

        self.print_finish_game()
        self.finish_game()

    def client_comm(self, exp):
        #exp is the expected type of message. The type is sent in the 1st letter of the msg. avalable types:
        #'s' = status
        #'b' = bet
        #'o' = war options. The next char can be 'w' or 'f' ( war or forfeit)
        #'q' = quit
        #'a' = answer. 'y' for yes 'n' for no

        msg = ''
        while msg == '':
            msg = self.client.recv(1024).decode() # get the message from client
        print("msg: " + msg + '\n')

        while( exp != msg[0]):
            if( msg[0] == 'q' ):
                self.quit()
            else:
                if( msg[0] == 's'):
                    self.send_status()
                else:
                    self.request_msg_again()
            msg = self.client.recv(1024).decode()  # get the message from client

        if( exp == "a"):
            return msg[1]

        if( exp == msg[0] ):
            if( exp == 'b' ):
                bet = msg[1: len(msg)]
                return int(bet)

            if( exp == 'o' ):
                return msg[1]   # the second char will have to be 'w' or 'f'. It is a part of the protocol

    def send_status(self):
        self.client.send("!Current round: ".encode() + str(self.round_count).encode() + "\n".encode()
                         + "Player won: ".encode() + str(self.player_prize).encode())

    def quit(self):
        self.client.send("!The game has ended on round: ".encode() + str(self.round_count).encode() + "!\n".encode()
                            + "The player has quit.\n".encode() + self.print_player_profit()
                            + "Thanks for playing.".encode())
        self.client.close()  # close socket
        sys.exit()          # close current thread

    def print_player_profit(self):
        if( self.player_prize >= 0 ):
            return "!Player won: ".encode() + str(self.player_prize).encode() + "$\n".encode()

        return "!Player lost: ".encode() + str(abs(self.player_prize)).encode() + "$\n".encode()

    def request_msg_again(self):
        self.client.send("?Invalid value. please try again".encode())

    def sendStatus(self):
        self.client.send("!Current round: ".encode() + self.round_count.encode() + "\n".encode()
                         + "Player won: ".encode() + self.player_prize.encode() + '\n'.encode())


    def get_bet(self):              # asks the player to send his bet and returns it as int
        self.client.send("?send your bet".encode() + '\n'.encode())
        return self.client_comm("b")

    def play_round(self):

        self.round_count += 1
        bet = self.get_bet()

        if( self.calc_winner() == "player" ):
            self.player_prize += bet
            self.client.send("!The results of round ".encode() + str(self.round_count).encode() + ":\n".encode()
                             + "Player won: ".encode() + str(bet).encode() + "$\n".encode()
                             + "Player's card: ".encode() + self.player_card.get_card().encode() + "\n".encode()
                             + "Dealer's card: ".encode() + self.dealer_card.get_card().encode() + '\n'.encode())

            return #start next round

        if ( self.calc_winner() == "dealer" ):
            self.player_prize -= bet
            self.client.send("!The results of round ".encode() + str(self.round_count).encode() + ":\n".encode()
                             + "Dealer won: ".encode() + str(bet).encode() + "$\n".encode()
                             + "Dealer's card: ".encode() + self.dealer_card.get_card().encode() + "\n".encode()
                             + "Player's card: ".encode() + self.player_card.get_card().encode() + "\n".encode())

            return # start next round

        if( self.calc_winner() == "tie" ):

            self.client.send("?The results of round ".encode() + str(self.round_count).encode() + " is a tie!\n".encode()
                             + "Dealer's card: ".encode() + self.dealer_card.get_card().encode() + "\n".encode()
                             + "Player's card: ".encode() + self.player_card.get_card().encode() + "\n".encode()
                             + "The bet: ".encode() + str(bet).encode() + "$\n".encode()
                             + "Do you wish to surrender or go to war?".encode() + "\n".encode())

            if( self.client_comm("o") == "w"):

                if( self.dealer.discard_three() == False ):   # if discard failed (deck is empty), end game.
                    self.finish_game()

                self.client.send("?Round ".encode() + str(self.round_count).encode() + " tie breaker:\n".encode()
                                 + "Going to war! \n 3 cards were discarded.\n".encode())

                self.player_card = self.dealer.deal_card()
                self.dealer_card = self.dealer.deal_card()

                if( self.dealer_card == False ):              # if deal card failed (deck is empty), end game.
                    self.finish_game()

                if( self.calc_winner() == "player" ):
                    self.player_prize += bet
                    self.client.send("!Original bet: ".encode() + str(bet).encode() + "$\n".encode()
                                     + "New bet: ".encode() + str(bet*2).encode() + "$\n".encode()
                                     + "Dealer's card: ".encode() + self.dealer_card.get_card().encode() + "\n".encode()
                                     + "Player's card: ".encode() + self.player_card.get_card().encode() + "\n".encode()
                                     + "Player won: ".encode() + str(bet).encode() + "$\n".encode())
                    return # start next round

                if( self.calc_winner() == "dealer" ):
                    self.player_prize -= bet*2
                    self.client.send("!Original bet: ".encode() + str(bet).encode() + "$\n".encode()
                                     + "New bet: ".encode() + str(bet * 2).encode() + "$\n".encode()
                                     + "Dealer's card: ".encode() + self.dealer_card.get_card().encode() + "\n".encode()
                                     + "Player's card: ".encode() + self.player_card.get_card().encode() + "\n".encode()
                                     + "Dealer won: ".encode() + str(2*bet).encode() + "$\n".encode())
                    return  # start next round

                if( self.calc_winner() == "tie" ):
                    self.player_prize += 2*bet
                    self.client.send("!Original bet: ".encode() + str(bet).encode() + "$\n".encode()
                                     + "New bet: ".encode() + str(bet * 2).encode() + "$\n".encode()
                                     + "Dealer's card: ".encode() + self.dealer_card.get_card().encode() + "\n".encode()
                                     + "Player's card: ".encode() + self.player_card.get_card().encode() + "\n".encode()
                                     + "Player won: ".encode() + str(2*bet).encode() + "$\n".encode())

                    return  # start next round

            if( self.client_comm("o") == "f"):
                self.player_prize += bet/2
                self.client.send("!Round ".encode() + str(self.round_count).encode() + " tie breaker:\n".encode()
                                 + "Player surrendered! \n".encode()
                                 + "The bet: ".encode() + str(bet).encode() + "$\n".encode()
                                 + "Dealer won: ".encode() + str(bet/2).encode() + "\n".encode()
                                 + "Player won: ".encode() + str(bet/2).encode() + "\n".encode())
                return  # start next round

    def finish_game(self):
        self.client.send("!The game has ended! \n".encode())

        if( self.player_prize >= 0):
            self.client.send("!Player won: ".encode() + str(self.player_prize).encode() + "$\n" )
            self.client.send("!Player is the winner!\n".encode())
        else:
            self.client.send("!Player lost: ".encode() + str(self.player_prize.encode()) + "$\n")
            self.client.send("!Dealer is the winner!\n".encode())

        self.client.send("?Would you like to play again?\n".encode())
        answer = self.client_comm('a')
        if( answer == "y" ):
            #----------------------restart all variables---------------------
            self.dealer = Dealer()
            self.player_card = Card()
            self.dealer_card = Card()
            self.round_count = 1
            self.player_prize = 0
            self.start_Game(client)
            #----------------------------------------------------------------
        if( answer == 'n' ):
            sys.exit()

    def calc_winner(self):
        if(self.player_card.get_num() > self.dealer_card.get_num()):
            return "player"
        if (self.player_card.get_num() < self.dealer_card.get_num()):
            return "dealer"

        return "tie"

#________________________________Game functions END___________________________________________

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
             client.send("denied".encode())
             client.close()


if __name__ == "__main__":
    wait_client = threading.Thread(wait_client())
    wait_client.start()
#_____________________________________________________________________________________
