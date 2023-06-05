chatclient.py

This program is a peer to peer chat platform that leverages the symmetic encryption framework knwon as Fernet. I orignally tried to use PGP but ran into issues with the public key handshake. By using Fernet I was able to massively simplify the encryption side.

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