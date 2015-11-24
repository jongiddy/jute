import unittest

from jute import Interface, implements, RedefinedAttributeError


# Use a nested class, to ensure __repr__ provides correct name.
class Interfaces:

    class MyInterface(Interface):

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

    def test_cannot_be_overridden(self):
        """Ensure ``__repr__`` cannot be over-ridden.

        If ``__repr__`` is re-defined in an interface (sub-class of Interface),
        it would forward to the wrapped object.  Since ``__repr__`` is mainly
        used for debugging, keep the information that the object is a wrapped
        interface object.
        """
        with self.assertRaises(RedefinedAttributeError):
            class DefinesRepr(Interface):

                def __repr__(self):
                    pass
