from distutils.core import setup
setup(
    name='jute',
    packages=['jute'],
    package_dir={'jute': 'python3/jute'},
    version='0.1.1',
    description='An interface module that verifies both providers and callers',
    author='Jonathan Patrick Giddy',
    author_email='jongiddy@gmail.com',
    url='https://github.com/jongiddy/jute',
    download_url='https://github.com/jongiddy/jute/tarball/v0.1.1',
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
