import socket
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('server socket opened')

host = 'localhost'
port = 9913
server.bind((host, port))
server.listen()
print('[LISTENING...]')

clients = []


# method that broadcasts message to all clients
def broadcast(message):
    for client in clients:
        client.send(message)


def client_socket_handler(client):
    while True:
        try:
            message = client.recv(1024)
            broadcast(message)
        except:
            # something went wrong, remove the client
            clients.remove(client)
            client.close()
            break


def receive():
    while True:
        client, ip = server.accept()
        client.send(bytes('Connected successfully'))

        thread = threading.Thread(target=client_socket_handler, args=(client,))
        thread.start()


def main():
    receive()


if __name__ == '__main__':
    main()
