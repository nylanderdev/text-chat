import unittest
from common.compression import *
from common.protocol import *


class TestCompression(unittest.TestCase):
    def test_hello_world(self):
        uncompressed = list("Hello world!!!!!".encode("utf-8"))
        self.assertEqual(decompress(compress(uncompressed)), uncompressed)

    def test_empty(self):
        self.assertEqual([], decompress(compress([])))

    def test_gzip_protocol(self):
        block = protocol_encode_plaintext("woooooooooop")
        compressed = protocol_compress(block)
        decompressed = protocol_decompress(block)
        self.assertEqual(block, decompressed)


if __name__ == '__main__':
    unittest.main()
