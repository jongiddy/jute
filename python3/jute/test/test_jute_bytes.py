import unittest

from jute import Interface, Dynamic


class BytesLike(Interface):

    def __iter__(self):
        """bytes-like object must be iterable."""

    def __bytes__(self):
        """Return bytes representation."""


class BytesTestMixin:

    def get_test_object(self):
        return object()

    def test_bytes(self):
        bytes_like = self.get_test_object()
        self.assertEqual(bytes(bytes_like), b'foo')

    def test_getattr(self):
        bytes_like = self.get_test_object()
        self.assertEqual(getattr(bytes_like, '__bytes__')(), b'foo')

    def test_attribute(self):
        bytes_like = self.get_test_object()
        self.assertEqual(bytes_like.__bytes__(), b'foo')


class FooBytes(BytesLike.Provider):

    def __iter__(self):
        return iter(b'foo')

    def __bytes__(self):
        return b'foo'


class BytesInstanceTests(BytesTestMixin, unittest.TestCase):

    def get_test_object(self):
        return FooBytes()


class BytesInterfaceTests(BytesTestMixin, unittest.TestCase):

    def get_test_object(self):
        return BytesLike(FooBytes())


class FooBytesProxy(Dynamic.Provider):

    def provides_interface(self, interface):
        return interface.implemented_by(BytesLike)

    def __iter__(self):
        return iter(b'foo')

    def __bytes__(self):
        return b'foo'


class BytesDynamicInstanceTests(BytesTestMixin, unittest.TestCase):

    def get_test_object(self):
        return FooBytesProxy()


class BytesDynamicInterfaceTests(BytesTestMixin, unittest.TestCase):

    def get_test_object(self):
        return BytesLike(FooBytesProxy())


# __bytes__ is never optimised away, so generated version works as is

class GeneratedBytes(BytesLike.Provider):

    """A class that generates the __bytes__ method dynamically."""

    def __iter__(self):
        return iter(b'foo')

    def __getattr__(self, name):
        if name == '__bytes__':
            def f():
                return b'foo'
            return f
        raise AttributeError(name)


class GeneratedBytesInstanceTests(BytesTestMixin, unittest.TestCase):

    def get_test_object(self):
        return GeneratedBytes()


class GeneratedBytesInterfaceTests(BytesTestMixin, unittest.TestCase):

    def get_test_object(self):
        return BytesLike(GeneratedBytes())
