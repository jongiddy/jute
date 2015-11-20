from distutils.core import setup

GITHUB_URL = 'https://github.com/jongiddy/jute'
VERSION = '0.1.4'

setup(
    name='jute',
    packages=['jute'],
    package_dir={'jute': 'python3/jute'},
    version=VERSION,
    description='Interface module that verifies both providers and callers',
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
)
