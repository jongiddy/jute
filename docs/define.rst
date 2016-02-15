Define an Interface
===================

Define an interface by setting a metaclass of ``jute.Interface``.

.. code-block:: python

    import jute

    class Writable(metaclass=jute.Interface):
        def write(self, buf):
            """Function to write a string."""

Interfaces can be subclassed:

.. code-block:: python

    class BufferedWritable(Writable):
        def flush(self):
            """Flush any pending output."""

Interface ``BufferedWritable`` requires both ``write`` and ``flush`` attributes to be
provided.

Objects can provide the same syntactical interface, but different semantics.
These differences can be represented by interface hierarchies with no
additional syntax:

.. code-block:: python

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

Subclassing the empty interface ``jute.Opaque`` provides an alternative way to define an interface.

.. code-block:: python

    import jute

    class Writable(jute.Opaque):
        def write(self, buf):
            """Function to write a string."""