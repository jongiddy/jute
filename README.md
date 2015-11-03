# jute
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

```
import sys
from jute import Interface
class Writable(Interface):
    def write(self, buf):
        "Write the string buf."

class StdoutWriter(Writable.Provider):
    def flush(self):
        sys.stdout.flush()
    def write(self, buf):
       sys.stdout.write(buf)

def output(writer, buf):
    if __debug__:
        writer = Writable(writer)
    writer.write(buf)
    writer.flush()

out = StdoutWriter()
output(out, 'Hello, World!')
```

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

```
Writable.register_implementation(file)
```
