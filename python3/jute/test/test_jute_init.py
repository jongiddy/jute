import unittest

from jute import Interface, RedefinedAttributeError


class InitTests(unittest.TestCase):

    def test_cannot_be_overridden(self):
        """Ensure ``__init__`` cannot be over-ridden."""
        with self.assertRaises(RedefinedAttributeError):
            class RedefinesInit(Interface):

                def __init__(self):
                    pass
