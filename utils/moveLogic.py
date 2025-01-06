import pygame as p 

#utility functions 


def validMoves(x, y, minX = 0, minY=0, maxX=7, maxY=7):
    """
    Argumentos:

      x (int): Coordenada x atual da peça.
      y (int): Coordenada y atual da peça.
      minX (int): Limite mínimo para a coordenada x.
      minY (int): Limite mínimo para a coordenada y.
      maxX (int): Limite máximo para a coordenada x.
      maxY (int): Limite máximo para a coordenada y.
    Retorna:
      list: Uma lista de tuplas representando as coordenadas dos movimentos válidos
    """
    
    moves = []
    #VERTICAL
    if x > minX:
        moves.append((x - 1, y))  # CIMA
        if y > minY:
            moves.append((x -1, y - 1))  # CIMA-ESQUERDA
        if y < maxY:
            moves.append((x - 1, y + 1))  #CIMA-DIREITA
    
    if x < maxX:
        moves.append(( x + 1, y)) #BAIXO
        
        if y > minY:
            moves.append((x + 1, y - 1)) #BAIXO-ESQUERDA 
        if y < maxY:
            moves.append((x + 1, y + 1)) #BAIXO-DIREITA
    #HORIZONTAL       
    if y > minY:
        moves.append((x, y - 1)) # HORIZONTAL- ESQUEDA
        
    if y < maxY:
        moves.append((x , y + 1 )) # HORIZONTAL-DIREITA
        
    return moves 


def loadImages(path,size):
    image = p.image.load(path).convert_alpha()
    return p.transform.scale(image, size)

def getSprites(sheet, row, columns, size, spriteSize):
    
    sprite = p.Surface((32, 32)).convert_alpha()
    sprite.blit(sheet, (0, 0), (row * spriteSize[0], columns * spriteSize[1], spriteSize[0], spriteSize[1]))
    sprite = p.transform.scale(sprite, size)
    sprite.set_colorkey('Black')
    return sprite
