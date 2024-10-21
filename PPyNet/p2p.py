from .rawws import RawWs

class P2P:
    """
        A class for creating a peer 2 peer connection. 

        Properties:
            key: The key (str) of the client. Defined at construction. Set and used only internally.
            id: The id (str) of the client. Defined at construction. Set and used only internally.
        
        Methods:
            init: Initializes the connection with a given id and username.
            deleteUser: Deletes the user from the server.
            changeUsername: Changes the username of the current session.
            send: Sends a message (str) to a specified client by id (int).
            recive: Recives a message (dict) with the username, id and message (str) of the sender.
    """
    def __init__(self,  key: str, timeout: int = 10) -> None:
        """
            Construct a new P2P connection.

            Connects to the P2P service with a given key and a timeout in seconds. If the connection fails, it raises a ConnectionRefusedError with the reason why the connection failed.

            Params:
                key: String the key to connect to the other client with.
                timeout: Int the timeout in seconds. Default is 10.

            Raises:
                ConnectionRefusedError: When the connection to the other client fails or times out.

        """
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
        """
            Relogs session whenever its called. Only used internally.
            This usually happens when a sending or recieving of a message fails.

            Raises:
                ConnectionError: When it can't reconnect to the server as its probably down.
                ConnectionError: When the login failed probably because the id or token is invalid. (This usually happens if the user changes the session's properties.)
        """
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
        """
            Sends a message to the other client in the p2p connection.

            Params:
                msg: String the message to send to the other client.
                retry: Boolean if the sending of the message should be retried after a connection failure.
                    Leave this on as this tries to relogin whenever your connection times out. Default is True.

            Raises:
                ConnectionError: When retry is false or failed and it can't send the message.

            Returns: None
        """
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
        """
            Recives a message from the other client in the p2p connection.

            Params:
                buffered: Boolean if the message should be retrieved from the buffer or not. Default is True.
                retry: Boolean if the recieving of the message should be retried after a connection failure.
                    Leave this on as this tries to relogin whenever your connection times out. Default is True.

            Raises:
                ConnectionError: When retry is false or failed and it can't recieve the message.

            Returns: String the message from the other client.
        """
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