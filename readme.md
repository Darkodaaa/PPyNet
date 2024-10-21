# Simple Networking Functions A Python package that provides basic networking functions for easy communication and data exchange over the network. 
## Features
- **Connnection**: Create a temporary user with and id and a username to send or receive messages from others specified by id.
- - **Connect**: Connect by creating an instance of the connection class and setting your id and username(optional). The id has to be unique the username doesn't.
- - **Message Sending**: Use the send method to send a message to someone specified by id.
- - **Message Receiving**: Use the receive method to receive a message from someone with an id and a username to identify.

- **Peer 2 Peer**: Create a connection between two clients with a shared key
- - **Key Based Connection**: Set a password/key to connect to another client wit the same setting.
- - **Message Sending**: Send a message directly to the other client. If the other client isn't connected this message will be buffered.
- - **Message Receiving**: Receive a message from the other client. Can be specified to not receive buffered messages.
## Installation
You can install the package via pip:
```bash
pip install ppynet
```
## Usage examples

**Peer 2 Peer**:
```python
from PPyNet import P2P
import threading

#key = input("Enter key: ")
key = "randomkey"

conn = P2P(key)

def sending():
    while True:
        msg = input("You: ")
        if msg == "exit":
            exit()
        conn.send({'message': msg})

def receiving():
    while True:
        msg = conn.receive()
        print("Partner: "+msg)
    
threading.Thread(target=sending).start()
threading.Thread(target=receiving).start()
```
**Connnection**:
```python
from PPyNet import Connection
import threading

username = input("Enter username: ")
userId = int(input("Enter your id: "))
to = int(input("Who do you want to chat with: "))

conn = Connection(userId, username)

def sending():
    while True:
        msg = input(username+": ")
        if msg == "chusr":
            conn.changeUsername(input("New username: "))
            continue
        conn.send(msg, to)

def receiving():
    while True:
        msg = conn.receive()
        print(msg["username"]+": "+msg["message"])
    
threading.Thread(target=sending).start()
threading.Thread(target=receiving).start()
```