import socket               # Import socket module
import time
s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 12345                # Reserve a port for your service.

s.connect((host, port))
s.settimeout(1)

while True:
    waiting = True
    while waiting:
        try:
            print( s.recv(1024).decode() )
        except:
            waiting = False

    choice = input("1 - status\n"
                      + "2 - bet\n"
                      + "3 - war\n"
                      + "4 - surrender\n"
                      + "5 - quit\n"
                      + "6 - yes\n"
                      + "7 - no\n")
    if choice == '1':
        s.send("s".encode())
    if choice == '2':
        bet = input("Enter your bet:\n")
        s.send("b".encode() + bet.encode())
    if choice == '3':
        s.send("ow".encode())
    if choice == '4':
        s.send("of".encode())
    if choice == '5':
        s.send("q".encode())
    if choice == '6':
        s.send("ay".encode())
    if choice == '7':
        s.send("an".encode())

s.close()