import unittest
from common.protocol import *


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

    def test_integrity_hello_world_compressed(self):
        text = "Hello world!"
        block = protocol_encode_plaintext(text)
        compressed = protocol_compress(block)
        decompressed = protocol_decompress(compressed)
        text_read, succeeded = protocol_decode_plaintext(decompressed)
        self.assertTrue(succeeded)
        self.assertEqual(text_read, text)

class TestProtocolEvent(unittest.TestCase):
    def test_integrity_login_event_as_generic(self):
        block = protocol_encode_event("login", ["username", "password"])
        event_type, params, succeeded = protocol_decode_event(block)
        self.assertTrue(succeeded)
        self.assertEqual(event_type, "login")
        self.assertEqual(params, ["username", "password"])

    def test_integrity_params_with_colon(self):
        block = protocol_encode_event("login", ["username:", "password"])
        event_type, params, succeeded = protocol_decode_event(block)
        self.assertTrue(succeeded)
        self.assertEqual(event_type, "login")
        self.assertEqual(params, ["username:", "password"])

    def test_integrity_login_event_as_login(self):
        block = protocol_encode_login("username", "password")
        username, password, succeeded = protocol_decode_login(block)
        self.assertTrue(succeeded)
        self.assertEqual(username, "username")
        self.assertEqual(password, "password")


if __name__ == '__main__':
    unittest.main()
