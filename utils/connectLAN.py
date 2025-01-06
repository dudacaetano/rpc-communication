import socket
import os


#SOCK_DGRAM:cria um socket de datagrama (usando o protocolo UDP), que é sem conexão. 
#Isso significa que não há estabelecimento de conexão completo entre cliente e servidor 
#como em SOCK_STREAM (protocolo TCP).

'''
Para obter o IP local, não precisamos de uma comunicação de dados verdadeira.
Precisamos apenas simular uma tentativa de conexão para que o sistema escolha a 
interface de rede e retorne o IP local.
Como SOCK_DGRAM não exige conexão contínua,
ele torna a operação mais rápida e simples.
'''


def connectLAN():
    try:
        #tentar obter o IP da váriavel de ambiente, caso contrario, usa a funcao de obter o ip local
        ipLocal =  os.getenv("LAN_IP", socket.gethostbyname(socket.gethostname()))
    except Exception:
        ipLocal = '127.0.0.1'  # Fallback para localhost se falhar
    return ipLocal
    
   
   
   
    
"""
     try:
        ipLocal = socket.gethostbyname(socket.gethostname())
    except Exception:
        ipLocal = '127.0.0.1'  # Fallback para localhost se falhar
    return ipLocal
"""








