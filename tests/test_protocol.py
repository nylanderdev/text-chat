import unittest
from common.protocol import generate_header, interpret_header, protocol_encode_plaintext, protocol_decode_plaintext


class TestProtocolHeader(unittest.TestCase):

    # Make sure headers are correctly constructed and interpreted for small (~10K) lengths
    def test_integrity_small(self):
        for n in range(0, 10_000):
            self.assertEqual(interpret_header(generate_header(n)), n)

    # Make sure headers are correctly constructed and interpreted for big (~1B) lengths
    def test_integrity_big(self):
        for n in range(1_000_000_000, 1_000_010_000):
            self.assertEqual(interpret_header(generate_header(n)), n)


class TestProtocolPlaintext(unittest.TestCase):
    def test_integrity_hello_world(self):
        text = "Hello world!"
        text_read, succeeded = (protocol_decode_plaintext(protocol_encode_plaintext(text)))
        self.assertTrue(succeeded)
        self.assertEqual(text_read, text)


if __name__ == '__main__':
    unittest.main()
