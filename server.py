import socket
import _thread
import time
import io
import sys
import game

dim = 2
MAX_CONNECTIONS = 2
connections = []
counter = 0
main_round = 0
paresEncontrados = 0
vez = 0

tabuleiro = game.novoTabuleiro(dim)
placar = game.novoPlacar(MAX_CONNECTIONS)

def send_player_number(conn, player_number):
    
    player_number = str(player_number)
    conn.send(player_number.encode().ljust(512))
    
    return None

def wait_for_players(conn):

    start = False
    while(start == False):

        if(MAX_CONNECTIONS == len(connections)):
            conn.send(b'start'.ljust(512))
            start = True
        else:
            time.sleep(1)
    
    return None

def send_winner(conn):

    vencedores = game.check_winner(placar, MAX_CONNECTIONS)

    if len(vencedores) > 1:

        winner = "Houve empate entre os jogadores "
        for i in vencedores:
            winner += str(i) + ' '
        winner += "\n"
    
    else:
        winner = "Jogador {0} foi o vencedor!".format(vencedores[0])
    
    conn.send(winner.encode().ljust(512))

    time.sleep(5)
        
    return None

def exit_game(conn, addr):

    for i in range(len(connections)):
        if(connections[i][1] == addr):
            print('Conexão finalizada com {}:{} total de conexões: {}'.format(addr[0], addr[1], len(connections)))
            connections.pop(i)
            break
        
    conn.close()
    return None

def send_round(player_number, conn):

    if(vez == player_number):
        conn.send(b'turn'.ljust(512))
        return True
    else:
        conn.send(b'wait'.ljust(512))
        return False

def send_table(conn, player_number):
    
    buffer = io.StringIO()
    sys.stdout = buffer

    global vez
    game.imprimeStatus(tabuleiro, placar, vez, player_number)

    sys.stdout = sys.__stdout__ 
    table = buffer.getvalue()
    conn.send(table.encode().ljust(512))

    buffer.close()
    
    return None

def client_choose_card(conn, player_number):

    while(1):

        send_table(conn, player_number)

        play = conn.recv(512).decode('utf-8').rstrip()

        try:
            coordenadas = game.leCoordenada(dim, play)
        except game.InvalidCoordinateError as e:
            conn.send(b'no'.ljust(512))
            conn.send(str(e).encode().ljust(512))
            continue

        i1, j1 = coordenadas

        if(game.abrePeca(tabuleiro, i1, j1) == False):
            conn.send(b'no'.ljust(512))
            conn.send(b'Escolha uma peca ainda fechada!'.ljust(512))
            continue

        conn.send(b'ok'.ljust(512))

        break

    return i1, j1

def check_equals(i1, j1, i2, j2):

    global tabuleiro, placar, vez, paresEncontrados

    result = 'hit'

    if tabuleiro[i1][j1] == tabuleiro[i2][j2]:
        game.incrementaPlacar(placar, vez)
        paresEncontrados = paresEncontrados + 1
        game.removePeca(tabuleiro, i1, j1)
        game.removePeca(tabuleiro, i2, j2)

    else:
        game.fechaPeca(tabuleiro, i1, j1)
        game.fechaPeca(tabuleiro, i2, j2)    
        result = 'miss'

    return result

def client_thread(conn, addr, player_number):

    global vez, paresEncontrados

    wait_for_players(conn)
    send_player_number(conn, player_number)

    totalDePares = dim**2 / 2

    while(paresEncontrados < totalDePares):
         
        my_turn = send_round(player_number, conn)

        if(my_turn == True):
            
            i1, j1 = client_choose_card(conn, player_number)
            i2, j2 = client_choose_card(conn, player_number)

            send_table(conn, player_number)
        
            point = check_equals(i1, j1, i2, j2)
            conn.send(point.encode().ljust(512))

            vez += 1
            vez = vez % MAX_CONNECTIONS

            time.sleep(2)
            continue    

        elif(my_turn == False):

            send_table(conn, player_number)
            
            time.sleep(5)
            continue

    conn.send(b'end'.ljust(512))
    send_table(conn, player_number)

    send_winner(conn)

    exit_game(conn, addr)
         
    return None

def main():
    
    global connections, counter

    HOST = "127.0.0.1"
    PORT = 10200

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    
        server_socket.bind((HOST, PORT))    
        server_socket.listen(1)

        print("Servidor iniciado!")
    
        while(1):

            conn, addr = server_socket.accept()
            if(len(connections) < MAX_CONNECTIONS):
                
                conn.send('Conexão aceita!'.encode('utf-8').ljust(512))
                
                player_number = counter
                connections.append(tuple((conn, addr, player_number)))

                print('Conectado por Jogador {} - {}:{} total de conexões: {}'.format(counter, addr[0], addr[1], len(connections)))
                counter += 1

                _thread.start_new_thread(client_thread, (conn, addr, player_number))

            else:
                conn.send('Conexão recusada!'.encode('utf-8').ljust(512))
                conn.close()

        server_socket.close()

    return None
 
if __name__ == '__main__':
    main()
