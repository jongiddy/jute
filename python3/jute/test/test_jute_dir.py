import unittest

from jute import Interface, implements


class MyInterface(Interface):

    def foo(self):
        """A method."""

    bar = int  # an attribute


@implements(MyInterface)
class MyClass:

    def foo(self):
        return 1

    bar = 3

    def not_included(self):
        """Not part of the interface."""


class DirTest(unittest.TestCase):

    def test_interface_dir(self):
        obj = MyClass()
        interface_attibutes = dir(Interface(obj))
        inf = MyInterface(obj)
        self.assertEqual(
            sorted(dir(inf)),
            sorted(['foo', 'bar'] + interface_attibutes)
        )
