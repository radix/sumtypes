#!/usr/bin/env python
import setuptools

setuptools.setup(
    name="sumtypes",
    version="0.1a6",
    description="Algebraic types for Python (notably providing Sum Types, aka "
                "Tagged Unions)",
    long_description=open('README.rst').read(),
    url="http://github.com/radix/sumtypes/",
    author="Christopher Armstrong",
    license="MIT",
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    py_modules=['sumtypes'],
    install_requires=['attrs'],
)
