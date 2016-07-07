from distutils.core import setup
import sys

GITHUB_URL = 'https://github.com/jongiddy/jute'
VERSION = '0.2.1'


if sys.version_info[0] < 3:
    sys.exit('The jute package requires Python 3.')


def contents_of(filename):
    with open(filename, encoding='utf-8') as f:
        return f.read()

setup(
    name='jute',
    packages=['jute'],
    package_dir={'jute': 'python3/jute'},
    version=VERSION,
    description='Interface module that verifies both providers and callers',
    long_description=contents_of('README.rst'),
    keywords=['interface', 'polymorphism'],
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
    extras_require={
        'doc': [
            "pyenchant",  # pre-requisite for sphinxcontrib-spelling
            "sphinx",
            "sphinxcontrib-spelling",
        ],
    },
)
