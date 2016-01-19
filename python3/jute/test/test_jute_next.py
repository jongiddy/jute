import unittest

from jute import Interface, Dynamic, implements


# Note that an Iterator is a syntactic sub-class of Iterable, but it is
# not (necessarily) a semantic sub-class.  Although there is no absolute
# rule, an iterator is usually a non-restartable "input iterator", while
# an iterable is a restartable "forward iterator".  In general, neither
# of them can be used in all code that works with the other.

class Iterable(Interface):

    def __iter__(self):
        """Get an iterator."""


class Iterator(Interface):

    def __iter__(self):
        """Handle for loops."""

    def __next__(self):
        """Get the next item."""


class IterTestMixin:

    def get_test_object(self):
        return object()

    def test_next(self):
        iterator = self.get_test_object()
        self.assertEqual(next(iterator), 0)

    def test_getattr(self):
        iterator = self.get_test_object()
        self.assertEqual(getattr(iterator, '__next__')(), 0)

    def test_attribute(self):
        iterator = self.get_test_object()
        self.assertEqual(iterator.__next__(), 0)


@implements(Iterator)
class LotsOfZeros:

    def __iter__(self):
        return self

    def __next__(self):
        return 0


class NextInstanceTests(IterTestMixin, unittest.TestCase):

    def get_test_object(self):
        return LotsOfZeros()


class NextInterfaceTests(IterTestMixin, unittest.TestCase):

    def get_test_object(self):
        return Iterator(LotsOfZeros())


@implements(Dynamic)
class IteratorProxy:

    def __init__(self, wrapped_iterator):
        self.wrapped = wrapped_iterator

    def provides_interface(self, interface):
        return interface.implemented_by(Iterator)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.wrapped)


class NextDynamicInstanceTests(IterTestMixin, unittest.TestCase):

    def get_test_object(self):
        return IteratorProxy(LotsOfZeros())


class NextDynamicInterfaceTests(IterTestMixin, unittest.TestCase):

    def get_test_object(self):
        return Iterator(IteratorProxy(LotsOfZeros()))


@implements(Iterator)
class GeneratedNext:

    """A class that generates the __next__ method dynamically."""

    def __getattr__(self, name):
        if name == '__next__':
            def f():
                return 0
            return f
        raise AttributeError(name)

    def __iter__(self):
        return self


class GeneratedNextTestMixin(IterTestMixin):

    """Test __next__ for a provider that generates __next__.

    Using a dynamically generated __next__ method fails when using `next`
    or `for` on an object.  To minimise surprise, the interface should
    behave the same way as a normal instance.

    Note, that getting the attribute succeeds otherwise.
    """

    def test_next(self):
        iterator = self.get_test_object()
        with self.assertRaises(TypeError):
            next(iterator)


class GeneratedNextInstanceTests(GeneratedNextTestMixin, unittest.TestCase):

    def get_test_object(self):
        return GeneratedNext()


class GeneratedNextInterfaceTests(GeneratedNextTestMixin, unittest.TestCase):

    def get_test_object(self):
        return Iterator(GeneratedNext())
