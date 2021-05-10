import socket
import threading
from common.connection import Connection

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('server socket opened')

host = "localhost"
port = 1337
server.bind((host, port))
server.listen()
print('[LISTENING...]')

clients = []


# method that broadcasts message to all clients
def broadcast(message):
    disconnected = []
    for client in clients:
        try:
            client.send_plaintext(message)
        except:
            print("error sending, dropping client")
            disconnected.append(client)
    for client in disconnected:
        clients.remove(client)


def receive(client, c):
    while True:
        try:
            message = client.recv_plaintext()
            if message is not None:
                broadcast(message)
        except:
            # something went wrong, remove the client
            print("error receiving, dropping client")
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
