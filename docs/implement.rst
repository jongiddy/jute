Implement an Interface
======================

There are several ways to indicate that instances of a class provide an
interface. These are listed here, and for performance reasons, should typically
be considered in the order that they appear.

Register a class that implements the interface
----------------------------------------------

To indicate that a class implements an interface, decorate the class with
:py:data:`jute.implements`.

.. code-block:: python

   @jute.implements(BufferedWritable)
   class OutputWriter:
       def write(self, buf):
           sys.stdout.write(buf)
       def flush(self):
           sys.stdout.flush()

If it is not possible to decorate the class, use the interface's
:py:data:`register_implementation` method to specify a class as an implementation of the
interface.

.. code-block:: python

   BufferedWritable.register_implementation(file)


Dynamically indicate that an instance provides the interface
------------------------------------------------------------

Sometimes, especially for wrapper classes, it is useful to declare support for
an interface dynamically.  Dynamic implementations are declared using the
:py:class:`jute.DynamicInterface` interface, which provides a single method :py:data:`provides_interface`:

.. code-block:: python

   @jute.implements(jute.DynamicInterface)
   class PrintAttributeAccessWrapper:
       def __init__(self, wrapped):
           self.wrapped = wrapped

       def __getattr__(self, name):
           # return the wrapped object's attributes
           print('Accessing attribute {}'.format(name))
           return getattr(self.wrapped, name)

       def provides_interface(self, interface):
           # Check wrapped object's support for interface.
           return interface.provided_by(self.wrapped)

Note, this object may print "Accessing attribute write" more than expected.
Interface verification uses :py:data:`getattr` to verify implementation of the interface.
This may be an issue if :py:data:`__getattr__` performs non-trivial work to resolve the
attribute.
