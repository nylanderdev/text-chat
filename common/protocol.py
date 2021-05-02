import math


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
