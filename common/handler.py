from .connection import *
from .protocol import TAG_EVENT, TAG_PLAINTEXT


# A tool for managing various connections in an event focused fashion
class ConnectionHandler:
    def __init__(self):
        self._connection_and_ids = []
        self._on_plaintext = lambda c, i, p: None
        self._on_login = lambda c, i, u, p: None

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
            if type_and_block[0] & TAG_COMPRESSED != 0:
                type_and_block[1] = protocol_decompress(type_and_block[1])
                type_and_block[0] &= 0b0111_1111
            if type_and_block is not None:
                if type_and_block[0] == TAG_PLAINTEXT:
                    plaintext, success = protocol_decode_plaintext(type_and_block[1])
                    if success:
                        self._on_plaintext(connection, conn_id, plaintext)
                elif type_and_block[0] == TAG_EVENT:
                    username, password, success = protocol_decode_login(type_and_block[1])
                    if success:
                        self._on_login(connection, conn_id, username, password)

    # Sets a function as handler for plaintext messages. Callback must take three parameters: connection, id,
    # and plaintext, containing the source connection object, its id, and the plaintext received, respectively.
    def set_plaintext_handler(self, callback):
        self._on_plaintext = callback

    # Sets a function as handler for login events. Callback must take four parameters: connection, id, username,
    # and password, containing the source connection object, its id, and the login information received, respectively.
    def set_login_handler(self, callback):
        self._on_login = callback
