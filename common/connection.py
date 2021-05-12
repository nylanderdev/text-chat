from .protocol import *
import socket


class Connection:
    def __init__(self, soc):
        self._message_length_expected = -1
        self._socket = soc
        self._byte_buffer = []
        self._header_buffer = []
        self._messages = []
        self._messages_by_type = {}
        self._socket.setblocking(False)
        self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    # Receives an event (string, [string])=(type, params) if available, else returns None
    def recv_event(self):
        self._poll()
        possible_event = self._pop_by_type(TAG_EVENT)
        if possible_event is not None:
            event_type, params, success = protocol_decode_event(possible_event[1])
            if success:
                return event_type, params
        return None

    # Receives a download request (int, boolean)=(fileid, compressed?) if available, else returns None
    def recv_download_request(self):
        self._poll()
        possible_download = self._pop_by_type(TAG_DOWNLOAD)
        if possible_download is not None:
            fid, compressed, success = protocol_decode_download(possible_download[1])
            if success:
                return fid, compressed
        return None

    # Receives an upload (int, [byte])=(fileid, data) if available, else returns None
    def recv_upload(self):
        self._poll()
        possible_upload = self._pop_by_type(TAG_UPLOAD)
        if possible_upload is not None:
            fid, data, success = protocol_decode_upload(possible_upload[1])
            if success:
                return fid, data
        return None

    # Sends a uid tagged message (counts as an event)
    def send_message(self, uid, msg_text):
        self.send(protocol_encode_message(uid, msg_text))

    # Sends a compressed upload with fileid int and file data [bytes]
    def send_upload_compressed(self, fid, data):
        self.send(protocol_compress(protocol_encode_upload(fid, data)))

    # Sends an upload with fileid int and file data [bytes]
    def send_upload(self, fid, data):
        self.send(protocol_encode_upload(fid, data))

    # Sends a download request with fileid and compression flag
    def send_download_request(self, fid, compressed):
        self.send(protocol_encode_download(fid, compressed))

    # Sends a generic event
    def send_event(self, event_type, params):
        self.send(protocol_encode_event(event_type, params))

    # Sends a login event
    def send_login(self, username, password):
        self.send(protocol_encode_login(username, password))

    # Sends a file event with sender userid, fileid, filename, filelen, and image flag
    def send_file_event(self, uid, fid, filename, filelen, imageflag):
        self.send(protocol_encode_file_event(uid, fid, filename, filelen, imageflag))

    # Receives a plaintext message, if available, else returns None
    def recv_plaintext(self):
        self._poll()
        possible_message = self._pop_by_type(TAG_PLAINTEXT)
        if possible_message is not None:
            plaintext, success = protocol_decode_plaintext(possible_message[1])
            if success:
                return plaintext
        return None

    # Sends the given string as a plaintext message
    def send_plaintext(self, plaintext):
        self.send(protocol_encode_plaintext(plaintext))

    # Receives an event (a tuple containing an event type and an argument list), if available, else returns None
    def recv_event(self):
        self._poll()
        possible_event = self._pop_by_type(TAG_EVENT)
        if possible_event is not None:
            event_type, params, success = protocol_decode_event(possible_event[1])
            if success:
                return event_type, params
        return None

    def send_event(self, event_type, params):
        self.send(protocol_encode_event(event_type, params))

    # Sends a raw list of bytes
    def send(self, block):
        self._socket.send(bytes(block))

    # Receives a tuple containing the Type tag byte and a protocol block, if available, else returns None
    def recv(self):
        if len(self._messages) == 0:
            self._poll()
        if len(self._messages) > 0:
            return self._messages.pop(0)
        else:
            return None

    def _pop_by_type(self, type_mask):
        if type_mask in self._messages_by_type:
            if len(self._messages_by_type[type_mask]) > 0:
                message = self._messages_by_type[type_mask].pop(0)
                self._messages.remove(message)
                if type_mask & TAG_COMPRESSED != 0:
                    message = protocol_decompress(message)
                    type_mask |= 0b0111_1111
                return message
        return None

    def _put_message(self, type_and_message):
        self._messages.append(type_and_message)
        the_type = type_and_message[0]
        if the_type not in self._messages_by_type:
            self._messages_by_type[the_type & 0b0111_1111] = []
        self._messages_by_type[the_type & 0b0111_1111].append(type_and_message)

    def _pop_message(self):
        if len(self._messages) > 0:
            message_type = self._messages[0]
            message = self._messages.pop(0)
            self._messages_by_type[message_type & 0b0111_1111].pop(0)
            return message
        return None

    def _recalculate_message_length(self):
        if len(self._byte_buffer) == 0:
            self._message_length_expected = -1
        else:
            header_end = find_header_end(self._byte_buffer)
            if header_end >= 0:
                header = self._byte_buffer[:header_end]
                length = interpret_header(header)
                self._message_length_expected = length
                self._header_buffer.extend(header)
                self._byte_buffer = self._byte_buffer[header_end:]

    def _poll(self):
        if len(self._messages) == 0:
            if self._message_length_expected < 0:
                self._poll_for_header()
            else:
                self._poll_for_message()
        else:
            self._messages.pop()

    def _poll_for_header(self):
        READ_LEN = 1024
        try:
            response = self._socket.recv(READ_LEN)
        except socket.error:
            # todo: better error handling
            return
        self._byte_buffer.extend(response)
        header_end = find_header_end(self._byte_buffer)
        header = self._byte_buffer[:header_end]
        message_length = interpret_header(header)
        self._header_buffer = header
        self._message_length_expected = message_length
        self._byte_buffer = self._byte_buffer[header_end:]

    def _poll_for_message(self):
        bytes_missing = self._message_length_expected + 1 - len(self._byte_buffer)
        if bytes_missing > 0:
            try:
                response = self._socket.recv(bytes_missing)
            except socket.error:
                # todo: better error handling
                return
            self._byte_buffer.extend(response)
        bytes_missing = self._message_length_expected + 1 - len(self._byte_buffer)
        if bytes_missing <= 0:
            # Got all missing bytes
            type_and_message = self._byte_buffer[:self._message_length_expected + 1]
            block = []
            block.extend(self._header_buffer)
            block.extend(type_and_message)
            self._header_buffer.clear()
            self._put_message((self._byte_buffer[0], block))
            self._byte_buffer = self._byte_buffer[self._message_length_expected + 1:]
            self._message_length_expected = -1
            self._recalculate_message_length()
