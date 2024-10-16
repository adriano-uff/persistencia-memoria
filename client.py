import socket
import time
import os

my_number = "0"

def limpaTela():
    
    os.system('cls' if os.name == 'nt' else 'clear')

def receive_table(client_socket):
    
    limpaTela()
    
    table = client_socket.recv(512).rstrip()
    print(table.decode('utf-8'))
    
    return None

def receive_round(client_socket):

    turn = client_socket.recv(512).rstrip()
    
    if(turn == b'turn'):
        return 'turn'
    elif(turn == b'wait'):
        return 'wait'
    else:
        return 'end'

def receive_player_number(client_socket):

    global my_number

    data = client_socket.recv(512).rstrip()
    my_number = data.decode('utf-8')
    print('Eu sou o jogador: ', my_number)
    
    return None

def wait_for_start(client_socket):

    start = False
    while(start == False):

        print('Aguardando jogadores...')
        
        response = client_socket.recv(512).rstrip()

        if(response == b'start'):
            start = True
        else:
            time.sleep(2)
    
    return None

def client_choose_card(client_socket, pos):
        
    while(1):    

        print('mostrar tabela')
        receive_table(client_socket)

        play = input(f'Digite a coordenada da {pos} peça: ')
        client_socket.send(play.encode().ljust(512))

        play_ack = client_socket.recv(512).rstrip()
        
        if(play_ack == b'ok'):    
            print('Coordenada enviada com sucesso!')
            break

        elif(play_ack == b'no'):
            message = client_socket.recv(512).rstrip()
            print(message.decode('utf-8'))
            input("Pressione <enter> para continuar...")

    return play

def receive_winner(client_socket):

    winner = client_socket.recv(512).rstrip()
    print(winner.decode('utf-8'))

    time.sleep(5)

    return None

def client_play(client_socket):

    wait_for_start(client_socket)
    receive_player_number(client_socket)

    while(1):

        my_turn = receive_round(client_socket)

        print('É a minha vez ?: ', my_turn)

        if(my_turn == 'turn'):

            pecasX = client_choose_card(client_socket, "1º")
            pecasY = client_choose_card(client_socket, "2º")

            receive_table(client_socket)
            
            print(f'Pecas escolhidas --> ({pecasX.split()[0]}, {pecasX.split()[1]}) e ({pecasY.split()[0]}, {pecasY.split()[1]})\n')

            point = client_socket.recv(512).rstrip()
            
            if(point == b'hit'):
                print('Pecas casam! Ponto para o jogador: ', my_number)
            elif(point == b'miss'):
                print('Pecas não casam!')

            time.sleep(2)
            continue
             
        elif(my_turn == 'wait'):

            receive_table(client_socket)
            print('Aguarde sua vez...')

            time.sleep(5)
            continue

        if(my_turn == 'end'):
            receive_table(client_socket)
            break

    receive_winner(client_socket)
    print('Fim de jogo! ###')

    client_socket.close()
    
    return None

def main():

    HOST = '127.0.0.1'
    PORT = 10200

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:

        client_socket.connect((HOST, PORT)) 
        response = client_socket.recv(512).rstrip()
        
        print(response.decode('utf-8'))

        if(response == 'Conexão aceita!'.encode('utf-8')):
            client_play(client_socket)
            #fim do jogo, ver vencedores
        
        client_socket.close()

    return None

if __name__ == '__main__':
    main()
