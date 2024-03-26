from PPyNet import Connection
import threading

username = input("Enter username: ")
fid = int(input("Enter your id: "))
to = int(input("Who do you want to chat with: "))

conn = Connection(fid, username)

def sending():
    while True:
        msg = input(username+": ")
        if msg == "stopnow":
            conn.deleteUser()
            exit()
        conn.send(msg, to)

def receiving():
    while True:
        msg = conn.receive()
        if type(msg) == "NoneType":
            continue
        print(msg["username"]+": "+msg["message"])

threading.Thread(target=sending).start()
threading.Thread(target=receiving).start()