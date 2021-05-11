import unittest
from common.bit_util import *


class TestBitReadingAndWriting(unittest.TestCase):
    def test_integrity(self):
        b1 = [False, True, False, True, True, False]
        b2 = [0b1111_0000, 202, 12, 45, 111, 2]
        b3 = [True, True, False, True, True, False]
        writer = BitWriter()
        for bit in b1:
            writer.push(bit)
        for byte in b2:
            writer.push_byte(byte)
        for bit in b3:
            writer.push(bit)
        byte_list, bits = writer.get()
        reader = BitReader(byte_list, bits)
        self.assertEqual(writer.length(), reader.length())
        for i in range(0, len(b1)):
            bit = reader.pop()
            self.assertEqual(bit, b1[i])
        for i in range(0, len(b2)):
            byte = reader.pop_byte()
            self.assertEqual(byte, b2[i])
        for i in range(0, len(b3)):
            bit = reader.pop()
            self.assertEqual(bit, b3[i])


if __name__ == '__main__':
    unittest.main()
