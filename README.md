# jute

Yet another interface module for Python 3.

Although duck typing is generally considered the Pythonic way of dealing with
object compatibility, it makes the assumption that syntactic compatibility
indicates semantic compatibility.  Interfaces provide a way to indicate
semantic compatibility directly.

Most existing interface modules for Python (e.g. `abc` and `zope.interface`)
check that implementing classes provide all the attributes specified in the
interface.  But they ignore the other side of the contract, failing to ensure
that the receiver of the interface only calls operations specified in the
interface.  This module checks both, ensuring that code will work with any
provider of the interface, not just the implementation with which it was tested.

Jute interfaces have minimal impact on the implementing classes.  The interface
hierarchy and the implementer hierarchy are completely distinct, so you don't
get tied up in knots getting a sub-class to implement a sub-interface when the
super-class already implements the super-interface.

## Define an Interface

Define an interface by subclassing `jute.Interface`.

```python
import jute

class Writable(jute.Interface):
    def write(self, buf):
        """Function to write a string."""
```

Interfaces can be subclassed:

```python
class BufferedWritable(Writable):
    def flush(self):
        """Flush any pending output."""
```

Interface `BufferedWritable` requires both `write` and `flush` attributes to be
provided.

Objects providing the same syntax, but different semantics can be represented
by empty interfaces, adding no attributes, but more specific semantics.

```python
class LineBufferedWritable(BufferedWritable):
    """
    No additional operations, but indicates the semantic information
    that the buffer is flushed when a newline occurs.
    """

# need line buffering here
if LineBufferedWritable.supported_by(out):
    out.write(buf)
else:
    # more expensive operation
    add_line_buffering(out, buf)
```

## Implement an Interface

There are several ways to indicate that instances of a class provide an
interface. These are listed here, and for performance reasons, should typically
be considered in the order that they appear.

### Register a class that implements the interface

For classes that define all attributes of an interface, decorate the class with
`jute.implements`.

```python
@jute.implements(BufferedWritable)
class OutputWriter:
    def write(self, buf):
        sys.stdout.write(buf)
    def flush(self):
        sys.stdout.flush()
```

If it is not possible to decorate a class, use the interface's
`register_implementation` method to specify a class as an implementation of the
interface.

```python
BufferedWritable.register_implementation(file)
```

In either of the above cases, the interface is verified once, during
registration.

### Register a class whose instances provide the interface

Sometimes a class does not define all interface attributes, but instances of
the class will, typically through the `__init__` or `__getattr__` methods.  In
this case, subclass the interface's `Provider` attribute.

```python
class ErrorWriter(BufferedWritable.Provider):
    def __init__(self):
        self.write = sys.stderr.write
    def __getattr__(self, name):
        if name == 'flush':
            def flush(buf):
                sys.stderr.flush(buf)
            return flush
        raise AttributeError(name)
```

An interface's `Provider` attribute is an empty class, adding no additional
attributes or metaclasses to the implementing class.

Subclassing an interface's Provider attribute indicates a claim to implement
the interface.  This claim is verified during each conversion to the interface,
and hence is slower than registering an implementation.

If it is not possible to subclass the class, use the interface's
`register_provider` method to specify that class instances will provide the
interface. Note that `register_provider` takes the class whose instances will
provide the interface, not a class instance.

```python
Writable.register_provider(ssl.SSLSocket)
```

(Note, this particular class could also have used `register_implementation`).

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

Note, this object may print "Accessing attribute write" twice.  The first time
is during interface verification, which will not actually call the function.
This may be an issue if `__getattr__` performs non-trivial work to resolve the
attribute.

## Use an Interface

To use interfaces, cast an object to the interface by wrapping the object with
the interface (`Writable(object)`)

To prevent interface checks from affecting performance, consider putting
interface casts inside `if __debug__:` clauses. This performs interface checks
during debugging, but production code can run faster using the original objects
by running Python with the `-O` flag.

```python
def write_hello(writer):
    if __debug__:
        writer = Writer(writer)
    writer.write('Hello\n')

output = OutputWriter()
error = ErrorWriter()
wrapped = PrintAttributeAccessWrapper(error)
write_hello(output)
write_hello(error)
write_hello(wrapped)
```

Not only is the object checked that it supports the `write` attribute.  Uses
of the interface are checked that they do not use non-supported attributes.

```python
def broken_write_hello(writer):
    if __debug__:
        writer = Writable(writer)
    writer.write('hello')
    writer.flush()

broken_write_hello(OutputWriter())
```

In the above code, `writer` will be replaced by the interface, and the attempt
to use `flush`, which is not part of the interface, will fail, even though the
passed object does support that attribute.

In optimised Python, `broken_hello_world` will use the original object, and
should run faster without the intervening interface replacement.  In this case,
the code will work with the current implementation, but may fail if a different
object, that does not support `flush`, is passed.  Hopefully, by using `jute`
this bug was caught during development.

Interfaces can also be returned from a function.  This is useful to ensure that
callers are only using the "public" attributes of the returned object.  This
makes it easier to modify the implementation to return a different object. As
long as the returned object satisfies the interface, all code should continue
to work.

```python
def get_output():
    output = sys.stdout
    if __debug__:
        output = Writable(output)
    return output
```

This definition of `get_output` can be changed to use a non-flushable object
(e.g. an `ssl.SSLSocket`) with no risk that code that uses the returned value
relies on non-supported attributes such as `flush`.

Returning interfaces can also be used to divide a complex object's method into
those needed for specific roles, and only pass the appropriate subset to code
implementing the roles.  For example, an object which signals a condition can
be divided into a Notifiable interface and a Watchable interface, to prevent a
watching object from accidentally notifying completion.

```python
class Notifiable(jute.Interface):
    def notify(self):
        """Notify that an event occurred."""

class Watchable(jute.Interface):
    def watch(self, callback):
        """Get called when an event occurs."""

@jute.implements(Notifiable, Watchable)
class Signal:
    def __init__(self):
        self.result = None
        self.callbacks = []

    def notify(self, result):
        self.result = result
        for f in self.callbacks:
            f(result)
        self.callbacks = []

    def watch(self, callback):
        if self.result:
            callback(result)
        else:
            self.callbacks.append(callback)

def do_task():
    signal = Signal()
    do_async(subtask, Notifiable(signal))
    return Watchable(signal)

task = do_task()
task.watch(func)  # OK
task.notify(3)    # Error
```