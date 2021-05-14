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

    def test_integrity_registration_event(self):
        block = protocol_encode_registration("username", "password")
        username, password, succeeded = protocol_decode_registration(block)
        self.assertTrue(succeeded)
        self.assertEqual(username, "username")
        self.assertEqual(password, "password")

    def test_integrity_accept_event(self):
        block = protocol_encode_accept()
        succeeded = protocol_decode_accept(block)
        self.assertTrue(succeeded)

    def test_integrity_reject_event(self):
        block = protocol_encode_reject("bad egg")
        reason, succeeded = protocol_decode_reject(block)
        self.assertTrue(succeeded)
        self.assertEqual(reason, "bad egg")

    def test_integrity_message_event(self):
        block = protocol_encode_message(123, "hello world!?")
        uid, message, succeeded = protocol_decode_message(block)
        self.assertTrue(succeeded)
        self.assertEqual(uid, 123)
        self.assertEqual(message, "hello world!?")

    def test_integrity_file_event(self):
        block = protocol_encode_file_event(2, 3, "spaceship.gol", 21312, False)
        uid, fid, filename, filelen, image, succeeded = protocol_decode_file_event(block)
        self.assertTrue(succeeded)
        self.assertEqual(uid, 2)
        self.assertEqual(fid, 3)
        self.assertEqual(filename, "spaceship.gol")
        self.assertEqual(filelen, 21312)
        self.assertFalse(image)


class TestProtocolUploadDownload(unittest.TestCase):
    def test_integrity_upload(self):
        data = [23, 53, 53, 78, 34, 0, 0, 0, 0, 1, 0]
        block = protocol_encode_upload(234, "hello.world", data)
        file_id, filename, data_read, succeeded = protocol_decode_upload(block)
        self.assertTrue(succeeded)
        self.assertEqual(file_id, 234)
        self.assertEqual(filename, "hello.world")
        self.assertEqual(data, data_read)

    def test_integrity_download(self):
        fileid = 342342
        compressed = True
        block = protocol_encode_download(fileid, compressed)
        read_fileid, read_compressed, succeeded = protocol_decode_download(block)
        self.assertTrue(succeeded)
        self.assertEqual(read_fileid, fileid)
        self.assertEqual(compressed, read_compressed)


if __name__ == '__main__':
    unittest.main()
