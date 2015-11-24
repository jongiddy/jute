import unittest

from jute import Interface, RedefinedAttributeError


class GetAttributeTests(unittest.TestCase):

    def test_cannot_be_overridden(self):
        """Ensure ``__getattribute__`` cannot be over-ridden."""
        with self.assertRaises(RedefinedAttributeError):
            class RedefinesGetAttribute(Interface):

                def __getattribute__(self, name):
                    pass
