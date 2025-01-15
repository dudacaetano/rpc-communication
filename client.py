import socket 
#import msgpack as m
import json
import threading

import re

import pygame as p  

from utils.notification import NotificationType
from gameConstruct.board import DrawGrid

from xmlrpc.client import ServerProxy
from xmlrpc.server import SimpleXMLRPCServer


class Client:
    def __init__(self, HOST = '0.0.0.0', PORT=7474):
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
        
    
    """
    Inicia um servidor de callback RPC no cliente para processar mensagens recebidas do servidor principal,
    decodificando e encaminhando para o método de tratamento.

    Args:
        PORT (int, optional): A porta na qual o servidor de callback será iniciado. 
                              Use 0 para permitir que o sistema escolha uma porta disponível automaticamente. 
                              Default: 0.

    Returns:
        str: O endereço do servidor de callback no formato 'http://<HOST>:<PORT>'.
    """
    def start_async_callback(self, PORT=0):
       
        def receive_message(message):
            print(message)
            try:
                msg = json.loads(message)
                print(f"\nMessage received: {msg}")
                self.handle_message(msg)
            except json.JSONDecodeError:
                print("Erro ao decodificar a mensagem")
            return True

        # Inicia o servidor e captura o endereço
        callback_server = SimpleXMLRPCServer(("0.0.0.0", PORT), allow_none=True, logRequests=False)
        callback_server.register_function(receive_message, "receive_message")

        #Obtém a porta usada caso `port=0` tenha sido passado (porta aleatória)
        port_server_refer = callback_server.server_address[1]

        threading.Thread(target=callback_server.serve_forever, daemon=True).start()
        return f"http://{self.HOST}:{port_server_refer}"
        
        
    
    def setup_client(self):
        """
        Configura e registra o cliente no servidor remoto, além de iniciar o servidor de callback.
        """
        # Registrar o cliente no servidor remoto e obter a configuração inicial
        setup_data = self.remoteserver.register_client()
        print(json.loads(setup_data))
        config =  json.loads(setup_data)
        self.executeConfig(config)

        # Exibe o status da conexão
        print(f"Cliente {self.playerTurn} conectado com sucesso!")

        self.callback_address = self.start_async_callback()
        print(f"Esperando por mensagens em {self.callback_address}")
        self.remoteserver.receive_client_callback(self.playerTurn, self.callback_address)
    
    def run(self):
       server_ip =  input ('Enter the server IP to connect:').strip()
       server_port = input('Enter the server PORT to connect:').strip()
       
       self.HOST = server_ip
       self.PORT = int(server_port)
       
       self.remoteserver = ServerProxy(f"http://{self.HOST}:{self.PORT}/", allow_none=True)
       self.setup_client()
        
    
    def run_GUI(self):
        p.display.set_caption(f"Othello-Client-RPC, Listening on: {self.callback_address}, Calling on: http://{self.HOST}:{self.PORT}")

        while self.RUN:
            self.input()
            self.draw()
            self.gameClock.tick(60)
            
    def receive_messages(self):
        while self.RUN:
            try:
                #receber dados do servidor 
                received_data = self.socket.recv(4096).decode()
                
                if received_data:
                    print("\nMensagem recebida:", received_data)
                    
                    #tentar fazer o parsing da mensagem como JSON
                    try:
                        message = json.loads(received_data)
                        self.handle_message(message)
                    except json.JSONDecodeError:
                        print("Falha ao decodificar a mensagem JSON")
            except ConnectionRefusedError:
                print(f"Conexão com o servidor foi perdida")
                break #finaliza o loop em caso de perda de conexão
            except Exception as e :
                print(f"Erro inesperado:{e}")
                break #Finaliza o loop em caso de erro inesperado
            finally:
                #fecha o socket quando o loop for finalizado
                if not self.RUN:
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
            self.whitePointsTxt += 'WHITE#YOU'
        else: 
            self.blackPointsTxt += 'BLACK#YOU'
        
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
    
    def executeEndGame(self):
        self.endGame = True 
        
        resultsGame = {
            1:('THE WINNER!!', 'THE LOSER:('),
            -1:('THE LOSER:(','THE WINNER!!'),
            0:('#RRR','#RRR')  
        }
        
        WINNER = 1 if self.whitePoints>self.blackPoints else(-1 if self.whitePoints < self.blackPoints else 0)
        
        self.whitePointsTxt += f'{resultsGame[WINNER][0]}'
        self.blackPointsTxt += f'{resultsGame[WINNER][1]}'
        
        
    def executeGiveUp(self):
        self.endGame = True

        # Determina o vencedor com base no jogador que desistiu
        if self.playerTurn == 1: #jogador branco desistiu
            WINNER = -1 
        elif self.playerTurn == -1:# jogador preto desistiu
            WINNER = 1 
        else:
            return # caso invalido

        resultsGame = {
           1: ('GAVEUP', 'THE WINNER :('),
          -1: ('THE WINNER', 'GAVEUP'),
        }
        # Atualiza os textos de pontuação com base no vencedor
        self.whitePointsTxt += f'{resultsGame[WINNER][0]}'
        self.blackPointsTxt += f'{resultsGame[WINNER][1]}'       
        
    def handle_message(self, message):
        
        message_type = message.get('type')
        
        if message_type == NotificationType.REFRESH.value:
            self.executeRefresh(message)
        
        elif message_type == NotificationType.CONFIG.value:
            self.executeConfig(message)
        
        elif message_type == NotificationType.CHAT.value:
            self.executeChat(message)
        
        elif message_type == NotificationType.END_GAME.value:
            self.executeEndGame()
            
        elif message_type == NotificationType.GIVEUP.value:
            self.executeGiveUp()
        
        else: 
            print("Unknown message type", message)
    
    def get_server_address(self):
        """
        solicita ao usuário o IP e a porta do servidor e valida as entradas
        Atualiza os atributos de HOST e PORT do objeto  
        """
        while True: 
            try: 
                #solicita o ip do servidor 
                server_ip = input("Please enter the server IP address:").strip()
                #valida se o IP está no formato correto
                if not self.id_valid_ip(server_ip):
                    print("IP esta no formato invalide. Tente novamente")
                    continue
                
                #solicita a porta do servidor 
                server_port = input("Please enter the server port:").strip()
                #verifica se a porta e um numero valido
                if not server_port.isdigit() or not (1024 <= int(server_port) <= 65535):
                    print("Porta Invalida. Tente novamente com um numero valido")
                    continue
                
                #atualiza os atributos do objeto
                self.HOST = server_ip
                self.PORT = int(server_port)
                break #sai do loop se tudo estiver ok 
            
            except Exception as e :
                print(f"An error ocurred:{e}")
                continue
            
    def is_valis_ip(self, ip):
        """
        Valida se o endereço IP fornecido está no formato correto(IPv4)
        """
        ip_pattern = r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        return bool(re.match(ip_pattern, ip))
        
    #================================================     
    '''
    botões de evento 
    '''
    def quitEvent(self, event):
        if event.type == p.QUIT:
            self.send_giveUp()
            self.RUN = False
    
    def textInput(self, event):
        if event.type == p.TEXTINPUT:
            if len(self.INPUT_TEXT) < 19:
                self.INPUT_TEXT += event.text
    
    def keydownEvent(self, event):
        if event.type == p.KEYDOWN:
            if event.key == p.K_BACKSPACE:
                self.INPUT_TEXT = self.INPUT_TEXT[:-1]
            elif event.key == p.K_RETURN and self.INPUT_TEXT != '':
                self.send_message_chat(self.INPUT_TEXT)
                self.chatLog.append(["s", self.INPUT_TEXT])
                self.INPUT_TEXT = ''
                
    def mouseButtonEvent(self, event):
        if event.type == p.MOUSEBUTTONDOWN and event.button == 1:
            x, y = p.mouse.get_pos()
            if self.endGame:
                self.endGameMouseClick(x, y)
            else:
                self.gameMouseClick(x, y)
    def endGameMouseClick(self, x, y):
        if 800 <= x <= (800 + 250) and 130 <= y <= (130 + 30):
            self.send_reset()
            
    def gameMouseClick(self, x, y):
        if 800 <= x <= (800 + 250) and 130 <= y <= (130 + 30):
            self.send_giveUp()
            self.endGame = True
            self.updateScoreGiveup()
        elif self.gameTurn == self.playerTurn:
            self.gameMove(x, y)
    
    def updateScoreGiveup(self):
        if self.playerTurn == 1:
            self.blackPointsTxt += ' YOU ARE THE WINNER'
            self.whitePointsTxt += ' GAVEUP :('
        else:
            self.whitePointsTxt += ' YOU ARE THE WINNER'
            self.blackPointsTxt += ' GAVEUP'
    
    def gameMove(self, x, y):
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
    
    def input(self):
        eventHandler = {
            p.QUIT: self.quitEvent,
            p.TEXTINPUT: self.textInput,
            p.KEYDOWN: self.keydownEvent,
            p.MOUSEBUTTONDOWN: self.mouseButtonEvent
        }
        for event in p.event.get():
            handler = eventHandler.get(event.type)
            if handler:
                handler(event)
                                    
                                    
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
        
if __name__ == '__main__':
    client = Client()
    client.run()
    client.run_GUI() 
        
        
        
        
    
        