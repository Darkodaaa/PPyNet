from .rawws import RawWs
import random

class Connection:
    """
        A class for creating a simple connection. 

        Properties:
            id: The id (str) of the client. Defined at construction. Set and used only internally.
            username: The username (str) of the client. Defined at construction. Has a getter and setter.
            token: The token (str) of the client. Given by the server at construction. Only used internally.
        
        Methods:
            init: Initializes the connection with a given id and username.
            deleteUser: Deletes the user from the server.
            changeUsername: Changes the username of the current session.
            send: Sends a message (str) to a specified client by id (int).
            recive: Recives a message (dict) with the username, id and message (str) of the sender.
    """
    def __init__(self, id: int = None, username: str = "") -> None:
        """
            Construct a new connection.

            Params:
                id: Number the id is what represents this session and where others can send messages.
                    If it cannot be converted to a string it defaults to to a random 6 digit integer.
                username: String an extra property that is given to the user you send a message to.
                    Defaults to the given or generated id and converts it into a string.

            Raises:
                ConnectionError: When it can't connect to the server.
                ValueError: When the id provided is already in use.
            
            Returns: New instance of the Connection class.
        """
        self.__conn = RawWs("connection")
        try: self.__id = str(id)
        except: self.__id = str(random.randint(100000, 999999))
        if username == "": self.__username = self.__id
        else: self.__username = username

        self.__conn.send("register",{
            "from": self.__id,
            "username": self.__username,
        })
        
        authPacket = self.__conn.receive()
        if authPacket["isSuccess"]:
            self.__token = authPacket['token']
        else:
            ValueError("Invalid id: %s. It's already in use." % self.__id)

    def __reLogin(self) -> None:
        """
            Relogs session whenever its called.
            This usually happens when a sending or recieving of a message fails.

            Raises:
                ConnectionError: When it can't reconnect to the server as its probably down.
                ConnectionError: When the login failed probably because the id or token is invalid. (This usually happens if the user changes the session's properties.)

            Returns: None
        """

        try:
            self.__conn.reConnect()
        except:
            raise ConnectionError("Did you change the address? If not the server is probably down.")
        self.__conn.send("login", {
            "id" : self.__id,
            "token" : self.__token
        })
        loginPacket = self.__conn.receive()
        if loginPacket["isSuccess"] == False:
            raise ConnectionError("Failed to relogin. Did you edit your token or id? \nIf not maybe someone else logged on with the same id because your session was expired.")

    def deleteUser(self):
        """
            Deletes the user. \n
            Not needed since the server cleans up unused users.

            Returns: Boolean if the server was reachable.If its false it was probably deleted already or the server shut down.
        """
        packet = {
            "from" : self.__id,
            "token": self.__token
        }
        try:
            self.__conn.send("deleteUser", packet)
            return True
        except:
            return False

    def changeUsername(self, username: str):
        """
            Changes the user name of the user. \n
            The happens on the server side and the client side.

            Params:
                username: The username to change to.
            
            Raises:
                ConnectionError: When the server isn't available.

            Returns: None
        """
        self.__conn.send("changeUsername", {
            "id" : self.__id,
            "token" : self.__token,
            "username" : username
        })
        self.__username = username

    @property
    def username(self) -> str:
        """
            Returns the username (str) stored in the current session.

            Returns: String the current username of the client. 
        """
        return self.__username
    
    @username.setter
    def username(self, username: str) -> None:
        """
            Changes the user name of the user. \n
            The happens on the server side and the client side.

            Params:
                username: The username to change to.
            
            Raises:
                ConnectionError: When the server isn't available.

            Returns: None
        """
        self.changeUsername(username)
    
    @property
    def id(self):
        """
            Returns the id (str) stored in the current session.

            Returns: String the current id of the client. 
        """
        return self.__id
    
    @id.setter
    def id(self, value):
        """
            Your id cannot be changed as of right now.
            It can be if you access the property, but don\'t do that.
        """

    def send(self, message: str, to: int, retry = True) -> None:
        """
            Sends a message to the client with the given id.

            Params:
                message: String the message to send to the specified user.
                to: Int the id of the user to send the message to.
                retry: Boolean if the sending of the message should be retried after a connection failure.
                    Leave this on as this tries to relogin whenever your connection times out. Default is True.

            Raises:
                ConnectionError: When retry is false and the it can't send the message.

            Returns: None
        """
        packet = {
            "from" : self.__id,
            "to" : to,
            "message" : message
        }

        if not retry:
            self.__conn.send("message", packet)
            return None

        try:
            self.__conn.send("message", packet)
        except:
            self.__reLogin()
            self.send(message, to)

    def receive(self, retry=True) -> dict:
        """
            Receive a message if someone sent this client one.

            Params:
                retry: Boolean if the receiving of a message should be retried after a connection failure.
                    Leave this on as this tries to relogin whenever your connection times out. Default is True.

            Raises:
                ConnectionError: When retry is false and the connection is closed.
                RecursionError: When retry is true and relogin succeeds but it can't receive a message. Happens very rarely.

            Returns: Dict a dictionary parsed from a json containing the senders username, id and message.
        """

        if not retry:
            return self.__conn.receive()
        
        try:
            return self.__conn.receive()
        except:
            self.__reLogin()
            return self.receive()