import unittest

from jute import Opaque, InvalidAttributeName


class SpecialTests(unittest.TestCase):

    def test_init(self):
        with self.assertRaises(InvalidAttributeName):
            class AnInterface(Opaque):

                def __init__(self):
                    pass

    def test_repr(self):
        with self.assertRaises(InvalidAttributeName):
            class AnInterface(Opaque):

                def __repr__(self):
                    pass

    def test_dir(self):
        with self.assertRaises(InvalidAttributeName):
            class AnInterface(Opaque):

                def __dir__(self):
                    pass

    def test_getattribute(self):
        with self.assertRaises(InvalidAttributeName):
            class AnInterface(Opaque):

                def __getattribute__(self, name):
                    pass

    def test_getattr(self):
        with self.assertRaises(InvalidAttributeName):
            class AnInterface(Opaque):

                def __getattr__(self, name):
                    pass

    def test_setattr(self):
        with self.assertRaises(InvalidAttributeName):
            class AnInterface(Opaque):

                def __setattr__(self, name, value):
                    pass

    def test_delattr(self):
        with self.assertRaises(InvalidAttributeName):
            class AnInterface(Opaque):

                def __delattr__(self):
                    pass
