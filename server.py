
import socket 
import threading
import msgpack as m
import os

from datetime import datetime
from utils.connectLAN import connectLAN
from utils.notification import NotificationType
from gameConstruct.board import othelloLogic

from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler


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
    def __init__(self, HOST = '0.0.0.0', PORT=55558):
        self.HOST = HOST
        self.PORT = PORT
        # Initialize XML-RPC server
        self.server = SimpleXMLRPCServer((self.HOST, self.PORT), allow_none=True)
        # Register the current instance to expose methods as XML-RPC
        self.server.register_instance(self)
        


        self.clientWhite = None
        self.clientBlack = None 
        
        self.board = othelloLogic(8, 8)
        self.gameTurn = -1
        self.endGame = False
        self.whitePoints = 2
        self.blackPoints = 2
        
    
    ''' def initializeServeSocket(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.HOST, self.PORT))
        self.server.listen(2)'''
        
    
    #**keyarg: parametro especial usado para capturar um numero variavel de argumentos nomeados
    '''def createMessage(self, messageType, **keyarg):
        message = {"type": messageType}
        message.update(keyarg)
        return message'''
        
    def createMessage(self, messageType, **keyarg):
        message = {"type":messageType}
        message.update(keyarg)
        return message
    
    def notifyMessage(self, message, client):
        if connect := self.clientWhite if client == 1 else self.clientBlack:
            try:
                #serializa a message 
                packedMessage = m.packb(message)
                connect.send(packedMessage) 
            except (BrokenPipeError, ConnectionResetError):
                print(f"Connection error with client {client}. Removing client")
            
            except Exception as e:
                print(f"Failed to send update to client {client}: {e}")
    
    def notifyConfig(self, client):
        message = self.createMessage(
            NotificationType.CONFIG.value,
            playerTurn = client,
            board = self.board.boardLogic,
            gameTurn = -1
        )
        self.notifyMessage(message, client)
        
    def notifyEndGame(self):
        message = self.createMessage(
            NotificationType.END_GAME.value,
            
        )
        self.notifyMessage(message, 1)
        self.notifyMessage(message, -1)
    
    def notifyRefresh(self):
        message = self.createMessage(
            NotificationType.REFRESH.value,
            board = self.board.boardLogic,
            gameTurn = self.gameTurn
        )
        self.notifyMessage(message, self.gameTurn)
    
    #<<<<<<<<<<<<<< FUNCTION OF EXECTIONS >>>>>>>>>>>>>>>>>
    
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
                self.notifyRefresh()
                
                if not self.board.findPlayableMoves(self.board.boardLogic, self.gameTurn):
                    self.endGame = True
                    self.notifyEndGame()
                    
    '''def formatChatMessage(self, content, player):
        return{
            "type": NotificationType.CHAT.value,
            "content":content,
            "player": player
        }'''
        
    def broadcastChatMessage(self, content, client):
        
        timestamp = datetime.now().strftime("%H:%M")
        message = {
            "type": NotificationType.CHAT.value,
            "content": content,
            "player": client,
            "timestamp": timestamp
        }
        #self.notifyMessage(message, client)
        #otherClient = 1 if client == -1 else -1
        #self.notifyMessage(message, otherClient)
        
        if client == 1 and self.clientWhite:
            self.notifyMessage(message, 1)
        if client == -1 and self.clientBlack:
            self.notifyMessage(message, -1)
        
                    
    def executeChat(self, message):
        content = message.get('content')
        client = message.get('player')
        
        
        self.broadcastChatMessage(content, client)
        
    
    def executeGiveup(self, client):
        message = {
            "type": NotificationType.GIVEUP.value
            
        }
        self.notifyMessage(message,client*-1)
        
    def executeReset(self):
        self.board.clearBoardLogic()
        self.gameTurn = -1
        self.endGame = False
        self.notifyConfig(1)
        self.notifyConfig(-1)
        
# <<<<<<<<<<<<< HANDLER FUNCTIONS >>>>>>>>>>>>>>>>>>>>>>>

    def handleMessage(self, connect, message, client): 
        messageType = message.get('type')
        
        if messageType == NotificationType.ACTION.value:
            self.executeMove(message)
        
        elif messageType == NotificationType.CHAT.value:
            self.executeChat(message)
        
        elif messageType == NotificationType.GIVEUP.value:
            self.executeGiveup(client)
            
        elif messageType == NotificationType.RESET.value:
            self.executeReset()         
        
        else:
            print("Unknown message type", message)
            
    def handleClient(self, connect, client):
        self.notifyConfig(client)
        
        '''try:
            while True: 
                data =  connect.recv(1024)
                if not data:
                    break
                print(f'{client}: {data}')
                try:
                    message = m.unpack(data)
                    self.handleMessage(connect, message, client)
                except m.exceptions.ExtraData:
                    print("ERROR decoding the MessagePack message")
        except (ConnectionResetError, BrokenPipeError):
            print(f"Client {client} disconnected")
            self.disconnClient(client)
        finally:
            connect.close()'''
        
        self.notifyConfig(client)
        try:
            while True: 
                data = connect.recv(1024)
                if data:
                    print(f'{client}:{data}')
                    try:
                        
                        message = m.unpackb(data)
                        self.handleMessage(connect, message, client)
                    except m.exceptions.ExtraData:
                        print("ERROR decoding the MessagePack message")
        except(ConnectionResetError, BrokenPipeError):
            print(f"Client {client} disconnected")
            self.disconnClient(client)
        finally:
            connect.close()
    
#<<<<<<<<<<<<<<<<<< DISCONNECTED AND CONNECTED CLIENT >>>>>>>>>>>>>>>

    def disconnClient(self, client):
        if client == 1:
            self.clientWhite = None
        
        else:
            self.clientBlack = None
            
        print(f"Client {client} removed. Waiting for new connection")
        
        thread = threading.Thread(target=self.connClient, args=(client,))
        thread.start()
        
    def connClient(self, clientColor):
        '''connect, addr = self.server.accept()
        print(f"New client connected: {addr} as  {'white' if clientColor == 1 else 'black'}")
        if clientColor == 1:
            self.clientWhite = connect
        else:
            self.clientBlack = connect'''
            
        # Conecta e define o endereço
        connect, addr = self.server.accept()
    
        # Armazena a conexão com base na cor
        client_attr = 'clientWhite' if clientColor == 1 else 'clientBlack'
        setattr(self, client_attr, connect)

        # Exibe mensagem com cor do cliente e endereço
        color = 'white' if clientColor == 1 else 'black'
        print(f"New client connected: {addr} as {color}")
        
        thread = threading.Thread(target=self.handleClient, args=(connect, clientColor))
        thread.start()
        
    def run(self):
        print('othelloServer')
        print(f"<<SERVER RUNNING>>('{connectLAN()}', {self.PORT})")
        
        self.connClient(1)
        self.connClient(-1)

if __name__ == "__main__":
    server = Server()
    server.run()