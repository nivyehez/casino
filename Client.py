import socket               # Import socket module
import time
import sys

s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 12345                # Reserve a port for your service.
quit_game = False

s.connect((host, port))
#s.settimeout(1)

while True:
    waiting = True
    while waiting:
        try:
            answer = s.recv(1024).decode()      # Get message from server
            print("1\n")
            if answer == '':
                continue
            elif answer == "denied":
                print("denied\n")
                s.close()
                sys.exit(0)
            else:
                print(answer[1: len(answer)] + '\n')
                print("2\n")
        except:
            print("SERVER ERROR. EXITING GAME\n")
            s.close()
            sys.exit(0)
        else:
            waiting = False


    if answer[0] == '!':
        continue

    elif answer[0] == '?':
        #in order to seperate the choices, "denumerated" them from string to a number(code-wise only)
        while True:
            choice = input("1 - status\n"
                              + "2 - bet\n"
                              + "3 - war\n"
                              + "4 - surrender\n"
                              + "5 - quit\n"
                              + "6 - yes\n"
                              + "7 - no\n")
            if int(choice)<= 7 and int(choice)>= 1:
                break
            else:
                print("Please enter a valid input \n")

        # handling the user's choice.
        if choice == '1':
            msg = "s".encode()
        elif choice == '2':
            bet = input("Enter your bet:\n")
            msg = "b".encode() + bet.encode()
        elif choice == '3':
            msg = "ow".encode()
        elif choice == '4':
            msg = "of".encode()

        elif choice == '5':
            quit_game = True
            msg = "q".encode()
            s.send(msg)
            answer = s.recv(1024).decode()
            print(answer)
            s.close()
            sys.exit()

        elif choice == '6':
            msg = "ay".encode()
        elif choice == '7':
            msg = "an".encode()

        s.send(msg)


s.close()