from setuptools import setup, find_packages

VERSION = (0, 1)
__version__ = VERSION
__versionstr__ = ".".join(map(str, VERSION))

setup(
    name = "yowie",
    version = __versionstr__,
    description = 'utilities for safe reading Python file-like objects',
    author = 'centrum holdings s.r.o',
    author_email='devel@centrumholdings.com',
    license = 'BSD',
    url='http://git.netcentrum.cz/projects/content/GIT/yowie.git/',

    packages = find_packages(
        where = '.',
        exclude = ('tests',)
    ),
    include_package_data = True,

    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = [
        'django',
        'setuptools>=0.6b1',
    ],
)
