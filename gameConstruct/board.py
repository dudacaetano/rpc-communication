import pygame as p  
import numpy as np
from utils.moveLogic import validMoves, loadImages ,getSprites
from gameConstruct.Token import TokenConfig, Token
from collections import Counter



class othelloLogic:
    def __init__(self, rows, columns):
        self.grid_height = rows
        self.grid_width = columns
        self.tokens = {}
        
        self.boardLogic = self.emptyGrid(rows, columns)
        
    def emptyGrid(self, rows, columns):
        board = [[0 for _ in range(columns)] for _ in range(rows)]
        self.insertToken(board, 1 , 3 ,3)
        self.insertToken(board, -1, 3 , 4)
        self.insertToken(board, 1, 4, 4 )
        self.insertToken(board, -1, 4 , 3)
        
        return board
    # ATUALIZA: mostra o tabuleiro atualizado depois da jogada    
    def displayLogicBoard(self):
        """Prints the current logic board state."""
        print('  | A | B | C | D | E | F | G | H |')
        for i, row in enumerate(self.boardLogic):
            line = f'{i} |'.ljust(3, " ")
            for item in row:
                line += f"{item}".center(3, " ") + '|'
            print(line)
        print()
        
    def insertToken(self, board, playerTurn, y, x):
        self.tokens[(y, x)] = TokenConfig(playerTurn, y, x)
        board[y][x] = self.tokens[(y,x)].player
    
    def findPlayableMoves(self, board, gameTurn):
        validCells = self.findValidCells(board, gameTurn)
        playableCells = []
        
        for cell in validCells:
            x, y = cell
            if cell in playableCells:
                continue
            swappableTiles = self.fetchSwappableTiles(x,y, board, gameTurn)
            
            if swappableTiles:
                playableCells.append(cell)
                
        return playableCells
    #REQUISITO : MOVIMENTAR AS PEÇAS NO TABULEIRO
    def findValidCells(self, board, playerTurn):
        
        validCellToClick = []
        
        for gridX, row in enumerate(board):
            for gridY, col in enumerate(row):
                if board[gridX][gridY] != 0:
                    continue
                DIRECTIONS = validMoves(gridX, gridY)
                
                for direction in DIRECTIONS:
                    dirX, dirY = direction
                    checkedCell = board[dirX][dirY]
                
                    if checkedCell == 0 or checkedCell == playerTurn:
                         continue
                
                    if (gridX, gridY) in validCellToClick:
                         continue
                
                    validCellToClick.append((gridX, gridY))       
        return validCellToClick
        
    
    def fetchSwappableTiles(self, x, y, board, player):
        
        surroundCells = validMoves(x, y)
        
        if not surroundCells:
            return []
        
        swappableTiles = []
        
        for checkCell in surroundCells:
            checkX, checkY = checkCell
            offsetX, offsetY = checkX - x, checkY - y
            currentLine = []
            
            
            while True: 
                if board[checkX][checkY] == -player:
                    currentLine.append((checkX, checkY))
                elif board[checkX][checkY] == player:
                    break
                elif board[checkX][checkY] == 0:
                    currentLine.clear()
                    break
                
                checkX += offsetX
                checkY += offsetY
                
                if checkX < 0 or checkX >= self.grid_width or checkY < 0 or checkY >= self.grid_height:
                    currentLine.clear()
                    break
                
            if currentLine:
                swappableTiles.extend(currentLine)
        
        return swappableTiles
    
    
    #CONTROLE DE PONTUAÇÃO DOS JOGADORES
    def calculatePlayerScore(self):
        listBoard = [cell for row in self.boardLogic for cell in row]
        counter = Counter(listBoard)
        
        whiteScore = counter[1]
        blackScore = counter[-1]
        emptyScore = counter[0]
        
        return(whiteScore, blackScore,emptyScore)

                    
            
    def clearBoardLogic(self):
        self.tokens.clear()
        self.boardLogic = self.emptyGrid(self.grid_height, self.grid_width)


class DrawGrid:
    
    def __init__(self, rows, columns, size, main):
        self.GAME = main
        self.grid_height = rows
        self.grid_width = columns
        self.size = size
        self.whitetoken = loadImages('assets/WhiteToken.png', size)
        self.blacktoken = loadImages('assets/BlackToken.png', size)
        self.transitionWhiteToBlack = [loadImages(f'assets/BlackToWhite{i}.png', self.size) for i in range(1, 4)]
        self.transitionBlackToWhite = [loadImages(f'assets/WhiteToBlack{i}.png', self.size) for i in range(1, 4)]
        self.background = self.loadBackGroundImages()
        
        self.tokens ={}
    
        self.gridBackgraundImage = self.createBackground()
        
        self.boardLogic = self.emptyGrid(rows, columns)
        
        
    def emptyGrid(self, rows, columns):
        '''board = [[0 for _ in range(columns)] for _ in range(rows)]
        return board'''
        return np.zeros((rows, columns), dtype=int)
    
    def displayLogicBoard(self):
        """Prints the current logic board state."""
        print('  | A | B | C | D | E | F | G | H |')
        for i, row in enumerate(self.boardLogic):
            line = f'{i} |'.ljust(3, " ")
            for item in row:
                line += f"{item}".center(3, " ") + '|'
            print(line)
        print()
    
    #REQUISITO: INDICA DE QUEM É O TURNO    
    def insertToken(self, board, playerTurn, y, x):
        tokenImage = self.whitetoken if playerTurn == 1 else self.blacktoken
        self.tokens[(y, x)] = Token(playerTurn, y, x, tokenImage, self.GAME)
        board[y][x] = self.tokens[(y, x)].player
    
    
    #REQUISITO: ENCONTRA MOVIMENTOS VALIDOS PARA O JOGADOR ATUAL    
    def findPlayableMoves(self, board, gameTurn):
        validCells = self.findValidCells(board, gameTurn)
        playableCells = []
        
        for cell in validCells:
            x, y = cell
            if cell in playableCells:
                continue
            swappableTiles = self.fetchSwappableTiles(x, y, board, gameTurn)
            
            if swappableTiles:
                playableCells.append(cell)
                
        return playableCells
    
    
    def findValidCells(self, board, playerTurn):
        
        validCellToClick = []
        
        for gridX, row in enumerate(board):
            for gridY, col in enumerate(row):
                if board[gridX][gridY] != 0:
                    continue
                DIRECTIONS = validMoves(gridX, gridY)
                
                for direction in DIRECTIONS:
                    dirX, dirY = direction
                    checkedCell = board[dirX][dirY]
                
                    if checkedCell == 0 or checkedCell == playerTurn:
                        continue
                 
                    if (gridX, gridY) in validCellToClick:
                        continue
                
                    validCellToClick.append((gridX, gridY))    
        return validCellToClick
    
    #depois de encontra a cell válida para jogar, inverte todas as cell que serao do novo jogador
    def fetchSwappableTiles(self, x, y, board, player):
        
        surroundCells = validMoves(x, y)
        
        if not surroundCells:
            return []
        
        swappableTiles = []
        
        for checkCell in surroundCells:
            checkX, checkY = checkCell
            offsetX, offsetY = checkX - x , checkY - y
            currentLine = []
            
            
            while True: 
                if board[checkX][checkY] == -player:
                    currentLine.append((checkX, checkY))
                elif board[checkX][checkY] == player:
                    break
                elif board[checkX][checkY] == 0:
                    currentLine.clear()
                    break
                
                checkX += offsetX
                checkY += offsetY
                
                if checkX < 0 or checkX >= self.grid_width or checkY < 0 or checkY >= self.grid_height:
                    currentLine.clear()
                    break
                
            if currentLine:
                swappableTiles.extend(currentLine)
        
        return swappableTiles
           
    def loadBackGroundImages(self):
        alpha = 'ABCDEFGHI'
        spriteSheet = p.image.load('assets/wood.png').convert_alpha()
        imageDict = {}
        for i in range(3):
            for j in range(7):
                imageDict[alpha[j]+str(i)] = getSprites(spriteSheet, j, i, (self.size), (32, 32))
        return imageDict
        
    
    
    def createBackground(self):
        gridBg = [
            ['C0', 'D0', 'D0', 'D0', 'D0', 'D0', 'D0', 'D0', 'D0', 'E0'],
            ['C1', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'E1'],
            ['C1', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'E1'],
            ['C1', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'E1'],
            ['C1', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'E1'],
            ['C1', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'E1'],
            ['C1', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'E1'],
            ['C1', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'E1'],
            ['C1', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'E1'],
            ['C2', 'D2', 'D2', 'D2', 'D2', 'D2', 'D2', 'D2', 'D2', 'E2'],
        ]
        image = p.Surface((960, 960))
        for j, row in enumerate(gridBg):
            for i, img in enumerate(row):
                image.blit(self.background[img], (i * self.size[0], j * self.size[1]))
        return image
    
    def drawGrid(self, window):
        window.blit(self.gridBackgraundImage, (0, 0))

        for token in self.tokens.values():
            token.draw(window)
            
        availMoves = self.findPlayableMoves(self.boardLogic, self.GAME.gameTurn)
        #if self.GAME.currentPlayer == 1: //show the validCells just for currentPlayer
        if self.GAME.gameTurn == self.GAME.playerTurn:
            for move in availMoves:
               p.draw.rect(window, (0,255, 0), (80 +(move[1]*80) + 30, 80 +(move[0] * 80) + 30 ,20 ,20))
               # p.draw.rect(window, (240, 240, 240) if self.GAME.playerTurn == 1 else (50, 50, 50), (80 + (move[1] * 80) + 30, 80 +(move[0] * 80) + 30, 20, 20))
    
    
    def animateTransitions(self, cell, player):
        if player == 1:
            self.tokens[(cell[0], cell[1])].animateTransition(self.transitionWhiteToBlack, self.whitetoken)
        else:
            self.tokens[(cell[0], cell[1])].animateTransition(self.transitionBlackToWhite, self.blacktoken)
        
    
    def calculatePlayerScore(self):
        listBoard = [cell for row in self.boardLogic for cell in row]
        counter = Counter(listBoard)
        
        whiteScore = counter[1]
        blackScore = counter[-1]
        emptyScore = counter[0]
        
        return(whiteScore, blackScore,emptyScore)