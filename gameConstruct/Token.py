
"""
Args:

  player (qualquer): Identificador do jogador que possui o token.
  gridX (int): Posição X do token na grade.
  gridY (int): Posição Y do token na grade.
  image (imagem ou pygame.Surface): A imagem que representa o token na tela.
  GAME (objeto de controle de jogo): Objeto que gerencia o estado do jogo e o desenho da tela.

Return:
  None: O construtor inicializa a instância do token com as propriedades fornecidas.
"""

class TokenConfig:
    def __init__(self, player,gridX, gridY):
        self.player = player
        self.gridX = gridX
        self.gridY = gridY
        self.posX = 80 + (gridY * 80)
        self.posY = 80 + (gridX * 80)

"""
Args:

  window (pygame.Surface): A superfície de desenho onde o token será renderizado na tela.

Return:
  None: O método desenha o token na posição especificada na janela.
"""
class Token(TokenConfig):
    def __init__(self, player, gridX, gridY, image, GAME):
        super().__init__(player, gridX, gridY)
        self.image = image
        self.GAME = GAME 
        
    def animateTransition(self, imagesTransition, imagesResult ):
        for i in range(30):
            self.image = imagesTransition[i // 10]
            self.GAME.draw()
        self.image = imagesResult

    def draw(self, window):
        window.blit(self.image, (self.posX, self.posY))        
