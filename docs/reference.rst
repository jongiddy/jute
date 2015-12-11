Module Reference
================

.. py:module:: jute

.. py:class:: InterfaceConformanceError

   Object does not conform to interface specification.

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


.. py:class:: Interface(provider)

   .. py:classmethod:: register_implementation(cls)

      Check if a class implements the interface, and register it.

   .. py:classmethod:: implemented_by(cls)

      Check if class claims to provide the interface.

      :return: True if interface is implemented by the class, else False.

   .. py:classmethod:: register_provider(cls)

      Register a provider class to the interface.

   .. py:classmethod:: provided_by(obj)

      Check if object claims to provide the interface.

      :return: True if the object claims to provide the interface, or False otherwise.

   .. note::

      The remaining functions break the abstraction provided by interfaces,
      allowing the caller to obtain more information about the wrapped object.

   .. py:classmethod:: supported_by(obj)

      Check if underlying object claims to provide the interface.

      Although it allows the caller to see if the underlying object supports
      any interface, since it does not provide access to the interface, its
      main use is to perform feature checks for marker interfaces (interfaces
      that have the same syntax, but different semantics to the supplied
      interface).

      :return: True if the underlying object claims to provide the interface,
         or False otherwise.

   .. py:classmethod:: cast(source)

      Attempt to cast one interface to another.

      The ``cast`` method allows the caller to access another supported interface.
      Whether this works depends on whether the underlying object supports this interface.
      Use of ``cast`` should be avoided, since it breaks the model of interface-based programming.


.. py:decorator:: implements(*interfaces)

   Decorator to mark a class as implementing the supplied interfaces.

   To implement an interface, the class must define all attributes in the interface.


.. py:decorator:: provides(*interfaces)

   Decorator to mark a class as providing the supplied interfaces.

   To provide an interface, the class instances must define all attributes in the interface.


.. py:class:: Dynamic(provider)

   Interface to dynamically provide other interfaces.

   .. py:method:: provides_interface(self, interface)

      Check whether this instance provides an interface.

      This method returns True when the interface class is provided,
      or False when the interface is not provided.


.. py:function:: underlying_object(interface)

   Obtain the non-interface object wrapped by this interface.

   Use of the ``underlying_object`` function should be avoided, since it breaks the model of interface-based programming.
   It is primarily useful for debugging.


