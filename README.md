chatclient.py

DEMO: https://youtu.be/6nz8sxHrPms

This program is a peer to peer chat platform that leverages the symmetic encryption framework knwon as Fernet. I orignally tried to use PGP but ran into issues with the public key handshake.
By using Fernet I was able to massively simplify the encryption side.

The first step is to create config.ini file

Below here is an example of how mine looked:
    [parameters]
    ip = 192.168.1.112
    port = 50233
    fernet_key = DN80giegpRHpNHLClZep_maYg2iXRGHsbq9Uy1Cobi0=
    username = desktop

I used this code to create my fernet key:
    from cryptography.fernet import Fernet
    key = Fernet.generate_key()
    print(key)


After config is done, we can just run this as 'python chat.py'

From there, the console will print out your IP and port you entered in the config:
'Your IP and port are: 192.168.1.112:50233'

It will then prompt if you want to connect or listen.

listen will just put the program into a loop waiting for a connection, once it connects, it will print out who it connected to:
Connected by ('192.168.1.144', 3573)

If we enter connect, we are then prompted to enter the peer's IP and port
Enter peer IP: 192.168.1.144
Enter peer port: 3573

Once the connection goes through, the connector will get the welcome message from the listener and it will look like this:
WELCOME Welcome to the chat! I am desktop

We are then able to send send messages either way due to the multithreaded nature of the program. Recieved chats will have the author in the output:
laptop says: hello desktop

When a message is sent by the client, 'Sent CHAT message.' will appear

If we want to end the chat we simply type in 'exit' this will then prompt us for an optional goodbye message:
exit
Enter goodbye text (optional): bye bye
Sent TERMINATE message.
Connection closed by you.


Learning summary:
    This project took me down a few rabbit holes. While I do have experience in C, it was never this robust. This caused me to take a look at C++ because I appreciated the object oriented nature at first glance.
    I had some skeleton code stood up, however was struggling with testing and as a result moved onto a language I use more frequently, Python.
    I was originally leveraging the python_gnupg however I kept running into issues regarding the binary encoding of the keys with the whitespace and the config file
    This caused me to pivot from the original design and try to find a different encryption algorithim. This is where ChatGPT helped as it pointed me to Fernet, a symmetric key solution
    While far less secure, it allowed me to implement the overall DFA as originally intended.

    To test this program I ran netstat on two machines on the same network and connected the ports and IPs
    This is where the desktop and laptop names come from. I found this to be the coolest part, when I would type one thing into one console and it popped up on the opposing. Very very cool.
    
    Further areas for expansion
        Get PGP to work
        Group chats
        Media sharing 
        Test cases



Some ChatGPT code I used for reference (felt best to include this in here):

    import socket
    import json
    from cryptography.fernet import Fernet

    class PeerToPeerChatClient:
        def __init__(self, config_file):
            self.config = self.load_config(config_file)
            self.key = Fernet.generate_key()
            self.fernet = Fernet(self.key)

        def load_config(self, config_file):
            with open(config_file) as file:
                config = json.load(file)
            return config

        def run(self):
            ip = self.config['ip']
            port = self.config['port']

            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((ip, port))
            self.socket.listen(1)

            print(f"Listening for connections on {ip}:{port}...")

            connection, address = self.socket.accept()
            print(f"Connected to {address[0]}:{address[1]}")

            self.send_greeting(connection)
            self.receive_welcome(connection)
            self.send_encrypted_message(connection)
            self.receive_encrypted_messages(connection)
            self.send_termination_message(connection)
            connection.close()

        def send_greeting(self, connection):
            greeting = "Hello! This is the connector."
            connection.send(greeting.encode())

        def receive_welcome(self, connection):
            welcome = connection.recv(1024).decode()
            print(f"Received welcome message: {welcome}")

        def send_encrypted_message(self, connection):
            while True:
                message = input("Enter your message (or 'exit' to terminate): ")
                if message == "exit":
                    break
                encrypted_message = self.fernet.encrypt(message.encode())
                connection.send(encrypted_message)

        def receive_encrypted_messages(self, connection):
            while True:
                encrypted_message = connection.recv(1024)
                if not encrypted_message:
                    break
                message = self.fernet.decrypt(encrypted_message).decode()
                print(f"Received message: {message}")

        def send_termination_message(self, connection):
            terminate = "Goodbye!"
            encrypted_terminate = self.fernet.encrypt(terminate.encode())
            connection.send(encrypted_terminate)


    if __name__ == "__main__":
        client = PeerToPeerChatClient("config.json")
        client.run()
