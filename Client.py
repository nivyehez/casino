import socket               # Import socket module
import time
import sys

# -----------------Create connection with server----------------------------#

s = socket.socket()          # Create a socket object
host = socket.gethostname()  # Get local machine name
port = 12345                 # Reserve a port for your service.
s.connect((host, port))
# ---------------------------------------------------------------------------#

# -------------------------Get message from server---------------------------#
while True:
    waiting = True
    while waiting:
        try:
            answer = s.recv(2048).decode()      # Get message from TCP Buffer
            if answer == '':
                continue
            elif answer == "denied":            # if server denied client's request to play
                print("denied\n")
                s.close()                       # close socket
                sys.exit(0)                     # exit program
        except:
            print("COMMUNICATION ERROR. EXITING GAME\n")    # in case of com error
            s.close()       # close socket
            sys.exit(0)     # exit program
        else:
            waiting = False                     # message received successfully
# ----------------------------------------------------------------------------#

# Explanation about the server->client protocol:
# When the server sends a message that requires client's response,
# it adds to that message the '#' char.
# Else, the message does not contain '#'

    if answer.find('#') == -1:              # message received does not require client's response
        print(answer)
        continue

    else:                                   # message received requires client's response
        answer = answer.replace('#', '')    # remove the '#' char as it is only required for msg classification
        print(answer)

        #--------------------Get user's choice------------------------------#

        #in order to seperate the choices, "denumerated" them from string to a number(code-wise only)
        while True:
            choice = input("1 - status\n"
                              + "2 - bet\n"
                              + "3 - war\n"
                              + "4 - surrender\n"
                              + "5 - quit\n"
                              + "6 - yes\n"
                              + "7 - no\n")
            # check validity of user's input:
            if int(choice)<= 7 and int(choice)>= 1:     # Got a valid input
                break
            else:                                       # Input is invalid
                print("Please enter a valid input \n")
        # --------------------------------------------------------------------#

        # -------------------Handling the user's choice------------------------#
        # CLIENT->SERVER PROTOCOL:
        # 's' = status
        # 'b' = bet. followed by the amount to bet
        # 'o' = war options. The next char can be 'w' or 'f' (war or forfeit)
        # 'q' = quit
        # 'a' = answer. Followed by 'y' for yes 'n' for no

        if choice == '1':       # ask for status
            msg = "s".encode()

        elif choice == '2':     # send bet
            bet = input("Enter your bet:\n")
            msg = "b".encode() + bet.encode()

        elif choice == '3':     # choose war
            msg = "ow".encode()

        elif choice == '4':     # choose forfeit
            msg = "of".encode()

        elif choice == '5':     # quit game
            msg = "q".encode()
            s.send(msg)
            answer = s.recv(1024).decode()  # Get end-of-game message
            print(answer)
            s.close()       # close socket
            sys.exit()      # close program

        elif choice == '6':  # send yes
            msg = "ay".encode()

        elif choice == '7':  # send no
            msg = "an".encode()
            s.close()   # close socket
            sys.exit()  # close program

        s.send(msg)     # send message
        # -------------------------------------------------------------------#