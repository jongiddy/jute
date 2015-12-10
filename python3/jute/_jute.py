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

Interfaces have minimal impact on the implementing classes.  Although
implementing classes must subclass an InterfaceProvider class, that
class is completely empty, adding no additional attributes or
metaclasses to the implementing class.

The interface hierarchy and the implementer hierarchy are completely
distinct, so you don't get tied up in knots getting a sub-class to
implement a sub-interface when the super-class already implements the
super-interface.

To prevent interface checks from affecting performance, we recommend
to code interface conversions inside ``if __debug__:`` clauses. This
can be used to allow interface checks during debugging, and production
code to use the original objects by running Python with the ``-O`` flag.

:Example:

>>> import sys
>>> from jute import Interface
>>> class Writable(Interface):
...     def write(self, buf):
...         "Write the string buf."
...
>>> class StdoutWriter(Writable.Provider):
...     def flush(self):
...         sys.stdout.flush()
...     def write(self, buf):
...         sys.stdout.write(buf)
...
>>> def output(writer, buf):
...     if __debug__:
...         writer = Writable(writer)
...     writer.write(buf)
...     writer.flush()
...
>>> out = StdoutWriter()
>>> output(out, 'Hello, World!')

In the above code, ``writer`` will be replaced by the interface, and the
attempt to use ``flush``, which is not part of the interface, will fail.

Subclassing an interface's Provider attribute indicates a claim to
implement the interface.  This claim is verified during conversion to
the interface, but only in non-optimised code.

In optimised Python, ``writer`` will use the original object, and should
run faster without the intervening interface replacement.  In this case,
the code will work with the current implementation, but may fail if a
different object, that does not support ``flush`` is passed.

Note, it is possible to use the `register_implementation` method to
specify a type as an implementation of interface, even if it cannot be
subclassed.  Hence, ``sys.stdout`` can be indicated as directly
satisfying the``Writable`` interface, using

>>> Writable.register_implementation(file)
"""


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


# Declare the base classes for the `Interface` class here so the
# metaclass `__new__` method can avoid running
# `issubclass(base, Interface)` during the creation of the `Interface`
# class, at a time when the name `Interface` does not exist.
_InterfaceBaseClasses = (object,)


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
    if name in _getattribute(self, '_provider_attributes'):
        raise InterfaceConformanceError(
            'Cannot delete attribute {!r} through interface'.format(name))
    else:
        raise AttributeError(
            "{!r} interface has no attribute {!r}".format(
                _getattribute(self, '__class__').__name__, name))


def handle_dir(self):
    return _getattribute(self, '_provider_attributes')


def handle_getattribute(self, name):
    if name in _getattribute(self, '_provider_attributes'):
        return getattr(_getattribute(self, 'provider'), name)
    else:
        raise AttributeError(
            "{!r} interface has no attribute {!r}".format(
                _getattribute(self, '__class__').__name__, name))


def handle_init(self, provider):
    # Use superclass __setattr__ in case interface defines __setattr__,
    # which points self's __setattr__ to underlying object.
    object.__setattr__(self, 'provider', provider)


def handle_iter(self):
    return iter(_getattribute(self, 'provider'))


def handle_next(self):
    return next(_getattribute(self, 'provider'))


def handle_setattr(self, name, value):
    if name in _getattribute(self, '_provider_attributes'):
        return setattr(_getattribute(self, 'provider'), name, value)
    else:
        raise AttributeError(
            "{!r} interface has no attribute {!r}".format(
                _getattribute(self, '__class__').__name__, name))


def handle_repr(self):
    return '<{}.{}({!r})>'.format(
        _getattribute(self, '__module__'),
        _getattribute(self, '__class__').__qualname__,
        _getattribute(self, 'provider'))

SPECIAL_METHODS = {
    '__call__': handle_call,
    '__delattr__': handle_delattr,
    '__dir__': handle_dir,
    # If __getattribute__ raises an AttributeError, any __getattr__
    # method (but not the implicit object.__getattr__) is then called.
    # Keep things simple by not adding any __getattr__ method.  Adding
    # __getattr__ to an an interface definition is OK, and works due to
    # __getattribute__ implementation calling getattr() on the wrapped
    # object.
    '__getattribute__': handle_getattribute,
    '__init__': handle_init,
    '__iter__': handle_iter,
    '__next__': handle_next,
    '__setattr__': handle_setattr,
    '__str__': mkdefault('__str__'),
    '__repr__': handle_repr,
}


class InterfaceMetaclass(type):

    KEPT = frozenset((
        '__module__', '__qualname__',
    ))

    def __new__(meta, name, bases, dct):
        # Called when a new class is defined.  Use the dictionary of
        # declared attributes to create a mapping to the wrapped object
        BaseInterfaceProviders = []
        class_attributes = {}
        provider_attributes = set()
        for base in bases:
            if (
                base not in _InterfaceBaseClasses and
                issubclass(base, Interface)
            ):
                # base class is a super-interface of this interface
                BaseInterfaceProviders.append(base.Provider)
                # This interface provides all attributes from the base
                # interface
                provider_attributes |= base._provider_attributes

        class Provider(*BaseInterfaceProviders):

            """Subclass this to express that instances provide interface.

            Subclassing this class indicates that the class implements
            the interface.  Since this class inherits the provider
            classes of super-interfaces, it also indicates that the
            class implements those interfaces as well.
            """

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
                # method on the Interface object, which acts in the same way
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
                # All other attributes are simply mapped using
                # `__getattribute__`.
                provider_attributes.add(key)
        class_attributes['Provider'] = Provider
        class_attributes['_provider_attributes'] = provider_attributes
        interface = super().__new__(meta, name, bases, class_attributes)
        # An object wrapped by (a subclass of) the interface is
        # guaranteed to provide the matching attributes.
        interface._verified = (interface,)
        interface._unverified = (interface.Provider,)
        return interface

    def __call__(interface, obj, validate=None):
        # Calling Interface(object) will call this function first.  We
        # get a chance to return the same object if suitable.
        """Cast the object to this interface."""
        if type(obj) is interface:
            # If the object to be cast is already an instance of this
            # interface, just return the same object.
            return obj
        interface.raise_if_not_provided_by(obj, validate)
        # create a wrapper object to enforce only this interface.
        return super().__call__(obj)

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
        if isinstance(obj, interface._verified):
            # an instance of a class that has been verified to provide
            # the interface, so it must support all operations
            if validate:
                missing = missing_attributes(
                    obj, interface._provider_attributes)
                if missing:
                    raise InterfaceConformanceError(mkmessage(obj, missing))
        elif (
            isinstance(obj, interface._unverified) or
            isinstance(obj, (Dynamic, Dynamic.Provider)) and
                obj.provides_interface(interface)
        ):
            # The object claims to provide the interface, either by
            # subclassing the interface's provider class, or by
            # implementing Dynamic and returning True from the provides
            # method.  Since it is just a claim, verify that the
            # attributes are supported.  If `validate` is False or is
            # not set and code is optimised, accept claims without
            # validating.
            if validate is None and __debug__ or validate:
                missing = missing_attributes(
                    obj, interface._provider_attributes)
                if missing:
                    raise InterfaceConformanceError(mkmessage(obj, missing))
        else:
            raise TypeError(
                'Object {} does not provide interface {}'. format(
                    obj, interface.__name__))

    def register_provider(interface, cls):
        """Register a provider class to the interface."""
        issubclass(cls, cls)      # ensure cls can appear on both sides
        for base in interface.__mro__:
            if (
                issubclass(base, Interface) and
                cls not in base._verified and
                cls not in base._unverified
            ):
                base._unverified += (cls,)

    def provided_by(interface, obj):
        """Check if object claims to provide the interface.

        :return: True if interface is provided by the object, else False.
        """
        return (
            isinstance(obj, interface._verified) or
            isinstance(obj, interface._unverified) or (
                isinstance(obj, Dynamic._verified) or
                isinstance(obj, Dynamic._unverified)) and
                obj.provides_interface(interface)
            )

    def supported_by(interface, obj):
        """Check if underlying object claims to provide the interface.

        This is useful for feature checks with marker interfaces.
        """
        return interface.provided_by(underlying_object(obj))

    def register_implementation(interface, cls):
        """Check if a provider implements the interface, and register it."""
        issubclass(cls, cls)      # ensure cls can appear on both sides
        missing = missing_attributes(cls, interface._provider_attributes)
        if missing:
            raise InterfaceConformanceError(mkmessage(cls, missing))
        for base in interface.__mro__:
            if issubclass(base, Interface) and cls not in base._verified:
                base._verified += (cls,)

    def implemented_by(interface, cls):
        """Check if class claims to provide the interface.

        :return: True if interface is implemented by the class, else False.
        """
        # Contrast this function with `provided_by`. Note that Dynamic Provider
        # classes cannot dynamically claim to implement an interface.
        return (
            issubclass(cls, interface._verified) or
            issubclass(cls, interface._unverified)
        )


class Interface(*_InterfaceBaseClasses, metaclass=InterfaceMetaclass):

    def __init__(self, provider):
        """Wrap an object with an interface object."""

    def __repr__(self):
        """Return representation of interface."""

    def __dir__(self):
        """Return the supported attributes of this interface."""

    def __getattribute__(self, name):
        """Check and return an attribute for the interface.

        When an interface object has an attribute accessed, check that
        the attribute is specified by the interface, and then retrieve
        it from the wrapped object.
        """

    def __setattr__(self, name, value):
        """Set an attribute on an interface.

        Check that the attribute is specified by the interface, and then
        set it on the wrapped object.
        """

    def __delattr__(self, name):
        """Fail to delete an attribute.

        Interface attributes cannot be deleted through the interface, as that
        would make the interface invalid.  Non-interface attributes cannot be
        seen through the interface, so cannot be deleted.
        """


def underlying_object(interface):
    """Obtain the non-interface object wrapped by this interface."""
    obj = interface
    while isinstance(obj, Interface):
        obj = _getattribute(obj, 'provider')
    return obj


class Dynamic(Interface):

    """Interface to dynamically provide other interfaces."""

    def provides_interface(self, interface):
        """Check whether this instance provides an interface.

        This method returns True when the interface class is provided,
        or False when the interface is not provided.
        """


def implements(*interfaces):
    """Decorator to mark a class as implementing an interface.

    The decorator does not wrap the class. It simply runs
    `register_implementation` for each interface, and returns the
    original class.  This handily avoids many of the problems typical of
    wrapping decorators. See
    http://blog.dscpl.com.au/2014/01/how-you-implemented-your-python.html
    """
    def decorator(cls):
        for interface in interfaces:
            interface.register_implementation(cls)
        return cls
    return decorator
