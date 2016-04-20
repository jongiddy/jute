import unittest
from jute import Attribute, Opaque, implements, InterfaceConformanceError


class MyString(str):

    """A subclass of str."""


class AnotherClass:

    """A different class."""


class IAttribute(Opaque):

    x = Attribute(type=str)


class IAttributeSubclass(IAttribute):

    x = Attribute(type=MyString)


class IAttributeSimilar(Opaque):

    x = Attribute(type=AnotherClass)


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

    def test_new_attribute_can_be_subclass(self):
        """
        A sub-interface can override the type of an attribute, but only
        to a sub-class of the initial type.
        """
        @implements(IAttributeSubclass)
        class Implementation:
            x = MyString("kan")
        impl = Implementation()
        IAttributeSubclass(impl)

    def test_new_attribute_cannot_be_a_different_type(self):
        """
        A sub-interface can override the type of an attribute, but only
        to a sub-class of the initial type.
        """
        with self.assertRaises(InterfaceConformanceError):
            class IAttributeTypeA2(IAttribute):
                x = Attribute(type=int)

    def test_subinterface_does_not_accept_original_type(self):
        @implements(IAttributeSubclass)
        class Implementation:
            x = "kan"
        impl = Implementation()
        with self.assertRaises(TypeError):
            IAttributeSubclass(impl)


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
        class AString(MyString, AnotherClass):
            pass

        class SubInterface(IAttributeSubclass, IAttributeSimilar):
            pass

        @implements(IAttributeSubclass, IAttributeSimilar)
        class Implementation:
            x = AString("kan")

        impl = Implementation()
        # An implementation can be cast to the interfaces
        IAttributeSubclass(impl)
        IAttributeSimilar(impl)
        # but not to a sub-interface it doesn't implement
        with self.assertRaises(TypeError):
            SubInterface(Implementation())

    def test_implementation_must_support_subinterface(self):
        class AString(MyString, AnotherClass):
            pass

        class SubInterface(IAttributeSubclass, IAttributeSimilar):
            pass

        @implements(SubInterface)
        class Implementation:
            x = AString("kan")

        impl = Implementation()
        # An implementation can be cast to the interfaces
        IAttributeSubclass(impl)
        IAttributeSimilar(impl)
        SubInterface(Implementation())

    def test_subinterface_must_support_both(self):
        class AString:
            pass

        with self.assertRaises(InterfaceConformanceError):
            class SubInterface(IAttributeSubclass, IAttributeSimilar):
                x = Attribute(type=AString)  # fails - not subclass of both

    def test_subinterface_fails_for_one(self):
        class AString:
            pass

        with self.assertRaises(InterfaceConformanceError):
            class SubInterface(IAttributeSubclass, IAttributeSimilar):
                x = Attribute(type=MyString)  # not subclass of AnotherClass

    def test_subinterface_fails_for_another(self):
        class AString:
            pass

        with self.assertRaises(InterfaceConformanceError):
            class SubInterface(IAttributeSubclass, IAttributeSimilar):
                x = Attribute(type=AnotherClass)  # not subclass of MyString

    def test_implementation_fails_for_one(self):
        class AString(MyString, AnotherClass):
            pass

        # TODO - this should fail during this class definition
        @implements(IAttributeSubclass, IAttributeSimilar)
        class Implementation:
            x = MyString("kan")

        with self.assertRaises(TypeError):
            IAttributeSimilar(Implementation())

    def test_implementation_fails_for_another(self):
        class AString(MyString, AnotherClass):
            pass

        # TODO - this should fail during this class definition
        @implements(IAttributeSubclass, IAttributeSimilar)
        class Implementation:
            x = AnotherClass()

        with self.assertRaises(TypeError):
            IAttributeSubclass(Implementation())


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
