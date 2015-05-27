#!/usr/bin/env python
import setuptools

setuptools.setup(
    name="sumtypes",
    version="0.1a1",
    description="Sum Types, aka Tagged Unions, for Python",
    long_description=open('README.rst').read(),
    url="http://github.com/radix/sumtypes/",
    author="Christopher Armstrong",
    license="MIT",
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    modules=['sumtypes'],
    install_requires=[],
)
