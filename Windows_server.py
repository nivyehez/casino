import socket
import threading
import random
import sys
# _________________Class Card______________________________________
class Card:

    def __init__(self, num, kind):
        self.kind = kind
        self.num = num

    def get_num(self):  # return card's value
        return int(self.num)

    def get_card(self):  # return string that represents the card (symbol+value)
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
# _________________________________________________________________

# _________________Class Dealer________________________________________________________
class Dealer:

    def __init__(self):
        deck = []
        for n in (list(range(2,14))):           #
            for k in ['c', 'd', 'h', 's']:      # Create deck
                deck.append(Card(n%3 + 1, k))       #TODO: FIX n%3+1 to n

        random.shuffle(deck)    # shuffle deck
        self.deck = deck        # Make deck an attribute of Dealer
        self.prize = 0          # initialize Dealer's prize to 0

    # **************************************************************************************************
    #   Function name: deal_card
    #   Input: None
    #   Output: card/ False
    #   description: If deck is not empty return card object, else return false

    #   Function implementation:
    def deal_card(self):
        try:
            return self.deck.pop(0)  # Return top card
        except:
            return False    # deck is empty

    # **************************************************************************************************

    # **************************************************************************************************
    #   Function name: discard_three
    #   Input: None
    #   Output: void / False
    #   description: If possible, discard 3 cards from deck. Otherwise return False

    #   Function implementation:
    def discard_three(self):
        try:
            self.deck.pop(0)
            self.deck.pop(0)
            self.deck.pop(0)
        except:
            return False

    # **************************************************************************************************

    # **************************************************************************************************
    #   Function name: deck_not_empty
    #   Input: None
    #   Output: True / False
    #   description: returns True if deck is not empty o.w return False

    #   Function implementation:
    def deck_not_empty(self):
        if len(self.deck) > 0:
            return True
        return False
    # **************************************************************************************************
# _____________________________________________________________________________________________

# _________________Game class START_________________________________________________
class Game:


    def __init__(self, client):     # Game CTR
        self.client = client        # |
        self.dealer = Dealer()      # |
        self.round_count = 0        # | Init all game variables
        self.player_prize = 0       # |

        self.start_Game()           # start game

    # **************************************************************************************************
    #   Function name: start_Game
    #   Input: None
    #   Output: None
    #   Description: This function is called after creating the game object for the client.
    #                It deals cards for the client and the dealer and then calls play_round function

    #   Function implementation:
    def start_Game(self):
        self.player_card = self.dealer.deal_card()  # | deal cards for dealer and client
        self.dealer_card = self.dealer.deal_card()  # |
        self.client.send("request accepted. Starting game:\n  Player Card: ".encode()  # send start of game msg
                         + self.player_card.get_card().encode() + '\n'.encode())

        while self.dealer.deck_not_empty():
            self.play_round()                           # Starts round
            self.player_card = self.dealer.deal_card()  # | Deal cards for next round
            self.dealer_card = self.dealer.deal_card()  # |

        self.finish_game()      # If reached here, the deck is empty so the game has ended

    # **************************************************************************************************

    # **************************************************************************************************
    #   Function name: client_comm
    #   Input: char
    #   Output: char
    #   Description: This function is responsible for getting messages from the client.
    #                It validates the message got  from client. If it is invalid, it
    #                asks the client to resend his message

    #   Function implementation:
    def client_comm(self, exp):
        # CLIENT -> SERVER PROTOCOL:
        # exp is the expected type of message. The type is sent in the 1st letter of the msg. Available types:
        # 's' = status
        # 'b' = bet
        # 'o' = war options. The next char can be 'w' or 'f' ( war or forfeit)
        # 'q' = quit
        # 'a' = answer. followed by 'y' for yes 'n' for no

        msg = ''
        while msg == '':
            msg = self.client.recv(1024).decode()  # get the message from client

        # ----------------- Interpret msg from client----------------------------------#
        while exp != msg[0]:
            if msg[0] == 'q':     # If client chose to quit game
                self.quit()
            else:
                if( msg[0] == 's'):     # If client asked for the game status
                    self.send_status()
                else:
                    self.request_msg_again()
            msg = self.client.recv(1024).decode()      # get the message from client
            while msg == '':
                msg = self.client.recv(1024).decode()  # get the message from client

        if exp == "a":      # If client sent 'y' (yes) or 'n' (no)
            return msg[1]   # Return client's answer

        if exp == msg[0]:
            if exp == 'b':              # If client sent his bet
                bet = msg[1: len(msg)]  # Extract the bet from the message
                return int(bet)         # Return the bet

            if exp == 'o':   # If the client replied 'w'(war) or 'f'(forfeit)
                return msg[1]   # Extract the client's choice from the message

    # **************************************************************************************************#

    # **************************************************************************************************#
    #   Function name: send_status
    #   Input: None
    #   Output: None
    #   Description: This function sends the current game status to the client.

    #   Function implementation:
    def send_status(self):
        if self.player_prize >= 0:
            self.client.send("#Current round: ".encode() + str(self.round_count).encode() + "\n".encode()
                             + "Player won: ".encode() + str(self.player_prize).encode() + '$\n'.encode())
        else:
            self.client.send("#Current round: ".encode() + str(self.round_count).encode() + "\n".encode()
                             + "Dealer won: ".encode() + str(abs(self.player_prize)).encode() + '$\n'.encode())
    # **************************************************************************************************#

    # **************************************************************************************************#
    #   Function name: quit
    #   Input: None
    #   Output: None
    #   Description: This function sends the client an "End-of-game" message and then closes socket and
    #                shuts down the thread

    #   Function implementation:
    def quit(self):
        self.client.send("The game has ended on round: ".encode() + str(self.round_count).encode() + "!\n".encode()
                            + "The player has quit.\n".encode() + self.print_player_profit()
                            + "Thanks for playing.".encode())
        self.client.close()  # close socket
        sys.exit()          # close current thread

    # **************************************************************************************************#
    #   Function name: print_player_profit
    #   Input: None
    #   Output: String
    #   Description: This function returns a String that describes the current player profit

    #   Function implementation:
    def print_player_profit(self):
        if self.player_prize >= 0:
            return "Player won: ".encode() + str(self.player_prize).encode() + "$\n".encode()

        return "Player lost: ".encode() + str(abs(self.player_prize)).encode() + "$\n".encode()
    # ***************************************************************************************************#

    # **************************************************************************************************#
    #   Function name: request_msg_again
    #   Input: None
    #   Output: None
    #   Description: Sends the client a request to send his message again

    #   Function implementation:
    def request_msg_again(self):
        self.client.send("#Invalid value. please try again".encode())
    # **************************************************************************************************#

    # **************************************************************************************************#
    #   Function name: request_msg_again
    #   Input: None
    #   Output: int
    #   Description: Asks the player to send his bet and returns it as int

    #   Function implementation:
    def get_bet(self):
        self.client.send("#send your bet".encode() + '\n'.encode())
        return self.client_comm("b")
    # **************************************************************************************************#

    # **************************************************************************************************#
    #   Function name: play_round
    #   Input: None
    #   Output: None
    #   Description: This is the main function that handles the game.
    #                It controls the flow of the game according to the current client-Dealer cards

    #   Function implementation:
    def play_round(self):

        self.round_count += 1   # update round_count
        bet = self.get_bet()    # get bet from client

        if( self.calc_winner() == "player" ):   # if the player won
            self.player_prize += bet
            self.client.send("The results of round ".encode() + str(self.round_count).encode() + ":\n".encode()
                             + "Player won: ".encode() + str(bet).encode() + "$\n".encode()
                             + "Player's card: ".encode() + self.player_card.get_card().encode() + "\n".encode()
                             + "Dealer's card: ".encode() + self.dealer_card.get_card().encode() + '\n'.encode())

            return  #start next round

        if ( self.calc_winner() == "dealer" ):  # if the dealer won
            self.player_prize -= bet
            self.client.send("The results of round ".encode() + str(self.round_count).encode() + ":\n".encode()
                             + "Dealer won: ".encode() + str(bet).encode() + "$\n".encode()
                             + "Dealer's card: ".encode() + self.dealer_card.get_card().encode() + "\n".encode()
                             + "Player's card: ".encode() + self.player_card.get_card().encode() + "\n".encode())

            return  # start next round

        if( self.calc_winner() == "tie" ):      # if there was a tie

            self.client.send("#The results of round ".encode() + str(self.round_count).encode() + " is a tie!\n".encode()
                             + "Dealer's card: ".encode() + self.dealer_card.get_card().encode() + "\n".encode()
                             + "Player's card: ".encode() + self.player_card.get_card().encode() + "\n".encode()
                             + "The bet: ".encode() + str(bet).encode() + "$\n".encode()
                             + "Do you wish to surrender or go to war?".encode() + "\n".encode())

            answer = self.client_comm("o")      # get player's choice - war or forfeit

            if answer == 'w':   # if the player chose war

                if self.dealer.discard_three() == False :   # if discard failed (deck is empty), end game.
                    self.finish_game()

                self.client.send("Round ".encode() + str(self.round_count).encode() + " tie breaker:\n".encode()
                                 + "Going to war! \n 3 cards were discarded.\n".encode())

                self.player_card = self.dealer.deal_card()  # | deal cards
                self.dealer_card = self.dealer.deal_card()  # |

                if self.dealer_card == False :    # if deal card failed (deck is empty), end game.
                    self.finish_game()

                if self.calc_winner() == "player":  # if the player won the war
                    self.player_prize += bet        # add the bet to player's prize
                    self.client.send("Original bet: ".encode() + str(bet).encode() + "$\n".encode()
                                     + "New bet: ".encode() + str(bet*2).encode() + "$\n".encode()
                                     + "Dealer's card: ".encode() + self.dealer_card.get_card().encode() + "\n".encode()
                                     + "Player's card: ".encode() + self.player_card.get_card().encode() + "\n".encode()
                                     + "Player won: ".encode() + str(bet).encode() + "$\n".encode())
                    return  # start next round

                if self.calc_winner() == "dealer":      # if the dealer won the war
                    self.player_prize -= bet*2          # subtract twice the bet from player's prize
                    self.client.send("Original bet: ".encode() + str(bet).encode() + "$\n".encode()
                                     + "New bet: ".encode() + str(bet * 2).encode() + "$\n".encode()
                                     + "Dealer's card: ".encode() + self.dealer_card.get_card().encode() + "\n".encode()
                                     + "Player's card: ".encode() + self.player_card.get_card().encode() + "\n".encode()
                                     + "Dealer won: ".encode() + str(2*bet).encode() + "$\n".encode())
                    return  # start next round

                if self.calc_winner() == "tie":  # if the war ended with a tie
                    self.player_prize += 2*bet  # add twice the bet to player's prize
                    self.client.send("Original bet: ".encode() + str(bet).encode() + "$\n".encode()
                                     + "New bet: ".encode() + str(bet * 2).encode() + "$\n".encode()
                                     + "Dealer's card: ".encode() + self.dealer_card.get_card().encode() + "\n".encode()
                                     + "Player's card: ".encode() + self.player_card.get_card().encode() + "\n".encode()
                                     + "Player won: ".encode() + str(2*bet).encode() + "$\n".encode())

                    return  # start next round

            if answer == "f":   # if player chose to forfiet
                self.player_prize += bet/2  # add half the bet to player's prize
                self.client.send("Round ".encode() + str(self.round_count).encode() + " tie breaker:\n".encode()
                                 + "Player surrendered! \n".encode()
                                 + "The bet: ".encode() + str(bet).encode() + "$\n".encode()
                                 + "Dealer won: ".encode() + str(bet/2).encode() + "$\n".encode()
                                 + "Player won: ".encode() + str(bet/2).encode() + "$\n".encode())
                return  # start next round
    # ***********************************************************************************************************#

    # **************************************************************************************************#
    #   Function name: finish_game
    #   Input: None
    #   Output: None
    #   Description: This function sends an "End-of-game" message and then asks the player if he wants to play again

    #   Function implementation:
    def finish_game(self):

        if( self.player_prize >= 0):    # if player gained money from the game
            self.client.send("#The game has ended! \n".encode() + "Player won: ".encode() + str(self.player_prize).encode() + "$\n".encode()
                              + "Player is the winner!\n".encode() + "Would you like to play again?\n".encode())

        else:   # if player lost money
            self.client.send("#The game has ended! \n".encode() + "Player lost: ".encode() + str(self.player_prize).encode() + "$\n".encode()
                                + "Dealer is the winner!\n".encode() + "Would you like to play again?\n".encode())

        answer = self.client_comm('a')  # get player's answer if he wants to play again

        if answer == "y":    # if player chose to play again
            # ----------------------restart all variables---------------------
            self.dealer = Dealer()
            self.round_count = 0
            self.player_prize = 0
            self.start_Game()
            # ----------------------------------------------------------------

        if answer == 'n':        # if player chose not to play
            self.client.close()  # close socket
            sys.exit()           # shut down thread

    # **************************************************************************************************#

    # **************************************************************************************************#
    #   Function name: calc_winner
    #   Input: None
    #   Output: None
    #   Description: This function checks whose card has a bigger value (player's or dealer's)
    #                and returns the winner

    #   Function implementation:
    def calc_winner(self):
        if(self.player_card.get_num() > self.dealer_card.get_num()):
            return "player"
        if (self.player_card.get_num() < self.dealer_card.get_num()):
            return "dealer"

        return "tie"
    # **************************************************************************************************#
#________________________________Game functions END___________________________________________

#_________________________connections and threads management____________________________
def wait_client():
    s = socket.socket()          # Create a socket object
    host = socket.gethostname()  # Get local machine name
    port = 12345                 # Reserve a port for your service.
    s.bind((host, port))         # Bind to the port

    while True:
        s.listen(5)                    # Now wait for client connection.
        client, addr = s.accept()      # Establish connection with client.

        if threading.active_count() < 3:    # if less then 2 Game threads are currently running
            t = threading.Thread(target=Game, args=(client,))
            t.start()
        else:                               # if 2 Game threads are already running, deny the client's request
            client.send("denied".encode())
            client.close()


if __name__ == "__main__":
    wait_client = threading.Thread(wait_client())
    wait_client.start()
#_____________________________________________________________________________________
