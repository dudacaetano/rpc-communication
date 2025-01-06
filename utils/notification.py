from enum import Enum

class NotificationType(Enum):
   REFRESH = "refresh" #atualiza
   ACTION = "action"  #mover peça
   END_GAME = "end_game" #fim de jogo
   ERROR = "error"
   CHAT = "chat"      #mensagem
   CONFIG = "config"  #inicio de jogo
   GIVEUP = "giveup"   #desistencia
   RESET = "reset"     # jogar novamente
    
    