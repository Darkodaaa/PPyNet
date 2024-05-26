from ..rawws import RawWs

class P2P:

    def __init__(self,  key: str, timeout: int = 10) -> None:
        self.__key = key
        self.__conn = RawWs('peer2peer')

        self.__conn.send('connect', {
            'key': self.__key,
            'timeout': timeout
        })

        authPacket = self.__conn.receive()
        if not authPacket["isSuccess"]:
            raise ConnectionRefusedError("Connection could not be established with other client. Reason: "+authPacket["reason"])
        self.__id = authPacket["id"]
        
    def __reconnect(self):
        try:
            self.__conn.reConnect()
        except:
            raise ConnectionError("Did you change the key? If not the server is probably down.")
        self.__conn.send('reconnect', {
            'key': self.__key,
            'id': self.__id
        })
        loginPacket = self.__conn.receive()
        if not loginPacket["isSuccess"]:
            raise ConnectionError("Failed to relogin. Did you edit your token?")
    
    def send(self, msg: str, retry: bool = True) -> None:
        message = {
            'message': msg,
            'id': self.__id,
            'key': self.__key
        }
        if not retry:
            self.__conn.send('message', message)
            return None

        try:
            self.__conn.send('message', message)
        except:
            self.__reconnect()
            self.send(message, True)

    def receive(self, buffered: bool = True, retry: bool = True) -> str:
        message = None
        if not retry:
            message = self.__conn.receive()

        try:
            message = self.__conn.receive()
        except:
            self.__reconnect()
            return self.receive(buffered)
        
        if message["isBuffered"] == buffered: return self.recive(False, retry)
        return message["message"]