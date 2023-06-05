# Import modules
import socket
import threading
import sys
import configparser
from cryptography.fernet import Fernet

# Define message types
GREETING = b'GREETING'
WELCOME = b'WELCOME'
CHAT = b'CHAT'
TERMINATE = b'TERMINATE'

# Define config file name
CONFIG_FILE = 'config.ini'

# Define a class for p2p chat client
class ChatClient:

    # Initialize the client with IP, port, key and name from config file
    def __init__(self):
        # Read config file
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        self.ip = config['parameters']['ip']
        self.port = int(config['parameters']['port'])
        self.key = config['parameters']['fernet_key'].encode()
        self.name = config['parameters']['username']

        # Create a Fernet object with the key
        self.key_object = Fernet(self.key)

        # Create a socket object
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the IP and port
        self.socket.bind((self.ip, self.port))

        # Print the IP and port on the console
        print(f'Your IP and port are: {self.ip}:{self.port}')

    # Listen for incoming connections
    def listen(self):
        # Start listening on the socket
        self.socket.listen()

        # Accept a connection from another peer
        self.connection, self.address = self.socket.accept()

        # Print the address of the connected peer
        print(f'Connected by {self.address}')

        # Receive a greeting message from the peer 
        greeting = self.connection.recv(1024)

        # Check if the message type is GREETING 
        if greeting.startswith(GREETING):
            # Send a welcome message to the peer with the name attribute
            self.connection.send(WELCOME + b' Welcome to the chat! I am ' + self.name.encode())

            # Start a thread for receiving messages from the peer 
            receive_thread = threading.Thread(target=self.receive)
            receive_thread.start()

            # Start a thread for sending messages to the peer 
            send_thread = threading.Thread(target=self.send)
            send_thread.start()

    # Connect to another peer by IP and port
    def connect(self, ip, port):
        # Connect to the peer's socket 
        self.connection = socket.create_connection((ip, port))

        # Print the address of the connected peer 
        print(f'Connected to {ip}:{port}')

        # Send a greeting message to the peer with the name attribute
        self.connection.send(GREETING + b' Hello! I am ' + self.name.encode())

        # Receive a welcome message from the peer 
        welcome = self.connection.recv(1024)

        # Check if the message type is WELCOME 
        if welcome.startswith(WELCOME):
            # Print the welcome message on the console 
            print(welcome.decode())

            # Start a thread for receiving messages from the peer 
            receive_thread = threading.Thread(target=self.receive)
            receive_thread.start()

            # Start a thread for sending messages to the peer 
            send_thread = threading.Thread(target=self.send)
            send_thread.start()

    # Receive messages from the peer
    def receive(self):
        while True:
            try:
                # Receive a message from the peer 
                message = self.connection.recv(1024)

                # Check if the message type is CHAT or TERMINATE 
                if message.startswith(CHAT):
                    # Decrypt the message with the key
                    decrypted_message = self.key_object.decrypt(message[4:])

                    # Print the decrypted message on the console with the author name
                    author, text = decrypted_message.decode().split(': ', 1)
                    print(f'{author} says: {text}')
                elif message.startswith(TERMINATE):
                    # Decrypt the optional goodbye text with the key
                    decrypted_text = self.key_object.decrypt(message[9:])

                    # Print the goodbye text on the console if any with the author name
                    if decrypted_text:
                        author, text = decrypted_text.decode().split(': ', 1)
                        print(f'{author} says: {text}')

                    # Close the connection and exit the program
                    print('Connection closed by peer.')
                    self.connection.close()
                    sys.exit(0)
                else:
                    # Ignore other message types
                    pass

            except Exception as e:
                # Print any exception on the console and exit the program
                print(e)
                sys.exit(1)

    # Send messages to the peer
    def send(self):
        while True:
            try:
                # Get the user input from the console 
                message = input()

                # Check if the user input is 'exit'
                if message == 'exit':
                    # Ask the user for an optional goodbye text
                    text = input('Enter goodbye text (optional): ')

                    # Encrypt the goodbye text with the key and the name attribute
                    encrypted_text = self.key_object.encrypt((self.name + ': ' + text).encode())

                    # Send a terminate message with the encrypted text to the peer
                    self.connection.send(TERMINATE + encrypted_text)

                    # Print the message type on the console
                    print('Sent TERMINATE message.') # Added to print the message type

                    # Close the connection and exit the program
                    print('Connection closed by you.')
                    self.connection.close()
                    sys.exit(0)
                else:
                    # Encrypt the message with the key and the name attribute
                    encrypted_message = self.key_object.encrypt((self.name + ': ' + message).encode())

                    # Send a chat message with the encrypted message to the peer
                    self.connection.send(CHAT + encrypted_message)

                    # Print the message type on the console
                    print('Sent CHAT message.') # Added to print the message type

            except Exception as e:
                # Print any exception on the console and exit the program
                print(e)
                sys.exit(1)

# Create a p2p chat client object
client = ChatClient()

# Check if the user wants to connect or listen
mode = input('Enter mode (connect or listen): ')

# If the user wants to connect, ask for the peer's IP and port
if mode == 'connect':
    ip = input('Enter peer IP: ')
    port = int(input('Enter peer port: '))
    client.connect(ip, port)
# If the user wants to listen, start listening for connections
elif mode == 'listen':
    client.listen()
# Otherwise, exit the program
else:
    print('Invalid mode.')
    sys.exit(0)


# References
# https://cryptography.io/en/latest/fernet/
# https://github.com/cassiofb-dev/python-p2p-crypt-chat/blob/master/p2p.py
# https://github.com/leonv024/PyChat_v3/blob/master/PyChat.py
# https://chat.openai.com/