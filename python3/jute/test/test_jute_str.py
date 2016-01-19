import unittest

from jute import Interface, Dynamic, implements


class StringLike(Interface):

    def __str__(self):
        """Return string representation."""


class StringTestMixin:

    def get_test_object(self):
        return object()

    def test_str(self):
        string_like = self.get_test_object()
        self.assertEqual(str(string_like), 'foo')

    def test_getattr(self):
        string_like = self.get_test_object()
        self.assertEqual(getattr(string_like, '__str__')(), 'foo')

    def test_attribute(self):
        string_like = self.get_test_object()
        self.assertEqual(string_like.__str__(), 'foo')


@implements(StringLike)
class FooString:

    def __str__(self):
        return 'foo'


class StrInstanceTests(StringTestMixin, unittest.TestCase):

    def get_test_object(self):
        return FooString()


class StrInterfaceTests(StringTestMixin, unittest.TestCase):

    def get_test_object(self):
        return StringLike(FooString())


@implements(Dynamic)
class FooStringProxy:

    def provides_interface(self, interface):
        return interface.implemented_by(StringLike)

    def __str__(self):
        return 'foo'


class StrDynamicInstanceTests(StringTestMixin, unittest.TestCase):

    def get_test_object(self):
        return FooStringProxy()


class StrDynamicInterfaceTests(StringTestMixin, unittest.TestCase):

    def get_test_object(self):
        return StringLike(FooStringProxy())


@implements(StringLike)
class GeneratedStr:

    """A class that generates the __str__ method dynamically."""

    def __getattr__(self, name):
        if name == '__str__':
            def f():
                return 'foo'
            return f
        raise AttributeError(name)


class GeneratedStrTestMixin(StringTestMixin):

    """Test __str__ for a provider that generates __str__.

    Using a dynamically generated __str__ method fails, no matter how
    __str__ is accessed.  To minimise surprise, the interface should
    behave the same way as a normal instance.

    Note, that getting the attribute succeeds otherwise.
    """

    def test_getattr(self):
        string_like = self.get_test_object()
        self.assertNotEqual(getattr(string_like, '__str__')(), 'foo')

    def test_attribute(self):
        string_like = self.get_test_object()
        self.assertNotEqual(string_like.__str__(), 'foo')

    def test_str(self):
        string_like = self.get_test_object()
        self.assertNotEqual(str(string_like), 'foo')


class GeneratedStrInstanceTests(GeneratedStrTestMixin, unittest.TestCase):

    def get_test_object(self):
        return GeneratedStr()


class GeneratedStrInterfaceTests(GeneratedStrTestMixin, unittest.TestCase):

    def get_test_object(self):
        return StringLike(GeneratedStr())
