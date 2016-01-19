import unittest

from jute import Dynamic, Interface, implements


class ProvidedByTests(unittest.TestCase):

    """
    Since Dynamic is used in the implementation of `provided_by`, it may
    cause problems when Dynamic is passed as the implementation to check
    (e.g. infinite loops).  Verify each of the ways to make something
    dynamic.
    """

    def test_implemented_provided_by(self):
        @implements(Dynamic)
        class DynamicImplemented:

            def provides_interface(self, interface):
                return False

        self.assertTrue(Dynamic.provided_by(DynamicImplemented()))

    def test_registered_implementation_provided_by(self):
        class DynamicRegisteredImplementation:

            def provides_interface(self, interface):
                return False

        Dynamic.register_implementation(DynamicRegisteredImplementation)

        self.assertTrue(Dynamic.provided_by(DynamicRegisteredImplementation()))

    def test_provider_provided_by(self):
        class DynamicProvider(Dynamic.Provider):

            def provides_interface(self, interface):
                return False

        self.assertTrue(Dynamic.provided_by(DynamicProvider()))


class IFoo(Interface):

    def foo(self):
        """"""


class DynamicInterfaceProvidedByTests(unittest.TestCase):

    """
    Check the different ways of creating a Dynamic inplementation
    """

    def test_implemented_provided_by(self):
        @implements(Dynamic)
        class FooDynamic:

            def provides_interface(self, interface):
                return interface.implemented_by(IFoo)

            def foo(self):
                return 1

        instance = FooDynamic()
        self.assertTrue(IFoo.provided_by(instance))
        IFoo(instance)

    def test_registered_implementation_provided_by(self):
        class FooDynamic:

            def provides_interface(self, interface):
                return interface.implemented_by(IFoo)

            def foo(self):
                return 1

        Dynamic.register_implementation(FooDynamic)

        instance = FooDynamic()
        self.assertTrue(IFoo.provided_by(instance))
        IFoo(instance)

    def test_provider_provided_by(self):
        class FooDynamic(Dynamic.Provider):

            def provides_interface(self, interface):
                return interface.implemented_by(IFoo)

            def foo(self):
                return 1

        instance = FooDynamic()
        self.assertTrue(IFoo.provided_by(instance))
        IFoo(instance)
