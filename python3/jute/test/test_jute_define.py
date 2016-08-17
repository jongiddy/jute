import unittest
from jute import Attribute, Opaque, implements, InterfaceConformanceError
from jute._jute import _validate_function


class TypeA(str):

    """A subclass of str."""


class TypeB:

    """A different class."""


class IAttributeString(Opaque):

    x = Attribute(type=str)


class IAttributeTypeA(IAttributeString):

    x = Attribute(type=TypeA)


class IAttributeTypeB(Opaque):

    x = Attribute(type=TypeB)


class WhenInterfaceHasAttribute(unittest.TestCase):

    def test_implementer_must_define_attribute(self):
        """
        If an Attribute is defined in an interface, then an implementation
        must provide the attribute.
        """
        @implements(IAttributeString)
        class Implementation:
            pass
        impl = Implementation()
        with self.assertRaises(InterfaceConformanceError):
            IAttributeString(impl)

    def test_attribute_cannot_be_deleted_through_interface(self):
        """
        It is not possible to delete an attribute through an interface
        (because the interface object would then not provide the interface).
        """
        @implements(IAttributeString)
        class Implementation:
            x = "kan"
        impl = Implementation()
        face = IAttributeString(impl)
        with self.assertRaises(InterfaceConformanceError):
            del face.x

    def test_attribute_can_be_set_to_type(self):
        """
        An attribute can be set to any value of the Attribute type.
        """
        @implements(IAttributeString)
        class Implementation:
            x = "kan"
        impl = Implementation()
        face = IAttributeString(impl)
        face.x = "ga"

    def test_attribute_can_be_set_to_subtype(self):
        """
        An attribute can be set to a subclass of the Attribute type.
        """
        @implements(IAttributeString)
        class Implementation:
            x = "kan"
        impl = Implementation()
        face = IAttributeString(impl)
        face.x = TypeA("ga")

    def test_attribute_cannot_be_set_to_different_type(self):
        """
        An attribute cannot be set to another type.
        """
        @implements(IAttributeString)
        class Implementation:
            x = "kan"
        impl = Implementation()
        face = IAttributeString(impl)
        with self.assertRaises(TypeError):
            face.x = 3


class WhenSubinterfaceOverridesAttribute(unittest.TestCase):

    def test_new_attribute_can_be_subclass(self):
        """
        A sub-interface can override the type of an attribute, but only
        to a sub-class of the initial type.
        """
        @implements(IAttributeTypeA)
        class Implementation:
            x = TypeA("kan")
        impl = Implementation()
        IAttributeTypeA(impl)

    def test_new_attribute_cannot_be_a_different_type(self):
        """
        A sub-interface can override the type of an attribute, but only
        to a sub-class of the initial type.
        """
        with self.assertRaises(InterfaceConformanceError):
            class IAttributeWrongType(IAttributeString):
                x = Attribute(type=int)

    def test_subinterface_does_not_accept_original_type(self):
        @implements(IAttributeTypeA)
        class Implementation:
            x = "kan"
        impl = Implementation()
        with self.assertRaises(TypeError):
            IAttributeTypeA(impl)


# field must contain subclass of both supertypes
# - test good + each bad
# if subinterface overrides attribute, it must subtype both supertypes
# - test good + each bad
class WhenSubinterfaceHasCommonSuperattributes(unittest.TestCase):

    """
    When an implementation implements two interfaces that define the
    same attribute, the attribute must meet satisfy both definitions.
    """

    def test_implementation_must_support_both_interfaces(self):
        class AString(TypeA, TypeB):
            pass

        class SubInterface(IAttributeTypeA, IAttributeTypeB):
            pass

        @implements(IAttributeTypeA, IAttributeTypeB)
        class Implementation:
            x = AString("kan")

        impl = Implementation()
        # An implementation can be cast to the interfaces
        IAttributeTypeA(impl)
        IAttributeTypeB(impl)
        # but not to a sub-interface it doesn't implement
        with self.assertRaises(TypeError):
            SubInterface(Implementation())

    def test_implementation_must_support_subinterface(self):
        class AString(TypeA, TypeB):
            pass

        class SubInterface(IAttributeTypeA, IAttributeTypeB):
            pass

        @implements(SubInterface)
        class Implementation:
            x = AString("kan")

        impl = Implementation()
        # An implementation can be cast to the interfaces
        IAttributeTypeA(impl)
        IAttributeTypeB(impl)
        SubInterface(Implementation())

    def test_subinterface_must_support_both(self):
        class AString:
            pass

        with self.assertRaises(InterfaceConformanceError):
            class SubInterface(IAttributeTypeA, IAttributeTypeB):
                x = Attribute(type=AString)  # fails - not subclass of both

    def test_subinterface_fails_for_one(self):
        class AString:
            pass

        with self.assertRaises(InterfaceConformanceError):
            class SubInterface(IAttributeTypeA, IAttributeTypeB):
                x = Attribute(type=TypeA)  # not subclass of TypeB

    def test_subinterface_fails_for_another(self):
        class AString:
            pass

        with self.assertRaises(InterfaceConformanceError):
            class SubInterface(IAttributeTypeA, IAttributeTypeB):
                x = Attribute(type=TypeB)  # not subclass of TypeA

    def test_implementation_fails_for_one(self):
        class AString(TypeA, TypeB):
            pass

        # We don't care what value the field has here, or even if it is
        # defined.  We only care when it is cast to the interface.
        @implements(IAttributeTypeA, IAttributeTypeB)
        class Implementation:
            x = TypeA("kan")

        with self.assertRaises(TypeError):
            IAttributeTypeB(Implementation())

    def test_implementation_fails_for_another(self):
        class AString(TypeA, TypeB):
            pass

        # We don't care what value the field has here, or even if it is
        # defined.  We only care when it is cast to the interface.
        @implements(IAttributeTypeA, IAttributeTypeB)
        class Implementation:
            x = TypeB()

        with self.assertRaises(TypeError):
            IAttributeTypeA(Implementation())


class IMethod(Opaque):

    def kan(self, ga):
        """A method"""


class WhenInterfaceHasMethod(unittest.TestCase):

    def test_implementer_must_define_method(self):
        @implements(IMethod)
        class Implementation:
            pass
        impl = Implementation()
        with self.assertRaises(InterfaceConformanceError):
            IMethod(impl)

    def test_method_cannot_be_deleted_through_interface(self):
        @implements(IMethod)
        class Implementation:

            def kan(self, ga):
                return ga
        impl = Implementation()
        face = IMethod(impl)
        with self.assertRaises(InterfaceConformanceError):
            del face.kan

    @unittest.skip("Need to add code to enforce this")
    def test_method_must_match_signature(self):
        @implements(IMethod)
        class Implementation:

            def kan(self, ga, roo):
                return ga
        impl = Implementation()
        with self.assertRaises(TypeError):
            IMethod(impl)

    @unittest.skip("Need to add code to enforce this")
    def test_method_cannot_be_set_to_different_type(self):
        @implements(IMethod)
        class Implementation:

            def kan(self, ga, roo):
                return ga, roo
        impl = Implementation()
        face = IMethod(impl)
        with self.assertRaises(TypeError):
            face.x = 3

    def test_method_can_be_inexact_matching_signature(self):
        @implements(IMethod)
        class Implementation:

            def kan(self, ga, roo=1):
                return ga, roo
        impl = Implementation()
        IMethod(impl)


class ValidateFunctionTests(unittest.TestCase):

    def test_empty_validator(self):
        def func(foo):
            return foo

        def validate(kan):
            """Nothing here"""
        self.assertEqual(_validate_function([validate], func, (3,), {}), 3)

    def test_non_acting_validator(self):
        def func(foo):
            return foo

        def validate(kan):
            yield
        self.assertEqual(_validate_function([validate], func, (3,), {}), 3)

    def test_too_many_iterations(self):
        def func(foo):
            return foo

        def validate(kan):
            yield
            yield
        with self.assertRaises(RuntimeError):
            _validate_function([validate], func, (3,), {})

    def test_failing_args_validator(self):
        def func(foo):
            return foo

        def validate(kan):
            assert isinstance(kan, str)

        with self.assertRaises(AssertionError):
            _validate_function([validate], func, (3,), {})

    def test_failing_result_validator(self):
        def func(foo):
            return foo

        def validate(kan):
            result = yield
            assert isinstance(result, str)

        with self.assertRaises(AssertionError):
            _validate_function([validate], func, (3,), {})
