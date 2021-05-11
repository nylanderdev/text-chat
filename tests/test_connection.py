import unittest
import threading
import socket
from common.connection import Connection


class MessageServerThread(threading.Thread):
    def __init__(self, message, count):
        super().__init__()
        self._message = message
        self._count = count

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("0.0.0.0", 1337))
        s.listen()
        c, _ = s.accept()
        conn = Connection(c)
        for _ in range(0, self._count):
            conn.send_plaintext(self._message)
        c.shutdown(socket.SHUT_RDWR)
        c.close()
        return


class EventServerThread(threading.Thread):
    def __init__(self, count):
        super().__init__()
        self._count = count

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("0.0.0.0", 1338))
        s.listen()
        c, _ = s.accept()
        conn = Connection(c)
        for _ in range(0, self._count):
            conn.send_event("login", ["username", "password"])
        c.shutdown(socket.SHUT_RDWR)
        c.close()
        return


class TestConnection(unittest.TestCase):
    def _test_n_messages_successful(self, n):
        message = "Hello world!"
        MessageServerThread(message, n).start()
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("localhost", 1337))
        conn = Connection(client)
        while n > 0:
            try:
                received_text = conn.recv_plaintext()
                self.assertEqual(message, received_text)
                n -= 1
            except Exception:
                pass
        client.shutdown(socket.SHUT_RDWR)
        client.close()

    def _test_n_events_successful(self, n):
        EventServerThread(n).start()
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("localhost", 1338))
        conn = Connection(client)
        while n > 0:
            try:
                event = conn.recv_event()
                self.assertEqual(("login", ["username", "password"]), event)
                n -= 1
            except Exception:
                pass
        client.shutdown(socket.SHUT_RDWR)
        client.close()

    def test_100_messages_successful(self):
        self._test_n_messages_successful(100)

    def test_100_events_successful(self):
        self._test_n_events_successful(100)


if __name__ == '__main__':
    unittest.main()
