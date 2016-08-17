Define an Interface
===================

Define an interface by subclassing :py:class:`jute.Opaque`.

.. code-block:: python

    import jute

    class Writable(jute.Opaque):
        def write(self, buf):
            """Function to write a string."""

Subclassing :py:class:`jute.Opaque` indicates that this class is an interface.
The interface requires implementations to provide the attributes defined in the class definition (:py:data:`write`) and in the super-class.
:py:class:`jute.Opaque` is an interface containing no attributes.
Hence, the :py:class:`Writable` interface only requires the attribute :py:data:`write`.

Interfaces can be subclassed further to add more attributes:

.. code-block:: python

    class BufferedWritable(Writable):
        def flush(self):
            """Flush any pending output."""

Interface :py:class:`BufferedWritable` requires implementations to provide both :py:data:`write` and :py:data:`flush` attributes.

Objects can provide the same syntactical interface, but different semantics.
These differences can be represented by interface hierarchies with no
additional attributes:

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

Interfaces can define non-method attributes using the :py:class:`jute.Attribute` class:

.. code-block:: python

    class BufferedWritableFile(BufferedWritable):

        fd = jute.Attribute("The file descriptor of the file to be written", type=int)
