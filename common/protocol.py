import math


# Returns a header for a message of the specified length in the form of a byte array
def generate_header(length):
    bytes_required = math.ceil(math.log2(length + 1) / 8)
    length_bytes = list(length.to_bytes(bytes_required, "big"))
    bit_buffer = []
    header_bytes = []
    expected_header_byte_length = math.ceil(len(length_bytes) * 8 / 7)
    bit_padding_required = (expected_header_byte_length * 7 - len(length_bytes) * 8)
    for i in range(0, bit_padding_required):
        bit_buffer.append(False)
    for byte in length_bytes:
        bits = byte_to_bits(byte)
        for bit in bits:
            bit_buffer.append(bit)
            if len(bit_buffer) == 7:
                assembled_byte = seven_bits_to_byte(bit_buffer)
                header_bytes.append(assembled_byte)
                bit_buffer.clear()
    return header_bytes


def seven_bits_to_byte(bits):
    exponents = [1, 2, 4, 8, 16, 32, 64]
    byte = 0
    for position in range(0, 7):
        if bits[position]:
            byte += exponents[position]
    return byte


def byte_to_bits(byte):
    exponents = [1, 2, 4, 8, 16, 32, 64, 128]
    bits = []
    for position in range(0, 8):
        bit = exponents[7 - position] & byte
        bits.append(bit != 0)
    return bits