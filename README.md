# rpc-comunication
<h1 align="center">
⚪<br>Othello-Reversi Game
</h1>

<img align="center" src="\assets\tabuleiro.jpeg">

## 📚 Resumo
> Othello é um jogo de estratégia para dois jogadores (Pretas e Brancas), jogado num tabuleiro 8x8. A partida começa com quatro peças colocadas no centro do tabuleiro com mostrado abaixo. Pretas fazem a primeira jogada. Os jogadores alternam a vez. Se um jogador não tem jogada válida, passa a vez para o adversário.O jogador com mais peças no tabuleiro ao final do jogo vence. Se ambos tiverem a mesma quantidade de peças, há empate.

# Recursos Principais:
>Este projeto apresenta uma implementação de RPC (Chamada de Procedimento Remoto), permitindo que funções localizadas em um servidor sejam invocadas por clientes de forma transparente, como se fossem locais. Ele explora conceitos fundamentais de sistemas distribuídos e comunicação entre processos.


**Gráficos Simples:** O jogo possui gráficos 2D, com uma interface de usuário limpa e fácil de entender.

Movimentação das peças: As peças podem se mover horizontalmente e verticalmente, apenas pulando outras peças, jogando em espaços vazios.

Chat: É possível se comunicar com o adversário durante toda a partida.

Desistência: Também é possível desistir no meio da partida

Opção de Reinício: Após o término do jogo, os jogadores têm a opção de reiniciar imediatamente.

## Clone Repositório:
```bash
git clone https://github.com/dudacaetano/rpc-communication
cd rpc-communication
```

## Config ambiente virtual
```bash
python -m venv .venv
source .venv/bin/activate
```

## Instalando Dependencias

```bash
pip install -r requirements.txt
```

## Iniciando Servidor

```bash
python server.py
```

output:

```bash
pygame 2.6.1 (SDL 2.28.4, Python 3.12.6)
Hello from the pygame community. https://www.pygame.org/contribute.html
Enter the server port:
```

##  Clientes

Para jogar, você precisa iniciar dois clientes. Os clientes podem ser executados em qualquer máquina da rede local. Ao executar o cliente, você precisará inserir o host (endereço IP) do servidor e o número da porta.

### Executando Clientes:

```bash
python client.py
```

output:

```bash
pygame 2.6.1 (SDL 2.28.4, Python 3.12.6)                                  
Hello from the pygame community. https://www.pygame.org/contribute.html
Enter the server IP to connect:192.168.X.X
Enter the server PORT to connect:5555
Cliente conectado com sucesso.
```
