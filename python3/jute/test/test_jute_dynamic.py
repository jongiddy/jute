import unittest

from jute import DynamicInterface, Interface, implements


class ProvidedByTests(unittest.TestCase):

    """
    Since DynamicInterface is used in the implementation of `provided_by`,
    it may cause problems when DynamicInterface is passed as the
    implementation to check (e.g. infinite loops).  Verify each of the
    ways to make something dynamic.
    """

    def test_implemented_provided_by(self):
        @implements(DynamicInterface)
        class DynamicImplemented:

            def provides_interface(self, interface):
                return False

        self.assertTrue(DynamicInterface.provided_by(DynamicImplemented()))

    def test_registered_implementation_provided_by(self):
        class DynamicRegisteredImplementation:

            def provides_interface(self, interface):
                return False

        DynamicInterface.register_implementation(
            DynamicRegisteredImplementation
        )

        self.assertTrue(
            DynamicInterface.provided_by(DynamicRegisteredImplementation())
        )


class IFoo(Interface):

    def foo(self):
        """"""


class DynamicInterfaceProvidedByTests(unittest.TestCase):

    """
    Check the different ways of creating a DynamicInterface implementation
    """

    def test_implemented_provided_by(self):
        @implements(DynamicInterface)
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

        DynamicInterface.register_implementation(FooDynamic)

        instance = FooDynamic()
        self.assertTrue(IFoo.provided_by(instance))
        IFoo(instance)
