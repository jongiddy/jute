import unittest

from jute import Interface, Dynamic


class Callable(Interface):

    def __call__(self):
        """Interface for a callable."""


class CallTestMixin:

    def get_test_object(self):
        return object()

    def test_call(self):
        callable = self.get_test_object()
        self.assertEqual(callable(), 0)

    def test_getattr(self):
        callable = self.get_test_object()
        self.assertEqual(getattr(callable, '__call__')(), 0)

    def test_attribute(self):
        callable = self.get_test_object()
        self.assertEqual(callable.__call__(), 0)


class BasicCallable(Callable.Provider):

    def __call__(self):
        return 0


class CallableInstanceTests(CallTestMixin, unittest.TestCase):

    def get_test_object(self):
        return BasicCallable()


class CallableInterfaceTests(CallTestMixin, unittest.TestCase):

    def get_test_object(self):
        return Callable(BasicCallable())


class CallableProxy(Dynamic.Provider):

    def __init__(self, wrapped_callable):
        self.wrapped = wrapped_callable

    def provides_interface(self, interface):
        return interface.implemented_by(Callable)

    def __call__(self):
        return self.wrapped()


class CallableDynamicInstanceTests(CallTestMixin, unittest.TestCase):

    def get_test_object(self):
        return CallableProxy(BasicCallable())


class CallableDynamicInterfaceTests(CallTestMixin, unittest.TestCase):

    def get_test_object(self):
        return Callable(CallableProxy(BasicCallable()))


class GeneratedCallable(Callable.Provider):

    """A class that generates the __call__ method dynamically."""

    def __getattr__(self, name):
        if name == '__call__':
            def f():
                return 0
            return f
        raise AttributeError(name)


class GeneratedCallTestMixin(CallTestMixin):

    """Test __call__ for a provider that generates __call__."""

    def test_call(self):
        callable = self.get_test_object()
        with self.assertRaises(TypeError):
            callable()


class GeneratedCallInstanceTests(GeneratedCallTestMixin, unittest.TestCase):

    def get_test_object(self):
        return GeneratedCallable()


class GeneratedCallInterfaceTests(GeneratedCallTestMixin, unittest.TestCase):

    def get_test_object(self):
        return Callable(GeneratedCallable())
