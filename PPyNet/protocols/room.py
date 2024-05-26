from ..rawws import RawWs
import random

class Room:
    
    def __init__(self, id: int, code: str) -> None:
        if id is None: id = random.randint(10000,99999)
        self.__id = id
        self.__code = code
        self.__conn = RawWs('room')

        self.__token = self.__conn.request('auth', {'id': self.__id})['token']

    def __reLogin(self):
        try:
            authPacket = self.__conn.request('relogin', {
                'token': self.__token,
                'id': self.__id
            })
            if authPacket['isSuccess']:
                self.__token = authPacket['token']
            return authPacket['isSuccess']
        except: 
            raise ConnectionError(f"Could not relogin to server. Did you change your token or id?")
    
    def send(self, message: dict, retry: bool = True):
        packet = {
            'message': message,
            'id': self.__id,
            'token': self.__token
        }

        if not retry:
            self.__conn.send('message', packet)

        try:
            self.__conn.send('message', packet)
        except:
            self.__reLogin()
            self.send(message, False)

    def receive(self, retry: bool = True) -> dict:
        message: dict = {}
        if not retry:
            message = self.__conn.receive()

        try:
            message = self.__conn.receive()
        except:
            self.__reLogin()
            message = self.receive(False)
        if message['subprotocol'] == 'message':
            return message['message']
        else:
            return self.receive(retry)

    def waitForEvent(self, retry: bool = True) -> dict:
        message: dict = {}
        try: message = self.__conn.receive()
        except:
            self.__reLogin()
            return self.waitForEvent(False)
        if message['subprotocol'] == "event":
            return message['event']
        else:
            return self.waitForEvent(retry)
 
        """if message['subprotocol'] != "event":
            return self.waitForEvent(eventType, retry)
        event: dict = message['event']
        if eventType is not None:
            if event['type'] == eventType: return event
            else: return self.waitForEvent(eventType, retry)
        return event"""
        


    def disconnect(self):
        pass