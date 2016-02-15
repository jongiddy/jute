import unittest

from jute import Attribute, InterfaceMetaclass, implements, Opaque


class DirTest(unittest.TestCase):

    def test_interface_dir(self):
        class MyInterface(metaclass=InterfaceMetaclass):

            def foo(self):
                """A method."""

            bar = Attribute()

        @implements(MyInterface)
        class MyClass:

            def foo(self):
                return 1

            bar = 3

            def not_included(self):
                """Not part of the interface."""

        obj = MyClass()
        inf = MyInterface(obj)
        self.assertEqual(sorted(dir(inf)), sorted(['foo', 'bar']))

    def test_opaque_dir(self):
        class MyInterface(Opaque):

            def foo(self):
                """A method."""

            bar = Attribute()

        @implements(MyInterface)
        class MyClass:

            def foo(self):
                return 1

            bar = 3

            def not_included(self):
                """Not part of the interface."""

        obj = MyClass()
        inf = MyInterface(obj)
        self.assertEqual(sorted(dir(inf)), sorted(['foo', 'bar']))
