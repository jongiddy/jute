import unittest

from jute import Interface, Dynamic, implements, InterfaceConformanceError


# Simple interface hierarchy for testing

class IFoo(Interface):
    foo = 99


class IFooBar(IFoo):

    def bar(self):
        """The bar method."""


class IFooBaz(IFoo):

    def baz(self):
        """The baz method."""


class IncompleteProviderTestsMixin:

    # Change this to the class to be tested
    HasBarOnly = object

    def test_incomplete_provider_validate_none(self):
        """Incomplete implementations are caught (during debugging).

        If an object claims to provide an interface, but doesn't,
        conversion to the interface will raise an
        InterfaceConformanceError in non-optimised code.

        In optimised code, the relatively expensive verification is
        removed and claims to implement an interface are always
        accepted. Accessing a non-interface attribute will still lead to
        an AttributeError, but this may occur later, when it is more
        difficult to diagnose where the invalid object came from.
        """
        obj = self.HasBarOnly()
        if __debug__:
            with self.assertRaises(InterfaceConformanceError):
                IFooBar(obj)
        else:
            foobar = IFooBar(obj)
            with self.assertRaises(AttributeError):
                foobar.foo

    def test_incomplete_provider_validate_true(self):
        """validate is True -> always raise InterfaceConformanceError."""
        obj = self.HasBarOnly()
        with self.assertRaises(InterfaceConformanceError):
            IFooBar(obj, validate=True)

    def test_incomplete_provider_validate_false(self):
        """validate is False -> always raise late AttributeError."""
        obj = self.HasBarOnly()
        foobar = IFooBar(obj, validate=False)
        with self.assertRaises(AttributeError):
            foobar.foo


class CompleteProviderTestsMixin:

    # Change this to the class to be tested
    HasFooBarBaz = object

    def test_provide(self):
        """An interface only has attributes defined in the interface (or
        in super-interfaces)."""
        obj = self.HasFooBarBaz()
        foobar = IFooBar(obj)
        self.assertEqual(foobar.foo, 1)
        foobar.bar()
        self.assertEqual(obj.foo, 2)
        with self.assertRaises(AttributeError):
            foobar.baz()
        self.assertEqual(obj.foo, 2)

    def test_inherit(self):
        """An interface can be mapped to a super-interface."""
        obj = self.HasFooBarBaz()
        foobar = IFooBar(obj)
        foo = IFoo(foobar)
        self.assertEqual(foo.foo, 1)
        with self.assertRaises(AttributeError):
            foo.bar()
        self.assertEqual(obj.foo, 1)

    def test_upcast_fails(self):
        """An interface cannot be mapped to a sub-interface, even if the
        wrapped instance could be."""
        obj = self.HasFooBarBaz()
        foo = IFoo(obj)
        with self.assertRaises(TypeError):
            IFooBar(foo)

    def test_duck_fails(self):
        """Duck-typed object does not match unclaimed interface.

        Although object matches the interface by duck-typing, it does
        not claim to provide the interface, so it fails with a
        TypeError."""
        obj = self.HasFooBarBaz()
        with self.assertRaises(TypeError):
            IFooBaz(obj)

    def test_wrapped_duck_fails(self):
        """Duck-typed wrapped object does not match unclaimed interface.

        Although object matches the interface by duck-typing, it does
        not claim to provide the interface, so it fails with a
        TypeError."""
        obj = self.HasFooBarBaz()
        foobar = IFooBar(obj)
        with self.assertRaises(TypeError):
            IFooBaz(foobar)

    def test_subclass_provider_provides_interface(self):
        """Subclassing an implementation and a provider works."""
        class IFooBarSubclass(self.HasFooBarBaz, IFooBaz.Provider):
            pass
        obj = IFooBarSubclass()
        foobar = IFooBar(obj)
        foobaz = IFooBaz(obj)
        self.assertEqual(foobar.foo, 1)
        foobar.bar()
        self.assertEqual(obj.foo, 2)
        foobaz.baz()
        self.assertEqual(obj.foo, 3)

    def test_provider_subclass_provides_interface(self):
        """Subclassing a provider and an implementation works."""
        class IFooBarSubclass(IFooBaz.Provider, self.HasFooBarBaz):
            pass
        obj = IFooBarSubclass()
        foobar = IFooBar(obj)
        foobaz = IFooBaz(obj)
        self.assertEqual(foobar.foo, 1)
        foobar.bar()
        self.assertEqual(obj.foo, 2)
        foobaz.baz()
        self.assertEqual(obj.foo, 3)


class FooBarSubclassProviderBaz(IFooBar.Provider):

    """IFooBar provider class.

    A class which implements IFooBar, and looks like IFooBaz, but does
    not implement IFooBaz.
    """

    foo = 1

    def bar(self):
        self.foo = 2

    def baz(self):
        self.foo = 3


class FooBarSubclassProviderNoFoo(IFooBar.Provider):
    # doesn't implement foo

    def bar():
        pass


class InterfaceProviderTests(
        CompleteProviderTestsMixin, IncompleteProviderTestsMixin,
        unittest.TestCase):

    HasFooBarBaz = FooBarSubclassProviderBaz
    HasBarOnly = FooBarSubclassProviderNoFoo


class FooBarDynamicProviderBaz(Dynamic.Provider):

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


class FooBarDynamicProviderNoFoo(Dynamic.Provider):
    # doesn't implement foo

    def provides_interface(self, interface):
        return interface.implemented_by(IFooBar)

    def bar():
        pass


class DynamicProviderTests(
        CompleteProviderTestsMixin, IncompleteProviderTestsMixin,
        unittest.TestCase):

    HasFooBarBaz = FooBarDynamicProviderBaz
    HasBarOnly = FooBarDynamicProviderNoFoo

    def test_subclass_provides_interface(self):
        class IFooBarSubclass(self.HasFooBarBaz):

            def provides_interface(self, interface):
                return (
                    interface.implemented_by(IFooBar) or
                    interface.implemented_by(IFooBaz)
                )

        obj = IFooBarSubclass()
        foobar = IFooBar(obj)
        foobaz = IFooBaz(obj)
        self.assertEqual(foobar.foo, 1)
        foobar.bar()
        self.assertEqual(obj.foo, 2)
        foobaz.baz()
        self.assertEqual(obj.foo, 3)


class FooBarRegisteredProviderBaz:

    """IFooBar provider class.

    A class which implements IFooBar, and looks like IFooBaz, but does
    not implement IFooBaz.
    """

    foo = 1

    def bar(self):
        self.foo = 2

    def baz(self):
        self.foo = 3

IFooBar.register_provider(FooBarRegisteredProviderBaz)


class FooBarRegisteredProviderNoFoo:
    # doesn't implement foo

    def bar():
        pass

IFooBar.register_provider(FooBarRegisteredProviderNoFoo)


class Capitalizable(Interface):

    """An interface provided by string type."""

    def capitalize(self):
        """Return first character capitalized and rest lowercased."""


class RegisteredProviderTests(
        CompleteProviderTestsMixin, unittest.TestCase):

    HasFooBarBaz = FooBarRegisteredProviderBaz

    def test_builtin_type(self):
        """Built in types can be registered."""
        Capitalizable.register_provider(str)
        c = Capitalizable('a stRing')
        self.assertEqual(c.capitalize(), 'A string')

    def test_incomplete_implementation_cannot_be_registered(self):
        with self.assertRaises(InterfaceConformanceError):
            IFooBar.register_implementation(FooBarSubclassProviderNoFoo)

    def test_incomplete_provider_validate_none(self):
        """Incomplete providers are caught (during debugging)."""
        obj = FooBarRegisteredProviderNoFoo()
        if __debug__:
            with self.assertRaises(InterfaceConformanceError):
                foobar = IFooBar(obj)
        else:
            foobar = IFooBar(obj)
            with self.assertRaises(AttributeError):
                foobar.foo

    def test_incomplete_provider_validate_true(self):
        """validate is True -> always raise InterfaceConformanceError."""
        obj = FooBarRegisteredProviderNoFoo()
        with self.assertRaises(InterfaceConformanceError):
            IFooBar(obj, validate=True)

    def test_incomplete_provider_validate_false(self):
        """validate is False -> always raise late AttributeError."""
        obj = FooBarRegisteredProviderNoFoo()
        foobar = IFooBar(obj, validate=False)
        with self.assertRaises(AttributeError):
            foobar.foo

    def test_non_class_fails(self):
        """A non-class interface provider cannot be registered.

        This is required to ensure that registered implementations can
        be tested quickly using `issubclass`"""
        with self.assertRaises(TypeError):
            Capitalizable.register_provider('')


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

    foo = 1

    def bar():
        pass

# Needs to be complete for registration, but then remove part of class.
# Document non-deletion of interface attributes as a requirement for
# registration.
IFooBar.register_implementation(FooBarRegisteredImplementationNoFoo)
del FooBarRegisteredImplementationNoFoo.foo


class RegisteredImplementationTests(
        CompleteProviderTestsMixin, unittest.TestCase):

    HasFooBarBaz = FooBarRegisteredImplementationBaz

    def test_builtin_type(self):
        """Built in types can be registered."""
        Capitalizable.register_implementation(str)
        c = Capitalizable('a stRing')
        self.assertEqual(c.capitalize(), 'A string')

    def test_incomplete_implementation_cannot_be_registered(self):
        with self.assertRaises(InterfaceConformanceError):
            IFooBar.register_implementation(FooBarSubclassProviderNoFoo)

    def test_incomplete_provider_validate_none(self):
        """Incomplete implementations are caught (during debugging).

        If a class successfully registers an interface, but doesn't
        provide the interface (e.g. deletes an attribute), the problem
        is not detected during creation.  A normal attribute error will
        be raised when the attributes is accessed.

        Note, this is the same as `validate=False` for non-registered
        providers, indicating that classes verified before instantiation
        are not verified when being instantiated.
        """
        obj = FooBarRegisteredImplementationNoFoo()
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


@implements(IFooBar)
class FooBarDecoratedImplementationBaz:

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


class DecoratedImplementationTests(
        CompleteProviderTestsMixin, unittest.TestCase):

    HasFooBarBaz = FooBarRegisteredImplementationBaz


class IFooBarSubclass(IFooBar):
    pass


class DoubleInheritedInterfaceTests(unittest.TestCase):

    """Check that all base classes are treated as provided by an interface.

    If we mistakenly just use the first level of base classes, these tests
    should fail.
    """

    def test_provider(self):
        class FooBar(IFooBarSubclass.Provider):
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
        """An interface is implemented by itself."""
        self.assertTrue(IFoo.implemented_by(IFoo))

    def test_implemented_by_subinterface(self):
        """An interface is implemented by a sub-interface."""
        self.assertTrue(IFoo.implemented_by(IFooBar))

    def test_implemented_by_registered_class(self):
        """An interface is implemented by a registered class."""
        self.assertTrue(IFoo.implemented_by(FooBarRegisteredImplementationBaz))

    def test_implemented_by_verifiable_provider_class(self):
        """An interface is implemented by a provider class if verified."""
        class Foo(IFoo.Provider):
            foo = 1
        self.assertTrue(IFoo.implemented_by(Foo))

    def test_implemented_by_non_verifiable_provider_class(self):
        """An interface is implemented by non-verified provider class."""
        class Foo(IFoo.Provider):
            # Instance is a valid provider, but the class itself is not.

            def __init__(self):
                self.foo = 1
        self.assertTrue(IFoo.implemented_by(Foo))

    def test_not_implemented_by_provider_instance(self):
        """An interface is not implemented by a provider instance."""
        self.assertFalse(IFoo.implemented_by(FooBarSubclassProviderBaz()))

    def test_not_implemented_by_registered_instance(self):
        """An interface is not implemented by a registered class instance."""
        self.assertFalse(
            IFoo.implemented_by(FooBarRegisteredImplementationBaz()))

    def test_not_implemented_by_non_provider(self):
        """An interface is not implemented by a non-providing class."""
        class C:
            foo = 1
        self.assertFalse(IFoo.implemented_by(C))


class CastTest(unittest.TestCase):

    def test_provider_cast(self):
        class FooBarBaz(FooBarSubclassProviderBaz, IFooBaz.Provider):

            """Class that implements IFooBar and IFooBaz."""

        foobarbaz = FooBarBaz()
        foobar = IFooBar(foobarbaz)
        with self.assertRaises(AttributeError):
            foobar.baz()
        foobaz = IFooBaz.cast(foobar)
        foobaz.baz()


class SupportedByTest(unittest.TestCase):

    def test_supported_by(self):
        foobar = FooBarSubclassProviderBaz()
        foo = IFoo(foobar)
        self.assertFalse(IFooBar.provided_by(foo))
        self.assertTrue(IFooBar.supported_by(foo))
        # interface not supported if duck-typed, but not claimed
        self.assertFalse(IFooBaz.supported_by(foo))

