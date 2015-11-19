Implement an Interface
======================

There are several ways to indicate that instances of a class provide an
interface. These are listed here, and for performance reasons, should typically
be considered in the order that they appear.

Register a class that implements the interface
----------------------------------------------

For classes that define all attributes of an interface, decorate the class with
``jute.implements``.

.. code-block:: python

   @jute.implements(BufferedWritable)
   class OutputWriter:
       def write(self, buf):
           sys.stdout.write(buf)
       def flush(self):
           sys.stdout.flush()

If it is not possible to decorate a class, use the interface's
``register_implementation`` method to specify a class as an implementation of the
interface.

.. code-block:: python

   BufferedWritable.register_implementation(file)

In either of the above cases, the interface is verified once, during
registration.

Register a class whose instances provide the interface
------------------------------------------------------

Sometimes a class does not define all interface attributes, but instances of
the class will, typically through the ``__init__`` or ``__getattr__`` methods.  In
this case, subclass the interface's ``Provider`` attribute.

.. code-block:: python

   class ErrorWriter(BufferedWritable.Provider):
       def __init__(self):
           self.write = sys.stderr.write
       def __getattr__(self, name):
           if name == 'flush':
               def flush(buf):
                   sys.stderr.flush(buf)
               return flush
           raise AttributeError(name)

An interface's ``Provider`` attribute is an empty class, adding no additional
attributes or metaclasses to the implementing class.

Subclassing an interface's Provider attribute indicates a claim to implement
the interface.  This claim is verified during each conversion to the interface,
and hence is slower than registering an implementation.

If it is not possible to subclass the class, use the interface's
``register_provider`` method to specify that class instances will provide the
interface. Note that ``register_provider`` takes the class whose instances will
provide the interface, not a class instance.

.. code-block:: python

   Writable.register_provider(ssl.SSLSocket)

(Note, this particular class could also have used ``register_implementation``).

Dynamically indicate that an instance provides the interface
------------------------------------------------------------

Sometimes, especially for wrapper classes, it is useful to declare support for
an interface dynamically.  Dynamic implementations are declared using the
``jute.Dynamic`` interface, which provides a single method ``provides_interface``:

.. code-block:: python

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

Note, this object may print "Accessing attribute write" twice.  The first time
is during interface verification, which will not actually call the function.
This may be an issue if ``__getattr__`` performs non-trivial work to resolve the
attribute.
