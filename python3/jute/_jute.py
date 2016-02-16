"""
Interfaces for Python.

Yet another interface module for Python.

Although duck typing is generally considered the Pythonic way of dealing
with object compatibility, it's major problem is that it relies on
syntactical compatibility to indicate semantic compatibility.
Interfaces provide a way to indicate semantic compatibility
directly.

Most existing interface modules for Python (e.g. ``abc``,
and ``zope.interface``) check that implementing classes provide all the
attributes specified in the interface.  But they ignore the other side
of the contract, failing to ensure that the receiver of the interface
only calls operations specified in the interface.  This module checks
both, ensuring that called code will work with any provider of the
interface, not just the one with which it was tested.

To prevent interface checks from affecting performance, we recommend
to code interface conversions inside ``if __debug__:`` clauses. This
can be used to allow interface checks during debugging, and production
code to use the original objects by running Python with the ``-O`` flag.
"""

import types


def mkmessage(obj, missing):
    if len(missing) == 1:
        attribute = 'attribute'
    else:
        attribute = 'attributes'
    return '{} does not provide {} {}'.format(
        obj, attribute, ', '.join(repr(m) for m in missing))


class InterfaceConformanceError(Exception):

    """Object does not conform to interface specification.

    Exception indicating that an object claims to provide an interface,
    but does not match the interface specification.

    This is almost a TypeError, but an object provides two parts to its
    interface implementation: a claim to provide the interface, and the
    attributes that match the interface specification.  This exception
    indicates the partial match of claiming to provide the interface,
    but not actually providing all the attributes required by an
    interface.

    It could also be considered an AttributeError, as when validation is
    off, that is the alternative exception (that might be) raised.
    However, future versions of this module may perform additional
    validation to catch TypeError's (e.g. function paramete matching).

    It was also tempting to raise a NotImplementedError, which captures
    some of the meaning. However, NotImplementedError is usually used
    as a marker for abstract methods or in-progress partial
    implementations.  In particular, a developer of an interface
    provider class may use NotImplementedError to satisy the interface
    where they know the code does not use a particular attribute of the
    interface.  Using a different exception causes less confusion.
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


def missing_attributes(obj, attributes):
    """Return a list of attributes not provided by an object."""
    missing = None
    for name in attributes:
        try:
            getattr(obj, name)
        except AttributeError:
            if missing is None:
                missing = []
            missing.append(name)
    return missing


_getattribute = object.__getattribute__


def mkdefault(name):
    def handle(self, *args, **kw):
        method = getattr(_getattribute(self, 'provider'), name)
        return method(*args, **kw)
    return handle


def handle_call(self, *args, **kwargs):
    return _getattribute(self, 'provider')(*args, **kwargs)


def handle_delattr(self, name):
    """
    Fail to delete an attribute.

    Interface attributes cannot be deleted through the interface, as that
    would make the interface invalid.  Non-interface attributes cannot be
    seen through the interface, so cannot be deleted.
    """
    if name in _getattribute(self, '_provider_attributes'):
        raise InterfaceConformanceError(
            'Cannot delete attribute {!r} through interface'.format(name))
    else:
        raise AttributeError(
            "{!r} interface has no attribute {!r}".format(
                _getattribute(self, '__class__').__name__, name))


def handle_dir(self):
    """Return the supported attributes of this interface."""
    return _getattribute(self, '_provider_attributes')


def handle_getattribute(self, name):
    """
    Check and return an attribute for the interface.

    When an interface object has an attribute accessed, check that
    the attribute is specified by the interface, and then retrieve
    it from the wrapped object.
    """
    if name in _getattribute(self, '_provider_attributes'):
        return getattr(_getattribute(self, 'provider'), name)
    else:
        raise AttributeError(
            "{!r} interface has no attribute {!r}".format(
                _getattribute(self, '__class__').__name__, name))


def handle_init(self, provider):
    """Wrap an object with an interface object."""
    # Use superclass __setattr__ in case interface defines __setattr__,
    # which points self's __setattr__ to underlying object.
    object.__setattr__(self, 'provider', provider)


def handle_iter(self):
    return iter(_getattribute(self, 'provider'))


def handle_next(self):
    return next(_getattribute(self, 'provider'))


def handle_setattr(self, name, value):
    """
    Set an attribute on an interface.

    Check that the attribute is specified by the interface, and then
    set it on the wrapped object.
    """
    if name in _getattribute(self, '_provider_attributes'):
        return setattr(_getattribute(self, 'provider'), name, value)
    else:
        raise AttributeError(
            "{!r} interface has no attribute {!r}".format(
                _getattribute(self, '__class__').__name__, name))


def handle_repr(self):
    """Return representation of interface."""
    return '<{}.{}({!r})>'.format(
        _getattribute(self, '__module__'),
        _getattribute(self, '__class__').__qualname__,
        _getattribute(self, 'provider'))

SPECIAL_METHODS = {
    '__call__': handle_call,
    # If __getattribute__ raises an AttributeError, any __getattr__
    # method (but not the implicit object.__getattr__) is then called.
    # Keep things simple by not adding any __getattr__ method.  Adding
    # __getattr__ to an an interface definition is OK, and works due to
    # __getattribute__ implementation calling getattr() on the wrapped
    # object.
    '__bytes__': mkdefault('__bytes__'),
    '__iter__': handle_iter,
    '__next__': handle_next,
    '__str__': mkdefault('__str__'),
}


class Interface(type):

    KEPT = frozenset((
        '__module__', '__qualname__',
    ))

    def __new__(meta, name, bases, dct):
        # Called when a new class is defined.  Use the dictionary of
        # declared attributes to create a mapping to the wrapped object
        class_attributes = {}
        provider_attributes = set()
        for base in bases:
            if isinstance(base, Interface):
                # base class is a super-interface of this interface
                # This interface provides all attributes from the base
                # interface
                provider_attributes |= base._provider_attributes

        for key, value in dct.items():
            # Almost all attributes on the interface are mapped to
            # return the equivalent attributes on the wrapped object.
            if key in meta.KEPT:
                # A few attributes need to be kept pointing to the
                # new interface object.
                class_attributes[key] = value
            elif key in SPECIAL_METHODS:
                # Special methods (e.g. __call__, __iter__) bypass the usual
                # getattribute machinery. To ensure that the interface behaves
                # in the same way as the original instance, create the special
                # method on the interface object, which acts in the same way
                # as the original object.  It is important to ensure that
                # interfaces work the same as the wrapped object, to avoid new
                # errors occurring in production code if the user wraps
                # interface casting in 'if __debug__:'.
                class_attributes[key] = SPECIAL_METHODS[key]
                # Also add the name to `provider_attributes` to ensure
                # that `__getattribute__` does not reject the name for
                # the cases where Python does go through the usual
                # process, e.g. a literal `x.__iter__`
                provider_attributes.add(key)
            else:
                # Attributes and functions are mapped using `__getattribute__`.
                # Any other values (e.g. docstrings) are not accessible through
                # provider instances.
                if isinstance(value, (Attribute, types.FunctionType)):
                    provider_attributes.add(key)
                # All values are added as class attributes, to make docs work.
                class_attributes[key] = value
        class_attributes['_provider_attributes'] = provider_attributes
        # Default attributes of all interfaces.  The methods that must be
        # present to make an instance act as an interface.
        class_attributes.update({
            '__init__': handle_init,
            '__repr__': handle_repr,
            '__dir__': handle_dir,
            '__getattribute__': handle_getattribute,
            '__setattr__': handle_setattr,
            '__delattr__': handle_delattr,
        })
        interface = super().__new__(meta, name, bases, class_attributes)
        # An object wrapped by (a subclass of) the interface is
        # guaranteed to provide the matching attributes.
        interface._verified = (interface,)
        interface._unverified = ()

        return interface

    def __call__(interface, obj, validate=None):
        # Calling interface(object) will call this function first.  We
        # get a chance to return the same object if suitable.
        """Cast the object to this interface."""
        if type(obj) is interface:
            # If the object to be cast is already an instance of this
            # interface, just return the same object.
            return obj
        interface.raise_if_not_provided_by(obj, validate)
        # If interface is provided by object, call type.__call__ which creates
        # a wrapper object to enforce only this interface.
        # Use underlying object to avoid calling through multiple wrappers.
        return super().__call__(underlying_object(obj))

    def __instancecheck__(interface, instance):
        """
        Support interface checking through type hints.

        This creates an unusual class, where isinstance() returns whether an
        object provides the interface, but issubclass() returns whether a class
        is actually a subclass of an interface.  This supports using the
        interface for type hinting.  One day Python may support a special
        method checking if types are consistent, so users should not rely on
        this behaviour, but should use `provided_by` directly.
        """
        return interface.provided_by(instance)

    def cast(interface, source):
        """Attempt to cast one interface to another.

        Whether this works depends on whether the underlying object supports
        this interface.
        """
        return interface(underlying_object(source))

    def raise_if_not_provided_by(interface, obj, validate=None):
        """Check if object provides the interface.

        :raise: an informative error if not. For example, a
        non-implemented attribute is returned in the exception.
        """
        obj_type = type(obj)
        if issubclass(obj_type, interface._verified):
            # an instance of a class that has been verified to provide
            # the interface, so it must support all operations
            if validate:
                missing = missing_attributes(
                    obj, interface._provider_attributes)
                if missing:
                    raise InterfaceConformanceError(mkmessage(obj, missing))
        elif (
            issubclass(obj_type, interface._unverified) or (
                issubclass(obj_type, DynamicInterface._verified) or
                issubclass(obj_type, DynamicInterface._unverified)
                ) and obj.provides_interface(interface)
        ):
            # The object claims to provide the interface, either by
            # implementing the interface, or by implementing the
            # `DynamicInterface` interface and returning True from the
            # `provides_interface` method.  Since it is just a claim, verify
            # that the attributes are supported.  If `validate` is False or is
            # not set and code is optimised, accept claims without validating.
            if validate is None and __debug__ or validate:
                missing = missing_attributes(
                    obj, interface._provider_attributes)
                if missing:
                    raise InterfaceConformanceError(mkmessage(obj, missing))
        else:
            raise TypeError(
                'Object {} does not provide interface {}'. format(
                    obj, interface.__name__))

    def register_implementation(interface, cls):
        """Register a provider class to the interface."""
        issubclass(cls, cls)      # ensure cls can appear on both sides
        for base in interface.__mro__:
            if (
                isinstance(base, Interface) and
                cls not in base._verified and
                cls not in base._unverified
            ):
                base._unverified += (cls,)

    def implemented_by(interface, cls):
        """Check if class claims to provide the interface.

        :return: True if interface is implemented by the class, else False.
        """
        # Contrast this function with `provided_by`. Note that DynamicInterface
        # classes cannot dynamically claim to implement an interface.
        return (
            issubclass(cls, interface._verified) or
            issubclass(cls, interface._unverified)
        )

    def provided_by(interface, obj):
        """Check if object claims to provide the interface.

        :return: True if interface is provided by the object, else False.
        """
        obj_type = type(obj)
        return (
            issubclass(obj_type, interface._verified) or
            issubclass(obj_type, interface._unverified) or (
                issubclass(obj_type, DynamicInterface._verified) or
                issubclass(obj_type, DynamicInterface._unverified)) and
                obj.provides_interface(interface)
            )

    def supported_by(interface, obj):
        """Check if underlying object claims to provide the interface.

        This is useful for feature checks with marker interfaces.
        """
        return interface.provided_by(underlying_object(obj))


class Attribute:

    pass


class Opaque(metaclass=Interface):

    """
    An interface with no attributes.

    This interface has two uses.

    It can be used as an opaque handle to an object.  A method can
    return an object wrapped by Opaque in order to make it inscrutable
    to callers.

    In addition, it provides an alternative to declaring interfaces
    using the metaclass.  Simply inherit from Opaque to create an
    interface.
    """


def underlying_object(interface):
    """Obtain the non-interface object wrapped by this interface."""
    obj = interface
    while isinstance(type(obj), Interface):
        obj = _getattribute(obj, 'provider')
    return obj


class DynamicInterface(Opaque):

    """Interface to dynamically provide other interfaces."""

    def provides_interface(self, interface):
        """Check whether this instance provides an interface.

        This method returns True when the interface class is provided,
        or False when the interface is not provided.
        """


def implements(*interfaces):
    """Decorator to mark a class as implementing an interface."""
    # The decorator does not wrap the class. It simply runs the
    # `register_implementation` method for each interface, and returns
    # the original class.  This handily avoids many of the problems
    # typical of wrapping decorators. See
    # http://blog.dscpl.com.au/2014/01/how-you-implemented-your-python.html
    def decorator(cls):
        for interface in interfaces:
            interface.register_implementation(cls)
        return cls
    return decorator
