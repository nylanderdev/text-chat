import unittest
from protocol import generate_header, interpret_header


class TestProtocol(unittest.TestCase):
    # Make sure headers are correctly constructed and interpreted for small (~10K) lengths
    def test_integrity_small(self):
        for n in range(0, 10_000):
            self.assertEqual(interpret_header(generate_header(n)), n)

    # Make sure headers are correctly constructed and interpreted for big (~1B) lengths
    def test_integrity_big(self):
        for n in range(1_000_000_000, 1_000_010_000):
            self.assertEqual(interpret_header(generate_header(n)), n)


if __name__ == '__main__':
    unittest.main()
