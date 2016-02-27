import unittest

from jute import Opaque, implements


# Use a nested class, to ensure __repr__ provides correct name.
class Interfaces:

    class MyInterface(Opaque):

        pass


# Fully qualified name for interface is module name plus nested name
expected_interface_name = '{}.Interfaces.MyInterface'.format(__name__)


@implements(Interfaces.MyInterface)
class MyObject:

    def __repr__(self):
        return 'MyObject'


class ReprTests(unittest.TestCase):

    def test_repr(self):
        wrapper = Interfaces.MyInterface(MyObject())
        self.assertEqual(
            repr(wrapper),
            '<{}(MyObject)>'.format(expected_interface_name))
