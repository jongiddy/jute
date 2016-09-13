import unittest
from jute import Opaque, implements, InterfaceConformanceError
from jute._jute import _validate_function


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
            face.kan = 3

    @unittest.skip("Need to add code to enforce this")
    def test_method_cannot_be_set_to_different_signature(self):
        @implements(IMethod)
        class Implementation:

            def kan(self, ga, roo):
                return ga, roo
        impl = Implementation()
        face = IMethod(impl)
        from types import MethodType
        def new(self, ga):
            pass
        with self.assertRaises(TypeError):
            face.kan = MethodType(new, face, IMethod)

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
