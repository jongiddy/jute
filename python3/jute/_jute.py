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

    This is almost a :py:exc:`TypeError`, but an object provides two
    parts to its interface implementation: a claim to provide the
    interface, and the attributes that match the interface specification.
    This exception indicates the partial match of claiming to provide
    the interface, but not actually providing all the attributes
    required by an interface.

    It could also be considered an :py:exc:`AttributeError`, as when
    validation is off, that is the alternative exception (that might be)
    raised.  However, future versions of this module may perform
    additional validation to catch :py:exc:`TypeError`'s (e.g. function
    parameter matching).

    It was also tempting to raise a :py:exc:`NotImplementedError`, which
    captures some of the meaning. However, :py:exc:`NotImplementedError`
    is usually used as a marker for abstract methods or in-progress
    partial implementations.  In particular, a developer of an interface
    provider class may use :py:exc:`NotImplementedError` to satisfy the
    interface where they know the code does not use a particular
    attribute of the interface.  Using a different exception causes less
    confusion.
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class InvalidAttributeName(Exception):

    """
    Interface defines invalid attribute name.

    There are a small number of special attributes that are provided by
    the interface provider to implement the provider.  These attributes
    cannot be attributes of an interface.
    """

    def __init__(self, attribute):
        self.attribute = attribute

    def __str__(self):
        return 'Cannot specify {!r} attribute in interface'.format(
            self.attribute
        )


def missing_attributes(iface, obj, attributes):
    """Return a list of attributes not provided by an object."""
    missing = None
    for name in attributes:
        try:
            value = getattr(obj, name)
        except AttributeError:
            if missing is None:
                missing = []
            missing.append(name)
        else:
            for validator in attributes[name]:
                if isinstance(validator, Attribute):
                    if not isinstance(value, validator.type):
                        raise TypeError(
                            '{}.{} requires type {}, got type {}'.format(
                                iface, name, validator.type, type(value)
                            )
                        )

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


def handle_getattr(self, name):
    # If __getattribute__ raises an AttributeError, any __getattr__
    # method (but not the implicit object.__getattr__) is then
    # called.  Keep things simple by reserving the __getattr__
    # method, and raising an AttributeError in it.
    raise AttributeError(
        "{!r} interface has no attribute {!r}".format(
            _getattribute(self, '__class__').__name__, name))


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
    provider_attributes = _getattribute(self, '_provider_attributes')
    if name in provider_attributes:
        for validator in provider_attributes[name]:
            if isinstance(validator, Attribute):
                if not isinstance(value, validator.type):
                    raise TypeError(
                        '{}.{} requires type {}, got type {}'.format(
                            type(self), name, validator.type, type(value)
                        )
                    )
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
    '__iter__': handle_iter,
    '__next__': handle_next,
}


class Interface(type):

    """
    A metaclass to allow classes to define interfaces.

    Each class with this metaclass will create an interface allowing
    access only to the attributes in the class.  Attributes can be
    provided as functions or using the :py:class:`.Attribute` class.
    Any other types will be available as attributes of the interface
    class, but not as attributes of interface instances.

    An instances of the interface class is a called a provider.  A
    provider maps interface attributes to an underlying Python object.
    The provider behaves the same as the underlying object, but only
    allows access to the attributes named in the interface.
    """

    _KEPT = frozenset((
        '__module__', '__qualname__',
    ))

    # Default attributes of all interfaces.  The methods that must be
    # present to make an instance act as an interface.
    _DEFAULT_ATTRIBUTES = {
        '__init__': handle_init,
        '__repr__': handle_repr,
        '__dir__': handle_dir,
        '__getattr__': handle_getattr,
        '__getattribute__': handle_getattribute,
        '__setattr__': handle_setattr,
        '__delattr__': handle_delattr,
    }

    def __new__(meta, name, bases, dct):
        # Called when a new class is defined.  Use the dictionary of
        # declared attributes to create a mapping to the wrapped object
        class_attributes = meta._DEFAULT_ATTRIBUTES.copy()
        provider_attributes = dict()
        for base in bases:
            if isinstance(base, Interface):
                # base class is a super-interface of this interface
                # This interface provides all attributes from the base
                # interface
                for key in base._provider_attributes:
                    v = provider_attributes.get(key)
                    if v is None:
                        v = []
                        provider_attributes[key] = v
                    v.extend(base._provider_attributes[key])
        for key, value in dct.items():
            # Almost all attributes on the interface are mapped to
            # return the equivalent attributes on the wrapped object.
            if key in meta._KEPT:
                # A few attributes need to be kept pointing to the
                # new interface object.
                class_attributes[key] = value
            elif key in meta._DEFAULT_ATTRIBUTES:
                # these attributes are set in the Provider instance to
                # make it work, so cannot be set for the interface
                raise InvalidAttributeName(key)
            elif key.startswith('__') and key.endswith('__'):
                if isinstance(value, types.FunctionType):
                    func = SPECIAL_METHODS.get(key)
                    if func is None:
                        func = mkdefault(key)
                    # Special methods (e.g. __call__, __iter__) bypass the
                    # usual getattribute machinery. To ensure that the
                    # interface behaves in the same way as the original
                    # instance, create the special method on the interface
                    # object, which acts in the same way as the original
                    # object.  It is important to ensure that interfaces work
                    # the same as the wrapped object, to avoid new errors
                    # occurring in production code if the user wraps interface
                    # casting in 'if __debug__:'.
                    class_attributes[key] = func
                    # Also add the name to `provider_attributes` to ensure
                    # that `__getattribute__` does not reject the name for
                    # the cases where Python does go through the usual
                    # process, e.g. a literal `x.__iter__`
                    v = provider_attributes.get(key)
                    if v is None:
                        v = provider_attributes[key] = []
                    v.append(func)
                else:
                    # Add attribute to interface class, but not to provider
                    # instances.  This is appropriate for the interface
                    # docstring (``__doc__``), where we want to see the
                    # docstring when looking at the class (for generating
                    # documentation), but don't want it to exist for the
                    # provider.
                    class_attributes[key] = value
            else:
                # Attributes and functions are mapped using `__getattribute__`.
                # Any other values (e.g. docstrings) are not accessible through
                # provider instances.
                if isinstance(value, Attribute):
                    v = provider_attributes.get(key)
                    if v is None:
                        v = provider_attributes[key] = [value]
                    else:
                        # check that attribute subclasses previous types
                        for attr in v:
                            if not issubclass(value.type, attr.type):
                                raise InterfaceConformanceError(
                                    'Attribute {!r} in interface {!r} must'
                                    ' subclass {}'.format(
                                        key, name, attr.type
                                    )
                                )
                        v = provider_attributes[key] = [value]
                elif isinstance(value, types.FunctionType):
                    v = provider_attributes.get(key)
                    if v is None:
                        v = provider_attributes[key] = [value]
                    else:
                        v.append(value)
                # All values are added as class attributes, to allow
                # interface method docstrings to be read.
                class_attributes[key] = value
        class_attributes['_provider_attributes'] = provider_attributes
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

        This creates an unusual class, where :py:func:`isinstance` returns
        whether an object provides the interface, but :py:func:`issubclass`
        returns whether a class is actually a subclass of an interface.  This
        supports using the interface for type hinting.  One day Python may
        support a special method checking if types are consistent, so users
        should not rely on this behaviour, but should call the
        :py:meth:`.provided_by` method directly.
        """
        return interface.provided_by(instance)

    def cast(interface, source):
        '''
        Attempt to cast one interface to another.

        This method allows the caller to access another interface supported by
        the underlying object.  Use the :py:meth:`.cast` method sparingly,
        since it breaks the model of interface-based programming.

        Note that upcasting (casting an interface to a base interface) can be
        done by calling the interface constructor::

            class IFoo(jute.Opaque):
                """An interface."""

            class IFooBar(IFoo):
                """A sub-interface of IFoo."""

            class IBaz(jute.Opaque):
                """A completely different interface."""

            @implements(IFooBar, IBaz)
            class FooBarBaz:
                """A class that implements all the above interfaces."""

            fb1 = IFooBar(FooBarBaz())
            foo = IFoo(fb1)      # upcast does not need cast
            fb2 = IFooBar.cast(foo)  # downcast needs a cast
            baz = IBaz.cast(fb2)     # sidecast needs a cast
        '''
        return interface(underlying_object(source))

    def raise_if_not_provided_by(interface, obj, validate=None):
        """
        Return if object provides the interface. Raise an informative error if
        not.
        """
        obj_type = type(obj)
        if issubclass(obj_type, interface._verified):
            # an instance of a class that has been verified to provide
            # the interface, so it must support all operations
            if validate:
                missing = missing_attributes(
                    interface, obj, interface._provider_attributes)
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
                    interface, obj, interface._provider_attributes)
                if missing:
                    raise InterfaceConformanceError(mkmessage(obj, missing))

        else:
            raise TypeError(
                'Object {} does not provide interface {}'. format(
                    obj, interface.__name__))

    def register_implementation(interface, cls):
        """
        Register a provider class to the interface.

        This is useful for declaring that a standard or third-party class
        provides an interface, when it cannot be decorated with the
        :py:data:`.implements` decorator.
        """
        issubclass(cls, cls)      # ensure cls can appear on both sides
        for base in interface.__mro__:
            if (
                isinstance(base, Interface) and
                cls not in base._verified and
                cls not in base._unverified
            ):
                base._unverified += (cls,)

    def implemented_by(interface, cls):
        """
        Check if class claims to provide the interface.

        Note that classes that implement the :py:class:`.DynamicInterface`
        interface cannot dynamically claim to `implement` an interface,
        although individual instances can claim to `provide` an interface.

        :return bool: :py:obj:`True` if interface is implemented by the class,
            else :py:obj:`False`.
        """
        return (
            issubclass(cls, interface._verified) or
            issubclass(cls, interface._unverified)
        )

    def provided_by(interface, obj):
        """Check if object claims to provide the interface.

        This will be true if the object's class claims to provide the
        interface.  It will also be true if the object provides the
        :py:class:`.DynamicInterface` interface, and the
        :py:meth:`.DynamicInterface.provides_interface` method returns
        :py:obj:`True` when passed this interface.

        :return bool: :py:obj:`True` if interface is provided by the object,
            else :py:obj:`False`.
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
        """
        Check if underlying object claims to provide the interface.

        Although it allows the caller to see if the underlying object supports
        an interface, it does not provide access to the interface, unless the
        interfaces contain attributes in common.  This makes it most useful for
        performing feature checks for marker interfaces (interfaces that have
        the same syntax, but different semantics to the supplied interface).

        :return bool: :py:obj:`True` if the underlying object claims to provide
            the interface, or :py:obj:`False` otherwise.
        """
        return interface.provided_by(underlying_object(obj))


class Attribute:

    '''
    Specify a non-function attribute in an interface.

    :ivar description: The doc-string for the attribute.
    :ivar type: The type of a valid value for the attribute.

    Any attribute which is part of an interface, but is not a method,
    should be defined as an :py:class:`.Attribute`::

        class IExample(jute.Opaque):

            value = jute.Attribute()

            def double(self):
                """Return twice the value."""

        @implements(IExample)
        class Example:

            value = 1

            def double(self):
                return 2 * self.value
    '''

    def __init__(self, description=None, *, type=object):
        self.description = description
        self.type = type


class Opaque(metaclass=Interface):

    """
    An interface with no attributes.

    This interface has two uses.

    It provides the base class for other interfaces to inherit.

    In addition, it can be used as an opaque handle to an object.  A
    method can return an object wrapped by :py:class:`Opaque` in order
    to make it inscrutable to callers.
    """


def underlying_object(interface):
    """
    Obtain the non-interface object wrapped by this interface.

    Use the :py:func:`underlying_object` function sparingly, since it
    breaks the model of interface-based programming.  It is primarily
    useful for debugging.
    """
    obj = interface
    while isinstance(type(obj), Interface):
        obj = _getattribute(obj, 'provider')
    return obj


class DynamicInterface(Opaque):

    """Interface to dynamically provide other interfaces."""

    def provides_interface(self, interface):
        """Check whether this instance provides an interface.

        This method returns :py:obj:`True` when the interface class is
        provided, or :py:obj:`False` when the interface is not provided.
        """


def implements(*interfaces):
    """
    Decorator to mark a class as implementing the supplied interfaces.

    To implement an interface, the class instances must define all attributes
    in the interface.
    """
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
