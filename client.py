import socket 
import msgpack as m
import json
import pygame as p  
import threading

from datetime import datetime
from utils.notification import NotificationType
from gameConstruct.board import DrawGrid

from xmlrpc.client import ServerProxy
from xmlrpc.server import SimpleXMLRPCServer


class Client:
    def __init__(self, HOST = '0.0.0.0', PORT=4444):
        self.HOST = HOST
        self.PORT = PORT

        p.init()
        self.gameDisplay = p.display.set_mode((1100, 800), p.DOUBLEBUF)
        self.gameClock = p.time.Clock()
        
        self.playerTurn = 1
        self.gameTurn = -1
        
        self.board = DrawGrid(8, 8, (80, 80), self)
        self.endGame = False
        self.RUN = True
        
        self.INPUT_TEXT = ''
        self.FONT = p.font.SysFont('arial', 18)
        self.chatBackground = p.image.load("assets/chatBackground.png")
        self.chatBackground = p.transform.scale(self.chatBackground,(250, 500))
        self.chatLog = []
        
        self.inputBoxChat = p.image.load("assets/chatInputBackground.png")
        self.inputBoxChat = p.transform.scale(self.inputBoxChat, (250, 30))
        
        
        self.whitePoints = 2
        self.whitePointsTxt = 'white'
        self.blackPoints = 2
        self.blackPointsTxt = 'black'
        
        self.remoteserver = None
        self.callback_address = None
        
    
    def start_callback_server(self, PORT = 0):
        """
        Inicia um servidor de callback XML-RPC para receber mensagens.
        """    
        def receive_message(message):
            print(message)
            msg = json.loads(message)
            print(f"\nMessage received: {msg}")
            self.handle_message(msg)
            return True
        
        #INCIA O SERVIDOR E CAPTURA O ENDEREÇO 
        callback_server = SimpleXMLRPCServer(("0.0.0.0", PORT), allow_none=True, logRequests=False)
        callback_server.register_function(receive_message, "receive_message")
        
        #Obtem a porta usada se port=0 foi passado
        assigned_port = callback_server.server_address[1]
        
        threading.Thread(target= callback_server.serve_forever, daemon=True).start()
        return f"http://{self.HOST}:{assigned_port}"
    
    def register(self):
        setup_data = self.remoteserver.register()
        print(json.loads(setup_data))
        self.executeConfig(json.loads(setup_data))
        
        print(f"Connected as Client {self.playerTurn}")
        
        self.callback_address = self.start_callback_server()
        print(f"Listening for messages on {self.callback_address}...")
        self.remoteserver.receive_callback(self.playerTurn, self.callback_address)
    
    def run(self):
       HOST =  input ('Enter the server IP to connect:').strip()
       PORT = input('Enter the server PORT to connect:').strip()
       self.HOST = HOST
       self.PORT = int(PORT)
       self.remoteserver = ServerProxy(f"http://{self.HOST}:{self.PORT}/", allow_none=True)
       self.register()
        
    
    def run_GUI(self):
        p.display.set_caption(f"Othello-Client-RPC, Listening on: {self.callback_address}, Calling on: http://{self.HOST}:{self.PORT}")

        while self.RUN:
            self.input()
            self.draw()
            self.gameClock.tick(60)
            
    def receive_messages(self):
        try:
            while self.RUN:
                if _message := self.socket.recv(4096).decode():
                    print()
                    print(_message)
                    try:
                        message = json.loads(_message)
                        self.handle_message(message)
                    except json.JSONDecodeError:
                        print("Error decoding the JSON message")
        except ConnectionResetError:
            print("Connection lost with the server.")
        finally:
            self.socket.close()
    
    def send_move(self, x, y):
        message = {
            "type": NotificationType.ACTION.value,
            "x": x,
            "y": y
        }
        self.remoteserver.send_message(self.playerTurn*-1, json.dumps(message))
    
    def send_message_chat(self, content):
        message = {
            "type": NotificationType.CHAT.value,
            "content": content,
            "playerTurn": self.playerTurn * -1
        }
        self.remoteserver.send_message(self.playerTurn*-1, json.dumps(message))
    
    def send_giveUp(self):
        message ={
            "type": NotificationType.GIVEUP.value
        }   
        self.remoteserver.send_message(self.playerTurn*-1, json.dumps(message))
        self.endGame = True
    
    def send_reset(self):
        message = {
            "type": NotificationType.RESET.value
        }
        self.remoteserver.send_message(self.playerTurn*-1, json.dumps(message))
    
    def executeConfig(self, message):
        playerTurn = message.get('playerTurn')
        
        self.endGame = False
        
        self.playerTurn = playerTurn
        self.gameTurn = -1
        self.whitePoints = 2
        self.whitePointsTxt = 'PLAYER-2'
        self.blackPoints = 2
        self.blackPointsTxt = 'PLAYER-1'
        
        self.executeScore()
        
        if self.playerTurn == 1:
            self.whitePointsTxt += 'WHITE# YOU'
        else: 
            self.blackPointsTxt += 'BLACK# YOU'
        
        self.board.tokens.clear()
        boardLogic = message.get('board')
        self.refresh(boardLogic, -1)
        self.endGame = False
        
    def executeRefresh(self, message):
        boardLogic = message.get('board')
        gameTurn = message.get('gameTurn')
        self.refresh(boardLogic, gameTurn)
     
    '''def displayChatMessage(self, content, timestamp):
        formattedMessage = f"[{timestamp}] {content}"
        self.chatLog.append(['r',formattedMessage]) '''   
        
    def executeChat(self, message):
        content = message.get('content')
        self.chatLog.append(['r', content]) 
        #timestamp = message.get('timestamp')
        #self.displayChatMessage(content, timestamp) 
    
    def executeEndGame(self):
        self.endGame = True 
        
        resultsGame = {
            1:('YOU ARE THE WINNER!!', 'YOU LOST:('),
            -1:('YOU LOST:(','YOU ARE THE WINNER!!'),
            0:('#RRR','#RRR')  
        }
        
        WINNER = 1 if self.whitePoints>self.blackPoints else(-1 if self.whitePoints < self.blackPoints else 0)
        
        self.whitePointsTxt += f'{resultsGame[WINNER][0]}'
        self.blackPointsTxt += f'{resultsGame[WINNER][1]}'
        
        
    def executeGiveUp(self,message):
        self.endGame = True
        
        resultsGame = {
            -1:('YOU ARE THE WINNER!!', 'GAVEUP'),
             1:('WON', 'GAVEUP')
        }
        self.whitePointsTxt += f'{resultsGame.get(self.playerTurn, ("",""))[0]}'
        self.blackPointsTxt += f'{resultsGame.get(self.playerTurn,("",""))[1]}'
        
    
        
    def handle_message(self, message):
        
        message_type = message.get('type')
        
        if message_type == NotificationType.REFRESH.value:
            self.executeRefresh(message)
        
        if message_type == NotificationType.CONFIG.value:
            self.executeConfig(message)
        
        if message_type == NotificationType.CHAT.value:
            self.executeChat()
        
        if message_type == NotificationType.END_GAME.value:
            self.executeEndGame()
            
        if message_type == NotificationType.GIVEUP.value:
            self.executeGiveUp()
        
        else: 
            print("Unknown message type", message)
    
    def get_server_address(self):
        HOST = input('Enter the server IP to connect: ').strip()
        PORT = input('Enter the server port to connect: ').strip()
        self.HOST = HOST
        self.PORT = int(PORT)
    
    def input(self):
        for event in p.event.get():
            if event.type == p.QUIT:
                self.send_giveUp()
                self.RUN = False
            if event.type == p.TEXTINPUT:
                if len(self.INPUT_TEXT) < 19:
                    self.INPUT_TEXT += event.text
            if event.type == p.KEYDOWN:
                if event.key == p.K_BACKSPACE:
                    self.INPUT_TEXT = self.INPUT_TEXT[:-1]
                if event.key == p.K_RETURN and self.INPUT_TEXT != '':
                    self.send_message_chat(self.INPUT_TEXT)
                    self.chatLog.append(["s", self.INPUT_TEXT])
                    self.INPUT_TEXT = ''
                    
            if event.type == p.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = p.mouse.get_pos()
                    
                    if self.endGame:
                        # se jogar novamente 
                        if 800 <= x <= (800+250) and 130 <= y <= (130+30):
                            print()
                            self.send_reset()
                    else: 
                        # se desistir
                        if 800 <= x <= (800+250) and 130 <= y <= (130+130):
                            self.send_giveup()
                            self.endGame = True
                            
                            if self.playerTurn == 1:
                                self.blackPointsTxt += ' YOU ARE THE WINNER'
                                self.whitePointsTxt += ' GAVEUP :('
                            else:
                                self.whitePointsTxt += ' YOU ARE THE WINNER'
                                self.blackPointsTxt += ' GAVEUP'
                        elif self.gameTurn == self.playerTurn:
                            x, y = (x - 80) // 80, (y - 80) // 80
                            if validCells := self.board.findPlayableMoves(self.board.boardLogic, self.gameTurn):
                                if (y, x) in validCells:
                                    self.board.insertToken(self.board.boardLogic, self.gameTurn, y, x)
                                    swappableTiles = self.board.fetchSwappableTiles(y, x, self.board.boardLogic, self.gameTurn)
                                    for tile in swappableTiles:
                                         self.board.animateTransitions(tile, self.gameTurn)
                                         self.board.boardLogic[tile[0]][tile[1]] *= -1
                                    self.send_move(x, y)
                                    self.gameTurn *= -1
                                    self.executeScore()
                            
                        
            
        
    
    def refresh(self, boardLogic, gameTurn):
        self.board.boardLogic = boardLogic  #atualiza o grid com a nova logica
        
        #  scroll through the entire boardLogic()
        for y in range(len(boardLogic)):
            for x in range (len(boardLogic[y])):
                if boardLogic[y][x] != 0:
                    player= boardLogic[y][x]
                    
                    self.board.insertToken(self.board.boardLogic, player, y, x)
        
        self.gameTurn = gameTurn
        self.executeScore()
        
    
    def executeScore(self):
        self.whitePoints, self.blackPoints, emptyScore = self.board.calculatePlayerScore()
        
 # <<<<<<<<<<<<<<<<<<<<<<< RENDER FUNCTIONS >>>>>>>>>>>>>>>>>>>>>>>   
    def renderLabel(self, text,x,y, color=(250,250,250), font=None):
        fontToUse = font if font else self.FONT
        drawImagetxt = fontToUse.render(text, True, color)
        self.gameDisplay.blit(drawImagetxt, (x,y))
        
    def renderBoxChat(self):
        
        '''chatWidth = 250
        chatHeight = 450
        resizedChatBackground = p.transform.scale(self.chatBackground,(chatWidth, chatHeight))
        self.gameDisplay.blit(resizedChatBackground, (800, 130))'''
        
        inputBoxWidth = 830
        inputBoxHeight = 720
        #resizedInputBoxChat = p.transform.scale(self.inputBoxChat,(inputBoxWidth, inputBoxHeight))
        self.gameDisplay.blit(self.inputBoxChat,(inputBoxWidth,inputBoxHeight))
        
         
        chatTitleFont = p.font.Font(None,36)       
        self.renderLabel('chat', 830, 175, color=(255,255,0),font=chatTitleFont)
        y = 670
        
        for type, content in reversed(self.chatLog[-14:]):
            if type == 'r':
                self.renderLabel(content, 805, y)
            else:
                self.renderLabel(content, 805, y, (30, 120, 30))
            y -= 35
            
        textX = 840
        textY = 725
        
        maxTextWidth = inputBoxWidth - 20
        drawImageText = self.FONT.render(self.INPUT_TEXT, True, (250,250,250))
        if drawImageText.get_width() > maxTextWidth:
            while drawImageText.get_width > maxTextWidth:
                self.INPUT_TEXT = self.INPUT_TEXT[:1]
                drawImageText = self.FONT.render(self.INPUT_TEXT, True, (250,250,250))
        
        self.renderLabel(self.INPUT_TEXT, textX, textY)        
        
        
    def renderEndGame(self):
        if self.endGame:
            buttonX, buttonY = 830, 130
            buttonWidth, buttonHeight = 250, 30
            
            resetButtonImage = p.image.load('assets/resetButton.png')
            #resetButtonImage = p.transform.scale(resetButtonImage, (buttonWidth, buttonHeight))
            
            self.gameDisplay.blit(resetButtonImage, (buttonX, buttonY))
            
    def renderGiveUp(self):
        if not self.endGame:
            
            buttonX, buttonY = 830, 130
            buttonWidth, buttonHeight = 250, 30
            
            resetButtonImage= p.image.load('assets/giveupButton.png')
            #resetButtonImage = p.image.load('assets/giveupButton.png')
            
            self.gameDisplay.blit(resetButtonImage, (buttonX, buttonY))
    
    def draw(self):
        self.gameDisplay.fill((0, 0, 0))
        
        self.board.drawGrid(self.gameDisplay)
        
        self.renderLabel(f'{self.whitePoints}: {self.whitePointsTxt}', 800,60)
        self.renderLabel(f'{self.blackPoints}:{self.blackPointsTxt}', 800,95)
        
        self.renderBoxChat()
        
        self.renderEndGame()
        
        self.renderGiveUp()
        
        p.display.flip()
    

#<<<<<<<<<<<< call SERVER >>>>>>>>>>>>
''' def connServer(self):
        HOST = input('HOST>>>')
        PORT = input('PORT>>>')
        
        self.HOST = HOST
        self.PORT = int(PORT)'''
        
if __name__ == "__main__":
    client = Client()
    client.run()
    client.run_GUI() 
        
        
        
        
    
        