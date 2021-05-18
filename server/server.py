import socket
import time

from server.persistence import *
from common.connection import Connection
from common.handler import ConnectionHandler

guarantee_complete_store()
file_registry = read_file_registry()
user_registry = read_user_registry()
max_user_uuid = running_user_uuid()
max_file_uuid = running_file_uuid()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('server socket opened')

host = "0.0.0.0"
port = 1337
server.bind((host, port))
server.listen()
print('[LISTENING...]')

awaiting_login = []
awaiting_handler = ConnectionHandler()
client_handler = ConnectionHandler()
clients = []
client_ids = {}
id_name_map = {}
for username, (password, uid) in user_registry.items():
    id_name_map[uid] = username


def init_client(client):
    client.send_channel("General", 0)
    client.send_channel("Misc", 1)
    send_online_joins(client)


def send_online_joins(client_joining):
    for client in clients:
        if client == client_joining:
            continue
        client_id = client_ids[client]
        client_name = id_name_map[client_id]
        client_joining.send_join(client_name, client_id)


def on_upload(client, cid, fid, chid, name, data):
    lost = []
    print("[IMG:", str(cid), "on ", str(chid) + "]", len(data))
    global max_file_uuid
    max_file_uuid += 1
    fid = max_file_uuid
    uid = cid
    is_jpg = name.endswith(".jpg")
    file_registry[fid] = (name, uid, is_jpg, len(data), chid)
    save_file(fid, data)
    persist_file_registry(file_registry)
    for client in clients:
        try:
            client.send_file_event(uid, chid, fid, name, len(data), is_jpg)
        except:
            print("Failed to send, kicking client")
            lost.append(client)
    disconnect_clients(lost)


def on_download(client, cid, fid, compressed):
    if fid in file_registry:
        data = read_file(fid)
        name = file_registry[fid][0]
        chid = file_registry[fid][4]
        if compressed:
            client.send_upload_compressed(fid, chid, name, data)
        else:
            client.send_upload(fid, chid, name, data)


def on_login(client, cid, username, password):
    print("login")
    if username in user_registry:
        real_password, uid = user_registry[username]
        if password == real_password:
            client.send_plaintext("Login successful. Welcome, user " + str(uid))
            client.send_accept()
            clients.append(client)
            client_ids[client] = uid
            id_name_map[max_user_uuid] = username
            client_handler.register(client, uid)
            init_client(client)
            broadcast_join(username, uid)
    else:
        client.send_plaintext("Invalid login, kicking...")
        client.send_reject()
    awaiting_login.remove(client)
    awaiting_handler.unregister(client)


def broadcast_join(username, uid):
    lost = []
    for client in clients:
        print("broadcast join")
        try:
            client.send_join(username, uid)
        except:
            lost.append(client)
    disconnect_clients(lost)


def on_registration(client, cid, username, password):
    print("registration")
    if username not in user_registry:
        client.send_accept()
        clients.append(client)
        global max_user_uuid
        max_user_uuid += 1
        client_ids[client] = max_user_uuid
        client_handler.register(client, max_user_uuid)
        user_registry[username] = (password, max_user_uuid)
        id_name_map[max_user_uuid] = username
        persist_user_registry(user_registry)
        init_client(client)
        broadcast_join(username, max_user_uuid)
    else:
        client.send_plaintext("Registration failed. Username unavailable.")
        client.send_reject("Username unavailable.")
    awaiting_login.remove(client)
    awaiting_handler.unregister(client)


def on_message(client, cid, uid, text, channel_id):
    lost = []
    print("[MESSAGE from", str(cid), "on", str(channel_id) + "]", text)
    for client in clients:
        try:
            client.send_message(cid, text, channel_id)
        except:
            print("Failed to send, kicking client")
            lost.append(client)
    disconnect_clients(lost)


awaiting_handler.set_login_handler(on_login)
awaiting_handler.set_registration_handler(on_registration)
client_handler.set_message_handler(on_message)
client_handler.set_upload_handler(on_upload)
client_handler.set_download_handler(on_download)


def broadcast_left(uid):
    lost = []
    for client in clients:
        try:
            client.send_left(uid)
        except:
            lost.append(client)
    disconnect_clients(lost)


def disconnect_clients(clients_to_remove):
    for client in clients_to_remove:
        client_handler.unregister(client)
        clients.remove(client)
    for client in clients_to_remove:
        broadcast_left(client_ids[client])


def start():
    server.setblocking(False)
    start = time.time()
    while True:
        try:
            c, ip = server.accept()
            client = Connection(c)
            client.send_plaintext("Connected! Awaiting authentication.")
            awaiting_login.append(client)
            awaiting_handler.register(client, 0)
        except:
            pass
        awaiting_handler.poll()
        client_handler.poll()
        if time.time() - start >= 300:
            start = time.time()
            print("[BACKUP]", time.gmtime(start))
            persist_file_registry(file_registry)



start()
