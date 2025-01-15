
import socket 
import threading
import json

from datetime import datetime
from utils.connectLAN import connectLAN
from utils.notification import NotificationType
from gameConstruct.board import othelloLogic

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
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
        
    def register_client(self):
        """
        Registra o cliente como 1 ou -1
        Registra o cliente e retorna a configuração inicial via RPC
        """
        with self.lock:
            if self.clientWhite is None:
                self.clientWhite = True
                print("White client registered.")
                return self.get_config(1)
            elif self.clientBlack is None:
                self.clientBlack = True
                print("Black client registered.")
                return self.get_config(-1)
            else:
               print("Registration failed: No available slots.")
               return {"status": "error", "message": "No available slots for registration."} 
    
    def send_message(self, sender, message):
        """
         Envia uma mensagem de um cliente para o outro via RPC.
        """
        recipient_conn = self.clientBlack if sender == 1 else self.clientWhite
        if not recipient_conn:
            return {"status": "error", "message": f"Recipient client ({-sender}) not connected."}
        try:
            data = json.loads(message)
            self.handle_message(data, sender)  # Processa a mensagem
            return {"status": "success", "message": "Message delivered successfully."}
        except json.JSONDecodeError:
            return {"status": "error", "message": "Invalid JSON message format."}
        except Exception as e:
            return {"status": "error", "message": f"Failed to deliver message: {str(e)}."}
    
    def receive_client_callback(self, client_id, callback_address):
        """
        Registra o endereço do callback de um cliente
        """
        with self.lock:
            try:
                proxy = ServerProxy(callback_address)
                if client_id == 1:
                   self.clientWhite = proxy
                   print("Callback registered for white")
                   return {"status": "success", "message": "Callback registered for white."}
                elif client_id == -1:
                   self.clientBlack = proxy
                   print("Callback registered for black")
                   return {"status": "success", "message": "Callback registered for black."}
                else:
                   return {"status": "error", "message": "Invalid client ID."}
            except Exception as e:
                return {"status": "error", "message": f"Failed to register callback: {str(e)}."}
        
    def send_message_to(self, message, client):
        conn = self.clientWhite if client == 1 else self.clientBlack
        if not conn: 
            return {"status": "error", "message": f"Client {client} not connected."}
        try:
            conn.receive_message(json.dumps(message))
            print(f"Message sent to client {client}")
            return {"status": "success", "message": f"Message sent to client {client}."}
        except Exception as e:
            #Remove o cliente da lista se a conexão falhar
            with self.lock:
                if client == 1:
                    self.clientWhite = None 
                else:
                    self.clientBlack = None
            print(f"Failed to send message to client {client}:{str(e)}")
            return{"status": "error", "message": f"Failed to send message to client {client}: {str(e)}"}
                    
    def get_config (self,client):
        message = {
           "type":NotificationType.CONFIG.value,
            "playerTurn": client,
            "board": self.board.boardLogic,
            "gameTurn": -1    
        }           
        return json.dumps(message)
    
    def send_config(self, client):
        config = self.get_config(client)
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
        client = message.get('playerTurn')
        message = {
        "type": NotificationType.CHAT.value,
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