.. Jute documentation master file, created by
   sphinx-quickstart on Wed Nov 18 17:36:47 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Jute
====

Although duck typing is generally considered the Pythonic way of dealing with
object compatibility, it assumes that syntactic compatibility implies semantic
compatibility.  Interfaces provide an explicit way to express semantic
compatibility.

Most existing interface modules for Python (e.g. ``abc`` and ``zope.interface``)
check that implementing classes provide all the attributes specified in the
interface.  But they ignore the other side of the contract, failing to ensure
that the receiver of the interface only calls operations specified in the
interface.  The ``jute`` module checks both, ensuring that code works with any
provider of the interface, not just the provider with which it was tested.

Jute interfaces have minimal impact on the implementing classes.  The interface
hierarchy and the implementer hierarchy are completely distinct, so you don't
get tied up in knots getting a sub-class to implement a sub-interface when the
super-class already implements the super-interface.

Contents:

.. toctree::
   :maxdepth: 2

   define
   implement
   use
   reference


Indices and tables
==================

* :ref:`search`

