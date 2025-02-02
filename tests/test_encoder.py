import unittest
from simulator.encoder import *

class TestEncoder(unittest.TestCase):
    def test_pack_bits_little_endian(self):
        data = bytearray(8)
        pack_bits(0x123, 0, 12, True, data)
        self.assertEqual(data[0], 0x23)
        self.assertEqual(data[1], 0x01)

    def test_pack_bits_big_endian(self):
        data = bytearray(8)
        pack_bits(0b1010, 4, 4, False, data)
        self.assertEqual(data[0], 0b10100000)