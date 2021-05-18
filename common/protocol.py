import math
import gzip
from .compression import *
from .bit_util import *

TAG_UNDEFINED = 0b0000_0000
TAG_EVENT = 0b0100_0000
TAG_UPLOAD = 0b0010_0000
TAG_DOWNLOAD = 0b0001_0000
TAG_PLAINTEXT = 0b0000_0001
# COMPRESSED is masked on top of any other tag
# to indicate compression and should not be used
# on its own
TAG_COMPRESSED = 0b1000_0000


def protocol_encode_channel(channel_name, channel_id):
    return protocol_encode_event("channel", [channel_name, str(channel_id)])


def protocol_decode_channel(block):
    e_type, e_params, e_success = protocol_decode_event(block)
    if e_success and e_type == "channel" and len(e_params) == 2:
        channel_name = e_params[0]
        channel_id = int(e_params[1])
        return channel_name, channel_id, True
    return "", 0, False


def protocol_encode_left(uid):
    return protocol_encode_event("left", [str(uid)])


def protocol_decode_left(block):
    e_type, e_params, e_success = protocol_decode_event(block)
    if e_success and e_type == "left" and len(e_params) == 1:
        uid = int(e_params[0])
        return uid, True
    return 0, False


def protocol_encode_join(username, uid):
    return protocol_encode_event("join", [username, str(uid)])


def protocol_decode_join(block):
    e_type, e_params, e_success = protocol_decode_event(block)
    if e_success and e_type == "join" and len(e_params) == 2:
        username = e_params[0]
        uid = int(e_params[1])
        return username, uid, True
    return "", 0, False


def protocol_encode_accept():
    return protocol_encode_event("accept", [])


def protocol_encode_reject(reason=""):
    return protocol_encode_event("reject", [reason])


# Reads a protocol block as an accept event if possible, returning a boolean signifying success status
def protocol_decode_accept(block):
    event_type, params, success = protocol_decode_event(block)
    if success and event_type == "accept" and len(params) == 0:
        return True
    return False


# Reads a protocol block as a reject event if possible, returning a (string, bool) tuple
# containing the rejection reason and success status
def protocol_decode_reject(block):
    event_type, params, success = protocol_decode_event(block)
    if success and event_type == "reject" and len(params) == 1:
        return params[0], True
    return "", False


def protocol_encode_registration(username, password):
    return protocol_encode_event("registration", [username, password])


# Reads a protocol block as a registration event if possible, returning a (string, string, bool) tuple
# containing the result (user and password) and success status
def protocol_decode_registration(block):
    event_type, params, success = protocol_decode_event(block)
    if success and event_type == "registration" and len(params) == 2:
        return params[0], params[1], True
    return "", "", False


# Encodes a download request, using fileid (int), and compression flag (boolean)
def protocol_encode_download(file_id, compressed):
    block_data = bytearray(b"")
    block_data.extend(str(file_id).encode("utf-8"))
    block_data.extend(b":")
    if compressed:
        block_data.extend(b"True")
    else:
        block_data.extend(b"False")
    block = generate_header(len(block_data))
    block.append(TAG_DOWNLOAD)
    block.extend(block_data)
    return block


# Reads a protocol block as download request if possible, returning a (int, bool, bool) tuple
# containing the result (fileid, compression flag) and success status
def protocol_decode_download(block):
    header_end = find_header_end(block)
    block_type = block[header_end]
    if block_type == TAG_DOWNLOAD:
        block_data = block[header_end + 1:]
        colon_index = block_data.index(58)  # First colon
        file_id_bytes = block_data[:colon_index]
        file_id = int(bytes(file_id_bytes).decode("utf-8"))
        compression_flag_str = bytes(block_data[colon_index + 1:]).decode("utf-8")
        compression_flag = False
        if compression_flag_str == "True":
            compression_flag = True
        return file_id, compression_flag, True
    return 0, False, False


# Encodes an upload block, using fileid (int), and file data ([byte])
def protocol_encode_upload(file_id, chid, file_name, data):
    block_data = bytearray(b"")
    block_data.extend(str(file_id).encode("utf-8"))
    block_data.extend(b":")
    block_data.extend(str(chid).encode("utf-8"))
    block_data.extend(b":")
    block_data.extend(file_name.encode("utf-8"))
    block_data.extend(b":")
    block_data.extend(data)
    block = generate_header(len(block_data))
    block.append(TAG_UPLOAD)
    block.extend(block_data)
    return block


# Reads a protocol block as message if possible, returning a (int, string, [byte], bool) tuple
# containing the result (fileid, filename file_data) and success status
def protocol_decode_upload(block):
    header_end = find_header_end(block)
    block_type = block[header_end]
    if block_type == TAG_UPLOAD:
        block_data = block[header_end + 1:]
        colon_index = block_data.index(58)  # First colon
        colon_index2 = block_data[colon_index + 1:].index(58) + colon_index + 1  # Second colon
        colon_index3 = block_data[colon_index2 + 1:].index(58) + colon_index2 + 1  # Third colon
        file_id_bytes = block_data[:colon_index]
        channel_id_bytes = block_data[colon_index + 1:colon_index2]
        file_id = int(bytes(file_id_bytes).decode("utf-8"))
        channel_id = int(bytes(channel_id_bytes).decode("utf-8"))
        file_name_bytes = block_data[colon_index2 + 1:colon_index3]
        file_name = bytes(file_name_bytes).decode("utf-8")
        file_bytes = block_data[colon_index3 + 1:]
        return file_id, channel_id, file_name, file_bytes, True
    return 0, 0, [], False


# Encodes a file event notification, using sender_uid (int), channel_id (int),
# fileid (int), filename (string), filelen (int) and imageflag (boolean)
def protocol_encode_file_event(sender_uid, channel_id, fileid, filename, filelen, imageflag):
    return protocol_encode_event("file", [str(sender_uid), str(channel_id),
                                          str(fileid), filename, str(filelen), str(imageflag)])


# Reads a protocol block as message if possible, returning a (int, int, int, string, bool, bool) tuple
# containing the result (sender_uid, channel_id, fileid, filename, filelen and image flag) and success status
def protocol_decode_file_event(block):
    event_type, params, succeeded = protocol_decode_event(block)
    if succeeded and event_type == "file" and len(params) == 6:
        try:
            uid = int(params[0])
            channel_id = int(params[1])
            fileid = int(params[2])
            filename = params[3]
            filelen = int(params[4])
            image = params[5] == "True"
            return uid, channel_id, fileid, filename, filelen, image, True
        except:  # Catch any parsing errors
            pass
    return 0, 0, 0, "", 0, False, False


# Encodes a plaintext message from the sender. Use sender_uid=0 for messages to the server
def protocol_encode_message(sender_uid, message_text, channel_id=0):
    return protocol_encode_event("message", [str(sender_uid), str(channel_id), message_text])


# Reads a protocol block as message if possible, returning a (int, string, bool) tuple
# containing the result (uid and message text) and success status
def protocol_decode_message(block):
    event_type, params, succeeded = protocol_decode_event(block)
    if succeeded and event_type == "message" and len(params) == 3:
        try:
            uid = int(params[0])
            message_text = params[2]
            channel_id = int(params[1])
            return uid, message_text, channel_id, True
        except:  # Catch any parsing errors
            pass
    return 0, "", 0, False


# Encodes a generic with the given params and tags it as the given event type
def protocol_encode_event(event_type, params):
    event_bytes = bytearray(event_type.encode("utf-8"))
    for param in params:
        event_bytes.extend(b":")
        event_bytes.extend(bytes(str(len(param)).encode("utf-8")))
    event_bytes.extend(b"=")
    for param in params:
        event_bytes.extend(bytes(str(param).encode("utf-8")))
    block = generate_header(len(event_bytes))
    block.append(TAG_EVENT)
    block.extend(event_bytes)
    return block


# Reads a protocol block as an event if possible, returning a (string, [string], bool) tuple
# containing the result (event type and params) and success status
def protocol_decode_event(block):
    header_end = find_header_end(block)
    block_type = block[header_end]
    if block_type == TAG_EVENT:
        event_string = bytes(block[header_end + 1:]).decode("utf-8")
        param_lengths_end = event_string.find("=")
        if param_lengths_end >= 0:
            event_type_end = event_string.find(":")
            if event_type_end == -1:
                # No params
                event_type = event_string[:param_lengths_end]
                return event_type, [], True
            event_type = event_string[:event_type_end]
            param_lengths_str = event_string[event_type_end + 1:param_lengths_end]
            params_str = event_string[param_lengths_end + 1:]
            param_lengths = param_lengths_str.split(":")
            params = []
            cursor = 0
            for length in param_lengths:
                try:
                    length = int(length)
                    param = params_str[cursor:cursor + length]
                    cursor += length
                    params.append(param)
                except:
                    return "", [], False
            return event_type, params, True
    return "", [], False


# Compresses a block into a special compressed protocol block, returns block if block is already tagged as compressed
def protocol_compress(block):
    header_end = find_header_end(block)
    block_type = block[header_end]
    if block_type & TAG_COMPRESSED != 0:
        # Already compressed
        return block
    data = block[header_end + 1:]
    compressed_type = block_type | TAG_COMPRESSED
    compressed_data = list(gzip.compress(bytes(data)))
    compressed_block = generate_header(len(compressed_data))
    compressed_block.append(compressed_type)
    compressed_block.extend(compressed_data)
    return compressed_block


# Decompresses a block into an uncompressed block, returns block if block is not compressed
def protocol_decompress(block):
    header_end = find_header_end(block)
    block_type = block[header_end]
    if block_type & TAG_COMPRESSED == 0:
        # Uncompressed
        return block
    data = block[header_end + 1:]
    decompressed_type = block_type & 0b0111_1111
    decompressed_data = list(gzip.decompress(bytes(data)))
    decompressed_block = generate_header(len(decompressed_data))
    decompressed_block.append(decompressed_type)
    decompressed_block.extend(decompressed_data)
    return decompressed_block


def protocol_encode_login(username, password):
    return protocol_encode_event("login", [username, password])


# Reads a protocol block as a login event if possible, returning a (string, string, bool) tuple
# containing the result (user and password) and success status
def protocol_decode_login(block):
    event_type, params, success = protocol_decode_event(block)
    if success and event_type == "login" and len(params) == 2:
        return params[0], params[1], True
    return "", "", False


# Generates a protocol block containing a plaintext message encoded in UTF-8
def protocol_encode_plaintext(plaintext):
    message_bytes = plaintext.encode("utf-8")
    return protocol_block(TAG_PLAINTEXT, message_bytes)


# Reads a protocol block as plaintext if possible, returning a (string, bool) tuple
# containing the result and success status
def protocol_decode_plaintext(block):
    header_length = find_header_end(block)
    header = block[:header_length]
    message_length = interpret_header(header)
    if len(block) != header_length + 1 + message_length:
        return "", False
    tag = block[header_length]
    if tag != TAG_PLAINTEXT:
        return "", False
    plaintext = bytes(block[header_length + 1:]).decode("utf-8")
    return plaintext, True


# Generates a protocol block from a type tag and a message byte array
def protocol_block(tag, message_bytes):
    block = generate_header(len(message_bytes))
    block.append(tag)
    block.extend(message_bytes)
    return block


# Finds the first index of a protocol block that is not a header byte, returning -1 if no end is found
def find_header_end(block):
    for i in range(0, len(block)):
        if block[i] & 0b1000_0000 != 0:
            return i + 1
    return -1


# Returns a header for a message of the specified length in the form of a byte array
def generate_header(length):
    # Quick case for empty messages, if required
    if length == 0:
        return [128]
    bytes_required = math.ceil(math.log2(length + 1) / 8)
    length_bytes = list(length.to_bytes(bytes_required, "big"))
    bit_padding_required = 7 - bytes_required * 8 % 7
    bit_buffer = [False] * bit_padding_required
    header_bytes = []
    for byte in length_bytes:
        bits = byte_to_bits(byte)
        for bit in bits:
            bit_buffer.append(bit)
            if len(bit_buffer) == 7:
                assembled_byte = seven_bits_to_byte(bit_buffer)
                # Skip any leading zero bytes, they are unnecessary
                if len(header_bytes) > 0 or assembled_byte != 0:
                    header_bytes.append(assembled_byte)
                bit_buffer.clear()
    # Toggle the MSB of the last byte
    header_bytes[-1] += 0b1000_0000
    return header_bytes


# Returns the length represented by a byte array header
def interpret_header(header):
    bit_buffer = []
    decoded_header_bytes = []
    for byte in header:
        # Ignore MSB
        byte &= 0b0111_1111
        bits = byte_to_bits(byte)
        for bit in bits:
            bit_buffer.append(bit)
            if len(bit_buffer) == 8:
                assembled_byte = eight_bits_to_byte(bit_buffer)
                bit_buffer.clear()
                decoded_header_bytes.append(assembled_byte)
    length = big_endian_to_int(decoded_header_bytes)
    return length
