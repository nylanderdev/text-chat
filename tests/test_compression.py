import unittest
from common.compression import *


class TestCompression(unittest.TestCase):
    def test_hello_world(self):
        uncompressed = list("Hello world!!!!!".encode("utf-8"))
        self.assertEqual(decompress(compress(uncompressed)), uncompressed)

    def test_empty(self):
        self.assertEqual([], decompress(compress([])))


if __name__ == '__main__':
    unittest.main()
