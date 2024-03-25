from websocket import create_connection
import json

class Connection:

    def __init__(self, id, username):
        self.__uri = "wss://darkodaaa.one:25500"
        self.__id = str(id)
        self.__username = username
        self.__timeout = None


        self.__ws = create_connection(self.__uri, timeout = self.__timeout)

        self.__ws.send(json.dumps({
            "protocol": "register",
            "from": self.__id,
            "username": self.__username,
        }))
        
        authPacket = json.loads(self.__ws.recv())
        self.__token = authPacket['token']

    def __reLogin(self):
        self.__ws = create_connection(self.__uri, timeout = self.__timeout)
        self.__ws.send(json.dumps({
            "protocol": "login",
            "id" : self.__id,
            "token" : self.__token
        }))
        loginPacket = json.loads(self.__ws.recv())
        if loginPacket["isSuccess"] == False:
            ConnectionError("Failed to relogin. Did you edit your token or id?")

    def deleteUser(self):
        packet = json.dumps({
            "protocol": "deleteUser",
            "from" : self.__id,
            "token": self.__token
        })
        try:
            self.__ws.send(packet)
        except:
            self.__reLogin()
            self.deleteUser()

    def changeUserName(self, username):
        self.__ws.send(json.dumps({
            "protocol": "changeUsername",
            "id" : self.__id,
            "token" : self.__token,
            "username" : username
        }))
    
    def send(self, message, to):
        packet = json.dumps({
            "protocol": "message",
            "from" : self.__id,
            "to" : to,
            "message" : message
        })
        try:
            self.__ws.send(packet)
        except:
            self.__reLogin()
            self.send(message, to)

    def receive(self):
        try:
            return json.loads(self.__ws.recv())
        except:
            self.__reLogin()
            self.receive()
