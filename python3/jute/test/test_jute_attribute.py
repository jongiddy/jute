import unittest

from jute import Interface, Dynamic, implements, InterfaceConformanceError


class Result:

    OK = 'ok'
    ERROR = 'exc'

    def __init__(self, state=None, result=None):
        self.state = state
        self.result = result

    @classmethod
    def ok(cls, result):
        return cls(cls.OK, result)

    @classmethod
    def exception(cls, exc):
        exc = (exc.__class__, exc.args)
        return cls(cls.ERROR, exc)

    def __repr__(self):
        return '<Result {}: {!r}>'.format(self.state, self.result)

    def __eq__(self, other):
        return self.state == other.state and self.result == other.result


def result(f, *args, **kw):
    try:
        return Result.ok(f(*args, **kw))
    except Exception as e:
        return Result.exception(e)


class IFoo(Interface):

    foo = int


@implements(IFoo)
class FooImplements:

    foo = 5
    bar = 6


class FooImplementsRegistered:

    foo = 5
    bar = 6

IFoo.register_implementation(FooImplementsRegistered)


class FooProvider(IFoo.Provider):

    def __init__(self):
        self.foo = 5
        self.bar = 6


class FooProviderRegistered:

    def __init__(self):
        self.foo = 5
        self.bar = 6

IFoo.register_provider(FooProviderRegistered)


class FooDynamic(Dynamic.Provider):

    def __getattr__(self, name):
        if name == 'foo':
            return 5
        elif name == 'bar':
            return 6
        return super().__getattr__(name)

    def provides_interface(self, interface):
        return interface.implemented_by(IFoo)


class WhenInterfaceHasAttribute:

    def test_get_internal_attribute_fails(self):
        """Caller cannot see the interface's hidden attributes."""
        # Interface does have a provider attribute
        object.__getattribute__(self.inf, 'provider')
        # but it is hidden from normal attribute access
        with self.assertRaises(AttributeError):
            self.inf.provider

    def test_get_attribute_in_interface(self):
        self.assertEqual(
            result(lambda: self.obj.foo),
            result(lambda: self.inf.foo)
        )

    def test_set_attribute_in_interface(self):
        self.inf.foo = 9
        self.assertEqual(self.obj.foo, 9)

    def test_del_attribute_in_interface(self):
        with self.assertRaises(InterfaceConformanceError):
            del self.inf.foo


class WhenInterfaceDoesNotHaveAttribute:

    def test_get_attribute_not_in_interface(self):
        with self.assertRaises(AttributeError):
            self.inf.bar

    def test_set_attribute_not_in_interface(self):
        with self.assertRaises(AttributeError):
            self.inf.bar = 9

    def test_del_attribute_not_in_interface(self):
        with self.assertRaises(AttributeError):
            del self.inf.bar


def mktest(cls):
    class TestClass(
        unittest.TestCase, WhenInterfaceHasAttribute,
        WhenInterfaceDoesNotHaveAttribute
    ):

        def setUp(self):
            self.obj = cls()
            self.inf = IFoo(self.obj)

    return TestClass


class FooImplementsTests(mktest(FooImplements)):
    pass


class FooImplementsRegisteredTests(mktest(FooImplementsRegistered)):
    pass


class FooProviderTests(mktest(FooProvider)):
    pass


class FooProviderRegisteredTests(mktest(FooProviderRegistered)):
    pass


class FooDynamicTests(mktest(FooDynamic)):
    pass
