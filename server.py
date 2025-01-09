
import socket 
import threading
import json

from datetime import datetime
from utils.connectLAN import connectLAN
from utils.notification import NotificationType
from gameConstruct.board import othelloLogic

from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from xmlrpc.client import ServerProxy


# criando o socket do serve 
'''
HOST - addrs to accept conn 
TCP PORT number - each internet service on a computer gets a unique port number (< 1024
reserved for specific services)
'''
#HOST = " 10.10 0.1"
#PORT = 55557

# create the socket
# AF_INET == ipv4
# SOCK_STREAM == TCP
class Server:    
    def __init__(self, HOST = '0.0.0.0', PORT=8000):
        self.lock = threading.Lock()
        self.HOST = HOST
        self.PORT = PORT

        self.clientWhite = None
        self.clientBlack = None 
        
        self.board = othelloLogic(8, 8)
        self.gameTurn = -1
        self.endGame = False
        self.whitePoints = 2
        self.blackPoints = 2
        
    def register(self):
        """
        Registra o cliente como 1 ou -1
        """
        with self.lock:
            if self.clientWhite is None:
                self.clientWhite = None
                return self.get_setup(1)
            elif self.clientBlack is None:
                self.clientBlack = None
                return self.get_setup(-1)
            else:
                return 0 #Não há espaço para mais clientes 
    
    def send_message(self, sender, message):
        """
        Recebe a mensagem de um cliente e a encaminha ao outro
        """
        if sender == 1:
            connect_receive = self.clientBlack # o destinatario é o cliente -1
            client = 1
        else:
            connect_receive = self.clientWhite # o destinatario é o client 1
            client = -1
            
        if connect_receive is not None:
            try:
                data=json.loads(message)
                self.handle_message(data, sender) # proecessa a mensagem
            except (BrokenPipeError, ConnectionResetError):
                print(f"Connection error with recipient client {client}.")
            except json.JSONDecodeError:
                print("Error decoding the JSON message.")
        return f"Client {client} not connected."
    
    def receive_callback(self, client_id, callback_address):
        """
        Registra o endereço do callback de um cliente
        """
        with self.lock:
            if client_id == 1:
                self.clientWhite = ServerProxy(callback_address)
                return "Callback registered for white."
            elif client_id == -1:
                self.clientBlack = ServerProxy(callback_address)
                return "Callback registered for black"
            return "Invalid client ID"
        
    def send_message_to(self, message, client):
        if connect := self.clientWhite if client == 1 else self.clientBlack:
            try:
                connect.receive_message(json.dumps(message))
            except (BrokenPipeError, ConnectionResetError):
                print(f"Connection error with client {client}. Removing client")
                if client == 1:
                    self.clientWhite = None
                else:
                    self.clientBlack = None
                    
    def get_setup (self,client):
        message = {
           "type":NotificationType.CONFIG.value,
            "playerTurn": client,
            "board": self.board.boardLogic,
            "gameTurn": -1    
        }           
        return json.dumps(message)
    
    def send_config(self, client):
        config = self.get_setup(client)
        self.send_message_to(json.loads(config), client)
        
    def send_refresh(self):
        message = {
            "type":NotificationType.REFRESH.value,
            "board":self.board.boardLogic,
            "gameTurn": self.gameTurn
        }
        self.send_message_to(message, self.gameTurn)
        
    def send_end_game(self):
        message = {
            "type":NotificationType.END_GAME.value,
        }
        self.send_message_to(message, 1)
        self.send_message_to(message, -1)
    
    def executeMove(self, message):
        x = message.get('x')
        y = message.get('y')
        
        if validCells := self.board.findPlayableMoves(self.board.boardLogic, self.gameTurn):
            if(y, x) in validCells:
                self.board.insertToken(self.board.boardLogic, self.gameTurn, y, x)
                swappableTiles = self.board.fetchSwappableTiles(y,x,self.board.boardLogic,self.gameTurn)
                for tile in swappableTiles:
                    self.board.boardLogic[tile[0]][tile[1]] *= -1
                
                self.gameTurn *= -1
                self.send_refresh()
                
                if not self.board.findPlayableMoves(self.board.boardLogic, self.gameTurn):
                    self.endGame = True
                    self.send_end_game()     
                    
    def executeChat(self, message):
        content = message.get('content')
        client = message.get('player')
        message = {
        "type":NotificationType.CHAT.value,
        "content": content,
        }
        self.send_message_to(message, client)
        
    def executeReset(self):
        self.board.clearBoardLogic()
        self.gameTurn = -1
        self.endGame = False
        self.send_config(1)
        self.send_config(-1)
    
    def executeGiveUp(self, client, message):
        message = {
            "type":NotificationType.GIVEUP.value
        }
        self.send_message_to(message, client)
        
    def handle_message(self, message, client):
        print(message)
        message_type = message.get('type')
        
        if message_type == NotificationType.ACTION.value:
            self.executeMove(message)
        
        elif message_type == NotificationType.CHAT.value:
            self.executeChat(message)
        
        elif message_type == NotificationType.RESET.value:
            self.executeReset()
        
        elif message_type == NotificationType.GIVEUP.value:
            self.executeGiveUp(client, message)
        
        else: 
            print("Unknown message type", message)
    
    def run(self):
        PORT = input("Enter the server port:").strip()
        self.PORT = int(PORT)

        with SimpleXMLRPCServer((self.HOST, self.PORT), allow_none=True) as server:
            server.register_instance(self)
            print(f"<<SERVER RUNNING===RPC CONNECTION>>('{connectLAN()}', {self.PORT})")
            server.serve_forever()

if __name__ == "__main__":
    server = Server()
    server.run()