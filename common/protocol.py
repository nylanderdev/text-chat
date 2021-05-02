import math

TAG_UNDEFINED = 0b0000_0000
TAG_PLAINTEXT = 0b0000_0001
# COMPRESSED is masked on top of any other tag
# to indicate compression and should not be used
# on its own
TAG_COMPRESSED = 0b1000_0000


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


def big_endian_to_int(be_bytes):
    accumulator = 0
    for byte in be_bytes:
        accumulator *= 128
        accumulator += byte
    return accumulator


def seven_bits_to_byte(bits):
    exponents = [64, 32, 16, 8, 4, 2, 1]
    byte = 0
    for position in range(0, 7):
        if bits[position]:
            byte += exponents[position]
    return byte


def eight_bits_to_byte(bits):
    return (128 if bits[0] else 0) + seven_bits_to_byte(bits[1:])


def byte_to_bits(byte):
    exponents = [128, 64, 32, 16, 8, 4, 2, 1]
    bits = []
    for position in range(0, 8):
        bit = exponents[position] & byte
        bits.append(bit != 0)
    return bits
