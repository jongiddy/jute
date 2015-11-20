Jute is an interface module for Python 3 that verifies both providers and
receivers of the interface.

Although duck typing is generally considered the Pythonic way of dealing with
object compatibility, it assumes that syntactic compatibility implies semantic
compatibility.  Interfaces provide an explicit way to express semantic
compatibility.

Most existing interface modules for Python (e.g. ``abc`` and ``zope.interface``)
check that implementing classes provide all the attributes specified in the
interface.  But they ignore the other side of the contract, failing to ensure
that the receiver of the interface only calls operations specified by the
interface.

The ``jute`` module allows verification of both providers of the interface and
receivers of the interface, to ensure that code works with any provider of the
interface, not just the provider with which it was tested.

Documentation is available at http://jute.readthedocs.org/
