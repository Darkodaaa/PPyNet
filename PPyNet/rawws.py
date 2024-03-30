from websocket import create_connection
import json

class RawConnection:

    def __init__(self):
        self.__uri = "wss://darkodaaa.one:25500"
        self.__ws = create_connection(self.__uri)

    def reConnect(self):
        try:
            self.__ws = create_connection(self.__uri)
            return True
        except:
            return False

    def send(self, data):
        try:
            return self.__ws.send(json.dumps(data))
        except:
            return False
        
    def receive(self):
        try:
            return json.loads(self.__ws.receive())
        except:
            return False