from websocket import create_connection
import json

class RawWs:

    def __init__(self, protocol):
        self.__uri = "wss://darkodaaa.one:25500"
        self.__protocol = protocol
        self.__ws = create_connection(self.__uri)

    def reConnect(self):
        try:
            self.__ws = create_connection(self.__uri)
            return True
        except:
            raise ConnectionError("Can't connect to the server is still it running?")
            
    def send(self, data):
        try:
            return self.__ws.send(json.dumps(data))
        except:
            raise ConnectionError("Sending failed is the server down?")
        
    def receive(self):
        try:
            return json.loads(self.__ws.recv())
        except:
            raise ConnectionError("Receive failed, is the server down?")