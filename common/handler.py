from .connection import *
from .protocol import TAG_EVENT, TAG_PLAINTEXT


# A tool for managing various connections in an event focused fashion
class ConnectionHandler:
    def __init__(self):
        self._connection_and_ids = []
        self._on_plaintext = lambda c, i, p: None
        self._on_login = lambda c, i, u, p: None
        self._on_message = lambda c, i, u, t: None
        self._on_download = lambda c, i, f, comp: None
        self._on_file = lambda c, i, u, f, n, l, img: None
        self._on_upload = lambda c, i, f, n, d: None
        self._on_accept = lambda c, i: None
        self._on_reject = lambda c, i, r: None
        self._on_registration = lambda c, i, u, p: None

    # Registers a connection to be handled and assigns it a non-unique id for future identification.
    def register(self, connection, connection_id):
        self._connection_and_ids.append((connection, connection_id))

    # Unregisters a connection
    def unregister(self, connection):
        for i in range(0, len(self._connection_and_ids)):
            if self._connection_and_ids[i] == connection:
                self._connection_and_ids.pop(i)

    # Poll connections and perform work. Nothing will happen unless this function is called regularly.
    def poll(self):
        for connection, conn_id in self._connection_and_ids:
            type_and_block = connection.recv()
            if type_and_block is None:
                continue
            if type_and_block[0] & TAG_COMPRESSED != 0:
                type_and_block[1] = protocol_decompress(type_and_block[1])
                type_and_block[0] &= 0b0111_1111
            if type_and_block is not None:
                if type_and_block[0] == TAG_PLAINTEXT:
                    plaintext, success = protocol_decode_plaintext(type_and_block[1])
                    if success:
                        self._on_plaintext(connection, conn_id, plaintext)
                elif type_and_block[0] == TAG_EVENT:
                    username, password, success_login = protocol_decode_login(type_and_block[1])
                    uid_msg, message, success_message = protocol_decode_message(type_and_block[1])
                    sender_uid, fileid, filename, filelen, image, success_file = \
                        protocol_decode_file_event(type_and_block[1])
                    username, password, success_registration = protocol_decode_registration(type_and_block[1])
                    if success_login:
                        self._on_login(connection, conn_id, username, password)
                    elif success_message:
                        self._on_message(connection, conn_id, uid_msg, message)
                    elif success_file:
                        self._on_file(connection, conn_id, sender_uid, fileid, filename, filelen, image)
                    elif success_registration:
                        self._on_registration(connection, conn_id, username, password)
                elif type_and_block[0] == TAG_DOWNLOAD:
                    fid, compressed, success = protocol_decode_download(type_and_block[1])
                    if success:
                        self._on_download(connection, conn_id, fid, compressed)
                elif type_and_block[0] == TAG_UPLOAD:
                    fid, name, data, success = protocol_decode_upload(type_and_block[1])
                    if success:
                        self._on_upload(connection, conn_id, fid, name, data)

    # Sets a function as handler for plaintext messages. Callback must take three parameters: connection, id,
    # and plaintext, containing the source connection object, its id, and the plaintext received, respectively.
    def set_plaintext_handler(self, callback):
        self._on_plaintext = callback

    # Sets a function as handler for login events. Callback must take four parameters: connection, id, username,
    # and password, containing the source connection object, its id, and the login information received, respectively.
    def set_login_handler(self, callback):
        self._on_login = callback

    # Sets a function as handler for uid-tagged messages. Callback must take four parameters: connection, id,
    # sender uid, and text containing the source connection object, its id, the sender uid, and the text received,
    # respectively.
    def set_message_handler(self, callback):
        self._on_message = callback

    # Sets a function as handler for file events. Callback must take seven parameters: connection, id,
    # sender_uid, fileid, filename, filelen, image containing the source connection object, its id,
    # the sender uid, file id, file name, file length and image flag, respectively.
    #     # received, respectively.
    def set_file_event_handler(self, callback):
        self._on_file = callback

    # Sets a function as handler for download requests. Callback must take four parameters: connection, id,
    # fileid, and compressed containing the source connection object, its id, the file id, and compression flag
    # received, respectively.
    def set_download_handler(self, callback):
        self._on_download = callback

    # Sets a function as handler for file uploads. Callback must take five parameters: connection, id,
    # fileid, filename, and data containing the source connection object, its id, the file id, the file name,
    # and file bytes received, respectively.
    def set_upload_handler(self, callback):
        self._on_upload = callback

    # Sets a function as handler for accept events. Callback must take two parameters: connection, and id,
    # containing the source connection object and its id.
    def set_accept_handler(self, callback):
        self._on_accept = callback

    # Sets a function as handler for accept events. Callback must take three parameters: connection, and id,
    # and reason, containing the source connection object, its id and the reason for rejection, respectively.
    def set_reject_handler(self, callback):
        self._on_reject = callback

    # Sets a function as handler for registration events. Callback must take four parameters: connection, and id,
    # username and password, containing the source connection object, its id and the requested username
    # and password respectively.
    def set_registration_handler(self, callback):
        self._on_registration = callback
