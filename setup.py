from distutils.core import setup

LONGDESC = '''
Although duck typing is generally considered the Pythonic way of dealing with
object compatibility, it assumes that syntactic compatibility implies semantic
compatibility.  Interfaces provide an explicit way to express semantic
compatibility.

Most existing interface modules for Python (e.g. ``abc`` and
``zope.interface``) check that implementing classes provide all the attributes
specified in the interface.  But they ignore the other side of the contract,
failing to ensure that the receiver of the interface only calls operations
specified in the interface.  The ``jute`` module checks both, ensuring that
code works with any provider of the interface, not just the provider with
which it was tested.
'''

GITHUB_URL = 'https://github.com/jongiddy/jute'
VERSION = '0.1.2'

setup(
    name='jute',
    packages=['jute'],
    package_dir={'jute': 'python3/jute'},
    version=VERSION,
    description='Interface module that verifies both providers and callers',
    keywords=['interface', 'polymorphism'],
    longdesc=LONGDESC,
    author='Jonathan Patrick Giddy',
    author_email='jongiddy@gmail.com',
    url=GITHUB_URL,
    download_url='{}/tarball/v{}'.format(GITHUB_URL, VERSION),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
