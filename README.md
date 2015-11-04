# jute

Yet another interface module for Python.

Although duck typing is generally considered the Pythonic way of dealing
with object compatibility, it's major problem is that it relies on
syntactical compatibility to indicate semantic compatibility.
Interfaces provide a way to indicate semantic compatibility
directly.

Most existing interface modules for Python (e.g. `abc` and `zope.interface`)
check that implementing classes provide all the attributes specified in the
interface.  But they ignore the other side of the contract, failing to ensure
that the receiver of the interface only calls operations specified in the
interface.  This module checks both, ensuring that called code will work with
any provider of the interface, not just the one with which it was tested.

Interfaces have minimal impact on the implementing classes.  The interface
hierarchy and the implementer hierarchy are completely distinct, so you don't
get tied up in knots getting a sub-class to implement a sub-interface when the
super-class already implements the super-interface.

## Define an Interface

Define an interface by subclassing `jute.Interface`.

```python
import jute


class Workable(jute.Interface):
    x = 1  # an attribute
    def work(self, val):
        """Function to do some work."""
```

## Implement an Interface

There are several ways to indicate that instances of a class provide an
interface. These are listed here, and for performance reasons, should typically
be considered in the order that they appear.

### Register a class that implements the interface

For classes that define all attributes of an interface, decorate the class with
`jute.implements`.

```python
@jute.implements(Workable)
class DoubleWork:
    x = 2
    def work(self, val):
        return val + val
```

If it is not possible to decorate a class, use the interface's
`register_implementation` method to specify a class as an implementation of the
interface.  Again, the class must define all interface attributes:

```python
Workable.register_implementation(ThirdPartyImplementation)
```

In either of the above cases, the interface is verified once, during
registration.

### Register a class whose instances provide the interface

Sometimes a class does not define all interface attributes, but instances of
the class will, typically through the `__init__` or `__getattr__` methods.  In
this case, subclass the interface's `Provider` attribute.

```python
class SquareWork(Workable.Provider):
    def __init__(self):
        self.x = 1
    def __getattr__(self, name):
        if name == 'work':
            def work(val):
                return val * val
            return work
        raise AttributeError(name)
```

An interface's `Provider` is an empty class, adding no additional attributes or
metaclasses to the implementing class.

Subclassing an interface's Provider attribute indicates a claim to implement
the interface.  This claim is verified during each conversion to the interface,
and hence is slower than registering an implementation.

If it is not possible to subclass the class, use the interface's
`register_provider` method to specify that class instances will provide the
interface:

```python
Workable.register_provider(ThirdPartyProvider)
```

### Dynamically indicate that an instance provides the interface

Sometimes, especially for wrapper classes, it is useful to declare support for
an interface dynamically.  Dynamic implementations are declared using the
`jute.Dynamic` interface, which provides a single method `provides_interface`:

```python
class PrintAttributeAccessWrapper(jute.Dynamic.Provider):
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def __getattr__(self, name):
        # return the wrapped object's attributes
        print('Accessing attribute {}'.format(name))
        return getattr(self.wrapped, name)

    def provides_interface(self, interface):
        # Check wrapped object's support for interface.
        return interface.provided_by(self.wrapped)
```

Note, if you pass this object to `do_work`, it will print "Accessing attribute
work" twice.  The first time is during interface verification, which will not
actually call the function.  However, this may be an issue if `__getattr__`
performs non-trivial work to resolve the attribute.

## Use an Interface

To use interfaces, cast an object to the interface by wrapping the object with
the interface (`Workable(object)`)

To prevent interface checks from affecting performance, consider putting
interface casts inside `if __debug__:` clauses. This performs interface checks
during debugging, but production code can run faster using the original objects
by running Python with the `-O` flag.

```python
def do_work(worker):
    if __debug__:
        worker = Workable(worker)
    return worker.work(5)

doubler = DoubleWork()
squarer = SquareWork()
wrapped = PrintAttributeAccessWrapper(squarer)
assert do_work(doubler) == 10
assert do_work(squarer) == 25
assert do_work(wrapped) == 25
```

Not only is the object checked that it supports the `work` attribute.  Uses
of the interface are checked that they do not use non-supported attributes.

```python
@jute.implements(Workable)
class WorkingHard:
    x = 4

    def work(self, val):
        return val

    def dumpx(self):
        print(self.x)


def broken_do_work(worker):
    if __debug__:
        worker = Workable(worker)
    worker.dumpx()
    return worker.work(5)

broken_do_work(WorkingHard())
```

In the above code, `worker` will be replaced by the interface, and the attempt
to use `dumpx`, which is not part of the interface, will fail, even though the
passed object does support that attribute.

In optimised Python, `broken_do_worker` will use the original object, and
should run faster without the intervening interface replacement.  In this case,
the code will work with the current implementation, but may fail if a different
object, that does not support `dumpx`, is passed.  Hopefully, by using `jute`
this bug was caught during development.
