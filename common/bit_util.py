# A tool for writing a byte sequence bit by bit
class BitWriter:
    def __init__(self):
        self._whole_bytes = []
        self._bit_buffer = []

    # Push a boolean as a bit (True=1, False=0)
    def push(self, bit):
        self._bit_buffer.append(bit)
        if len(self._bit_buffer) == 8:
            byte = eight_bits_to_byte(self._bit_buffer)
            self._whole_bytes.append(byte)
            self._bit_buffer.clear()

    # Pushes all bits in a byte
    def push_byte(self, byte):
        for bit in byte_to_bits(byte):
            self.push(bit)

    # Gets all bits written as a byte array of all assembled bits as well as a boolean array of any remaining bits
    # that couldn't be evenly packed into a byte
    def get(self):
        bytes_ = self._whole_bytes.copy()
        bits = self._bit_buffer.copy()
        return bytes_, bits

    # Returns the number of bits in the writer
    def length(self):
        return 8 * len(self._whole_bytes) + len(self._bit_buffer)


# A tool for reading a byte sequence bit by bit
class BitReader:
    def __init__(self, byte_list, bits=None):
        if bits is None:
            bits = []
        self._head_bits = []
        self._mid_bytes = byte_list.copy()
        self._tail_bits = bits.copy()

    # Pops a bit as a boolean
    def pop(self):
        if len(self._head_bits) == 0:
            if len(self._mid_bytes) > 0:
                byte = self._mid_bytes.pop(0)
                for bit in byte_to_bits(byte):
                    self._head_bits.append(bit)
                return self._head_bits.pop(0)
            elif len(self._tail_bits) > 0:
                self._head_bits = self._tail_bits.copy()
                self._tail_bits.clear()
                return self._head_bits.pop(0)
            else:
                return None
        else:
            return self._head_bits.pop(0)

    # Pops a byte from eight bits, if available
    def pop_byte(self):
        if self.length() >= 8:
            bits = []
            for _ in range(0, 8):
                bits.append(self.pop())
            return eight_bits_to_byte(bits)
        return None

    # Returns the number of bits in the reader
    def length(self):
        return len(self._head_bits) + 8 * len(self._mid_bytes) + len(self._tail_bits)


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
