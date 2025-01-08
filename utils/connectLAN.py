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
    LAN_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    LAN_socket.settimeout(0)
    
    try:
        #conectar em qualquer IP
        LAN_socket.connect(('10.254.254.254',1))
        local_ip = LAN_socket.getsockname()[0] # retorna o ip local
    except Exception:
        local_ip = '127.0.0.1' # retorna o localhost em caso de falha 
    finally:
        LAN_socket.close()
    return local_ip
        
"""
     try:
        ipLocal = socket.gethostbyname(socket.gethostname())
    except Exception:
        ipLocal = '127.0.0.1'  # Fallback para localhost se falhar
    return ipLocal
"""







