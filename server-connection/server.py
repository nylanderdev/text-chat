import socket
import threading
from connection import Connection

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('server socket opened')

host = "localhost"
port = 9913
server.bind((host, port))
server.listen()
print('[LISTENING...]')

clients = []


# method that broadcasts message to all clients
def broadcast(message):
    for client in clients:
        client.send_plaintext(message)


def receive(client, c):
    while True:
        try:
            message = client.recv_plaintext()
            broadcast(message)
        except:
            # something went wrong, remove the client
            print("error")
            clients.remove(client)
            c.close()
            break


def start():
    while True:
        c, ip = server.accept()
        client = Connection(c)
        client.send_plaintext("connected!")
        clients.append(client)
        thread = threading.Thread(target=receive, args=(client, c))
        thread.start()
        print('Active Connections: {}'.format(threading.activeCount() - 1))


start()
