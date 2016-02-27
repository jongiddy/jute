import unittest

from jute import Attribute, Opaque, implements, underlying_object


class ISettable(Opaque):

    def __setattr__(self, name, value):
        """Set an attribute."""

    foo = Attribute()


class SetAttrTestMixin:

    def get_test_object(self):
        return object()

    def test_dot_name(self):
        setdash = self.get_test_object()
        setdash.foo = 1
        self.assertTrue(hasattr(underlying_object(setdash), 'foo_'))
        self.assertEqual(underlying_object(setdash).foo_, 1)

    def test_setattr_function(self):
        setdash = self.get_test_object()
        setattr(setdash, 'foo', 1)
        self.assertTrue(hasattr(underlying_object(setdash), 'foo_'))
        self.assertEqual(underlying_object(setdash).foo_, 1)

    def test_direct(self):
        setdash = self.get_test_object()
        setdash.__setattr__('foo', 1)
        self.assertTrue(hasattr(underlying_object(setdash), 'foo_'))
        self.assertEqual(underlying_object(setdash).foo_, 1)


@implements(ISettable)
class SetDash:

    def __setattr__(self, name, value):
        object.__setattr__(self, name + '_', value)

    foo = 5


class SetAttrInstanceTests(SetAttrTestMixin, unittest.TestCase):

    def get_test_object(self):
        return SetDash()


class SetAttrInterfaceTests(SetAttrTestMixin, unittest.TestCase):

    def get_test_object(self):
        return ISettable(SetDash())


# setattr() ignores dynamically generated __setattr__, so interface must
# do the same

class GeneratedTestMixin:

    def get_test_object(self):
        return object()

    def test_dot_name(self):
        setdash = self.get_test_object()
        setdash.foo = 1
        self.assertTrue(hasattr(underlying_object(setdash), 'foo'))
        self.assertEqual(underlying_object(setdash).foo, 1)

    def test_setattr_function(self):
        setdash = self.get_test_object()
        setattr(setdash, 'foo', 1)
        self.assertTrue(hasattr(underlying_object(setdash), 'foo'))
        self.assertEqual(underlying_object(setdash).foo, 1)

    def test_direct(self):
        setdash = self.get_test_object()
        setdash.__setattr__('foo', 1)
        self.assertTrue(hasattr(underlying_object(setdash), 'foo'))
        self.assertEqual(underlying_object(setdash).foo, 1)


@implements(ISettable)
class GeneratedSetDash:

    def __getattr__(self, name):
        if name == '__setattr__':
            def f(obj, name, value):
                object.__setattr__(obj, name + '_', value)
            return f
        raise AttributeError(name)

    foo = 5


class GeneratedInstanceTests(GeneratedTestMixin, unittest.TestCase):

    def get_test_object(self):
        return GeneratedSetDash()


class GeneratedInterfaceTests(GeneratedTestMixin, unittest.TestCase):

    def get_test_object(self):
        return ISettable(GeneratedSetDash())
