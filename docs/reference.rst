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
   validation to catch TypeError's (e.g. function parameter matching).


.. py:metaclass:: Interface

   Create a class representing an interface.
   An interface instance will only provide the attributes defined in the class definition.

   .. py:method:: __call__(cls)

      Convert an object that provides an interface to a provider instance.

   .. py:method:: register_implementation(cls)

      Register a class that provides the interface.
      An implementing class has all the attributes defined in the interface.
      Therefore, the class can be verified once, rather than verifying each instance separately.

   .. py:method:: implemented_by(cls)

      Check if class claims to provide the interface.
      Both implementing and providing classes return True.
      However, dynamic providers return False.

      :return: True if interface is implemented by the class, else False.

   .. py:method:: provided_by(obj)

      Check if object claims to provide the interface.
      This will be true if the object's class claims to provide the interface.
      It will also be true if the object's class implements or provides the ``DynamicInterface`` interface, and the object's ``provides_interface`` method returns ``True`` when passed this interface.

      :return: True if the object claims to provide the interface, or False otherwise.

   .. note::

      The remaining functions break the abstraction provided by interfaces,
      allowing the caller to obtain more information about the wrapped object.

   .. py:method:: supported_by(obj)

      Check if underlying object claims to provide the interface.

      Although it allows the caller to see if the underlying object supports
      an interface, it does not provide access to the interface, unless the interfaces contain attributes in common.
      This makes it most useful for performing feature checks for marker interfaces
      (interfaces that have the same syntax, but different semantics to the supplied interface).

      :return: True if the underlying object claims to provide the interface,
         or False otherwise.

   .. py:method:: cast(source)

      Attempt to cast one interface to another.

      The ``cast`` method allows the caller to access another supported interface.
      Whether this works depends on whether the underlying object supports this interface.
      Use of ``cast`` should be avoided, since it breaks the model of interface-based programming.

.. py:decorator:: implements(*interfaces)

   Decorator to mark a class as implementing the supplied interfaces.

   To implement an interface, the class instances must define all attributes in the interface.


.. py:clss:: DynamicInterface(provider)

   Interface to dynamically provide other interfaces.

   .. py:method:: provides_interface(self, interface)

      Check whether this instance provides an interface.

      This method returns True when the interface class is provided,
      or False when the interface is not provided.


.. py:function:: underlying_object(interface)

   Obtain the non-interface object wrapped by this interface.

   Use of the ``underlying_object`` function should be avoided, since it breaks the model of interface-based programming.
   It is primarily useful for debugging.

