import unittest
from jute import Attribute, Opaque, implements, InterfaceConformanceError


class MyString(str):

    """A subclass of str."""


class IAttribute(Opaque):

    x = Attribute(type=str)


class IAttributeSubclass(IAttribute):
    x = Attribute(type=MyString)


class WhenInterfaceHasAttribute(unittest.TestCase):

    def test_implementer_must_define_attribute(self):
        """
        If an Attribute is defined in an interface, then an implementation
        must provide the attribute.
        """
        @implements(IAttribute)
        class Implementation:
            pass
        impl = Implementation()
        with self.assertRaises(InterfaceConformanceError):
            IAttribute(impl)

    def test_attribute_cannot_be_deleted_through_interface(self):
        """
        It is not possible to delete an attribute through an interface
        (because the interface object would then not provide the interface).
        """
        @implements(IAttribute)
        class Implementation:
            x = "kan"
        impl = Implementation()
        face = IAttribute(impl)
        with self.assertRaises(InterfaceConformanceError):
            del face.x

    def test_attribute_can_be_set_to_type(self):
        """
        An attribute can be set to any value of the Attribute type.
        """
        @implements(IAttribute)
        class Implementation:
            x = "kan"
        impl = Implementation()
        face = IAttribute(impl)
        face.x = "ga"

    def test_attribute_can_be_set_to_subtype(self):
        """
        An attribute can be set to a subclass of the Attribute type.
        """
        @implements(IAttribute)
        class Implementation:
            x = "kan"
        impl = Implementation()
        face = IAttribute(impl)
        face.x = MyString("ga")

    def test_attribute_cannot_be_set_to_different_type(self):
        """
        An attribute cannot be set to another type.
        """
        @implements(IAttribute)
        class Implementation:
            x = "kan"
        impl = Implementation()
        face = IAttribute(impl)
        with self.assertRaises(TypeError):
            face.x = 3


class WhenSubinterfaceOverridesAttribute(unittest.TestCase):

    def test_subclass_can_override_attribute_with_subclass(self):
        """
        A sub-interface can override the type of an attribute, but only
        to a sub-class of the initial type.
        """
        @implements(IAttributeSubclass)
        class Implementation:
            x = MyString("kan")
        impl = Implementation()
        IAttributeSubclass(impl)

    @unittest.skip("Need to check types")
    def test_subclass_cannot_override_attribute_with_another_type(self):
        """
        A sub-interface can override the type of an attribute, but only
        to a sub-class of the initial type.
        """
        with self.assertRaises(Exception):
            class IAttributeSubclass2(IAttribute):
                x = Attribute(type=int)

    def test_overridden_attribute_does_not_accept_original_type(self):
        @implements(IAttributeSubclass)
        class Implementation:
            x = "kan"
        impl = Implementation()
        with self.assertRaises(TypeError):
            IAttributeSubclass(impl)


class IMethod(Opaque):

    def kan(self, ga):
        """A method"""


@unittest.skip("Need to add code to enforce this")
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
            del face.x

    def test_method_must_match_signature(self):
        @implements(IMethod)
        class Implementation:

            def kan(self, ga, roo):
                return ga
        impl = Implementation()
        with self.assertRaises(TypeError):
            IMethod(impl)

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
