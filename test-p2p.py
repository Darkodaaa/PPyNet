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
