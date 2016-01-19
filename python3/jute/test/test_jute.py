import unittest

from jute import (
    Interface, Dynamic, implements, InterfaceConformanceError
)


# Simple interface hierarchy for testing

class IFoo(Interface):
    foo = 99  # Initially set to 1 in implementations


class IFooBar(IFoo):

    def bar(self):
        """The bar method. Sets foo to 2."""


class IFooBaz(IFoo):

    def baz(self):
        """The baz method. Sets foo to 3."""


class IncompleteProviderTestsMixin:

    # Change this to the class to be tested - a class that claims to
    # implement the interface `IFooBar`, but only provides `bar`.
    FooBarHasBarOnly = object

    def test_incomplete_provider_validate_none(self):
        """
        Incomplete implementations are caught (during debugging).

        If an object claims to provide an interface, but doesn't,
        conversion to the interface will raise an
        InterfaceConformanceError in non-optimised code.

        In optimised code, the relatively expensive verification is
        removed and claims to implement an interface are always
        accepted. Accessing a non-interface attribute will still lead to
        an AttributeError, but this may occur later, when it is more
        difficult to diagnose where the invalid object came from.
        """
        obj = self.FooBarHasBarOnly()
        if __debug__:
            with self.assertRaises(InterfaceConformanceError):
                IFooBar(obj)
        else:
            foobar = IFooBar(obj)
            with self.assertRaises(AttributeError):
                foobar.foo

    def test_incomplete_provider_validate_true(self):
        """validate is True -> always raise InterfaceConformanceError."""
        obj = self.FooBarHasBarOnly()
        with self.assertRaises(InterfaceConformanceError):
            IFooBar(obj, validate=True)

    def test_incomplete_provider_validate_false(self):
        """validate is False -> always raise late AttributeError."""
        obj = self.FooBarHasBarOnly()
        foobar = IFooBar(obj, validate=False)
        with self.assertRaises(AttributeError):
            foobar.foo


class CompleteProviderTestsMixin:

    # Change this to the class to be tested - a class that has
    # attributes `foo`, `bar`, `baz`, but which only claims to
    # implement `IFooBar`.
    FooBarHasFooBarBaz = object

    def test_provide(self):
        """
        An interface only has attributes defined in the interface (or
        in super-interfaces).
        """
        obj = self.FooBarHasFooBarBaz()
        foobar = IFooBar(obj)
        self.assertEqual(foobar.foo, 1)
        foobar.bar()
        self.assertEqual(obj.foo, 2)
        with self.assertRaises(AttributeError):
            foobar.baz()
        self.assertEqual(obj.foo, 2)

    def test_inherit(self):
        """An interface can be mapped to a super-interface."""
        obj = self.FooBarHasFooBarBaz()
        foobar = IFooBar(obj)
        foo = IFoo(foobar)
        self.assertEqual(foo.foo, 1)
        with self.assertRaises(AttributeError):
            foo.bar()
        self.assertEqual(obj.foo, 1)

    def test_upcast_fails(self):
        """
        An interface cannot be mapped to a sub-interface, even if the
        wrapped instance could be.
        """
        obj = self.FooBarHasFooBarBaz()
        foo = IFoo(obj)
        with self.assertRaises(TypeError):
            IFooBar(foo)

    def test_duck_fails(self):
        """
        Duck-typed object does not match unclaimed interface.

        Although object matches the interface by duck-typing, it does
        not claim to provide the interface, so it fails with a
        TypeError.
        """
        obj = self.FooBarHasFooBarBaz()
        with self.assertRaises(TypeError):
            IFooBaz(obj)

    def test_wrapped_duck_fails(self):
        """
        Duck-typed wrapped object does not match unclaimed interface.

        Although object matches the interface by duck-typing, it does
        not claim to provide the interface, so it fails with a
        TypeError.
        """
        obj = self.FooBarHasFooBarBaz()
        foobar = IFooBar(obj)
        with self.assertRaises(TypeError):
            IFooBaz(foobar)

    def test_subclass_implements_provides_all_interfaces(self):
        """Implements and subclasses together work."""
        @implements(IFooBaz)
        class IFooBarSubclass(self.FooBarHasFooBarBaz):
            pass
        obj = IFooBarSubclass()
        foobar = IFooBar(obj)
        foobaz = IFooBaz(obj)
        self.assertEqual(foobar.foo, 1)
        foobar.bar()
        self.assertEqual(obj.foo, 2)
        foobaz.baz()
        self.assertEqual(obj.foo, 3)


@implements(IFooBar)
class FooBarImplementerHasBaz:

    """
    Complete IFooBar implementation.

    A class which implements IFooBar, and looks like IFooBaz, but does
    not implement IFooBaz.
    """

    foo = 1

    def bar(self):
        self.foo = 2

    def baz(self):
        self.foo = 3


@implements(IFooBar)
class FooBarImplementerNoFoo:

    """
    Incomplete IFooBar implementation.

    A class which claims to implement IFooBar, but doesn't.
    """

    def bar():
        pass


class InterfaceProviderTests(
        CompleteProviderTestsMixin, IncompleteProviderTestsMixin,
        unittest.TestCase):

    FooBarHasFooBarBaz = FooBarImplementerHasBaz
    FooBarHasBarOnly = FooBarImplementerNoFoo


@implements(Dynamic)
class FooBarDynamicHasBaz:

    def provides_interface(self, interface):
        return interface.implemented_by(IFooBar)

    _foo = 1

    def bar(self):
        self._foo = 2

    def baz(self):
        self._foo = 3

    def __getattr__(self, name):
        if name == 'foo':
            return self._foo
        return super().__getattr__(name)


@implements(Dynamic)
class FooBarDynamicNoFoo:
    # doesn't implement foo

    def provides_interface(self, interface):
        return interface.implemented_by(IFooBar)

    def bar():
        pass


class DynamicProviderTests(
        CompleteProviderTestsMixin, IncompleteProviderTestsMixin,
        unittest.TestCase):

    FooBarHasFooBarBaz = FooBarDynamicHasBaz
    FooBarHasBarOnly = FooBarDynamicNoFoo

    def test_subclass_provides_interface(self):
        """
        A subclass of Dynamic can override the provided interfaces, even if
        that means breaking the expected subclass relationship.
        """
        class IFooBarSubclass(self.FooBarHasFooBarBaz):

            def provides_interface(self, interface):
                return interface.implemented_by(IFooBaz)

        obj = IFooBarSubclass()
        with self.assertRaises(TypeError):
            IFooBar(obj)
        foobaz = IFooBaz(obj)
        foobaz.baz()
        self.assertEqual(obj.foo, 3)


class FooBarRegisteredImplementationBaz:

    """IFooBar provider class.

    A class which implements IFooBar, and looks like IFooBaz, but does
    not implement IFooBaz.
    """

    foo = 1

    def bar(self):
        self.foo = 2

    def baz(self):
        self.foo = 3

IFooBar.register_implementation(FooBarRegisteredImplementationBaz)


class FooBarRegisteredImplementationNoFoo:
    # doesn't implement foo

    def bar():
        pass

IFooBar.register_implementation(FooBarRegisteredImplementationNoFoo)


class Capitalizable(Interface):

    """An interface provided by string type."""

    def capitalize(self):
        """Return first character capitalized and rest lowercased."""


class RegisteredImplementationTests(
        CompleteProviderTestsMixin, unittest.TestCase):

    FooBarHasFooBarBaz = FooBarRegisteredImplementationBaz

    def test_builtin_type(self):
        """Built in types can be registered."""
        Capitalizable.register_implementation(str)
        c = Capitalizable('a stRing')
        self.assertEqual(c.capitalize(), 'A string')

    def test_incomplete_implementation_can_be_registered(self):
        IFooBar.register_implementation(FooBarImplementerNoFoo)

    def test_incomplete_provider_validate_none(self):
        """Incomplete providers are caught (during debugging)."""
        obj = FooBarRegisteredImplementationNoFoo()
        if __debug__:
            with self.assertRaises(InterfaceConformanceError):
                foobar = IFooBar(obj)
        else:
            foobar = IFooBar(obj)
            with self.assertRaises(AttributeError):
                foobar.foo

    def test_incomplete_provider_validate_true(self):
        """validate is True -> always raise InterfaceConformanceError."""
        obj = FooBarRegisteredImplementationNoFoo()
        with self.assertRaises(InterfaceConformanceError):
            IFooBar(obj, validate=True)

    def test_incomplete_provider_validate_false(self):
        """validate is False -> always raise late AttributeError."""
        obj = FooBarRegisteredImplementationNoFoo()
        foobar = IFooBar(obj, validate=False)
        with self.assertRaises(AttributeError):
            foobar.foo

    def test_non_class_fails(self):
        """A non-class interface provider cannot be registered.

        This is required to ensure that registered implementations can
        be tested quickly using `issubclass`"""
        with self.assertRaises(TypeError):
            Capitalizable.register_implementation('')


class IFooBarSubclass(IFooBar):
    pass


class DoubleInheritedInterfaceTests(unittest.TestCase):

    """Check that all base classes are treated as provided by an interface.

    If we mistakenly just use the first level of base classes, these tests
    should fail.
    """

    def test_implements(self):
        @implements(IFooBarSubclass)
        class FooBar:
            foo = 1
            bar = 2

        foobar = FooBar()
        self.assertTrue(IFoo.provided_by(foobar))

    def test_registered(self):
        class FooBar:
            foo = 1
            bar = 2

        IFooBarSubclass.register_implementation(FooBar)

        foobar = FooBar()
        self.assertTrue(IFoo.provided_by(foobar))


class ImplementedByTests(unittest.TestCase):

    def test_implemented_by_self(self):
        """
        An interface is implemented by itself.  (An instance of the class
        IFoo (which wraps an object) implements the interface.)
        """
        self.assertTrue(IFoo.implemented_by(IFoo))

    def test_implemented_by_subinterface(self):
        """An interface is implemented by a sub-interface."""
        self.assertTrue(IFoo.implemented_by(IFooBar))

    def test_implemented_by_registered_class(self):
        """An interface is implemented by a registered class."""
        self.assertTrue(IFoo.implemented_by(FooBarRegisteredImplementationBaz))

    def test_implemented_by_verifiable_provider_class(self):
        """An interface is implemented by a provider class."""
        self.assertTrue(IFoo.implemented_by(FooBarImplementerHasBaz))

    def test_not_implemented_by_provider_instance(self):
        """A provider instance is not valid with implemented_by."""
        with self.assertRaises(TypeError):
            IFoo.implemented_by(FooBarImplementerHasBaz())

    def test_not_implemented_by_registered_instance(self):
        """A registered instance is not valid with implemented_by."""
        with self.assertRaises(TypeError):
            IFoo.implemented_by(FooBarRegisteredImplementationBaz())

    def test_not_implemented_by_non_provider(self):
        """An interface is not implemented by a non-providing class."""
        class C:
            foo = 1
        self.assertFalse(IFoo.implemented_by(C))


class CastTest(unittest.TestCase):

    def test_provider_valid_cast(self):
        @implements(IFooBaz)
        class FooBarBaz(FooBarImplementerHasBaz):

            """Class that implements IFooBar and IFooBaz."""

        foobarbaz = FooBarBaz()
        foobar = IFooBar(foobarbaz)
        with self.assertRaises(AttributeError):
            foobar.baz()
        foobaz = IFooBaz.cast(foobar)
        foobaz.baz()

    def test_provider_invalid_cast(self):
        """Cannot cast to interface not supported by underlying object."""
        foobarbaz = FooBarImplementerHasBaz()
        foobar = IFooBar(foobarbaz)
        with self.assertRaises(TypeError):
            IFooBaz.cast(foobar)


class SupportedByTest(unittest.TestCase):

    def test_supported_by(self):
        foobar = FooBarImplementerHasBaz()
        foo = IFoo(foobar)
        self.assertFalse(IFooBar.provided_by(foo))
        self.assertTrue(IFooBar.supported_by(foo))
        # interface not supported if duck-typed, but not claimed
        self.assertFalse(IFooBaz.supported_by(foo))
