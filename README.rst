sumtypes
========

.. image:: https://travis-ci.org/radix/sumtypes.svg?branch=master
    :target: https://travis-ci.org/radix/sumtypes

Sum Types (aka `Tagged Unions`_) for Python. Documentation is at
https://sumtypes.readthedocs.org/

.. _`Tagged Unions`: http://en.wikipedia.org/wiki/Tagged_union

Example
=======

Decorate your classes to make them a sum type:

.. code:: python

    @sumtype
    class MyType(object):
        MyConstructor = constructor(int)

        @constructor
        def AnotherConstructor(x, y):
            assert type(x) is str
            assert type(y) is int
            return (x, y)

Then construct them by calling the constructors:

.. code:: python

    v = MyType.MyConstructor(1)
    v2 = MyType.AnotherConstructor('foo', 2)

You can get the value from the tagged objects:

.. code:: python

    assert v.value == 1
    assert v2.value == ('foo', 2)

The type of the tagged objects is the type you declared:

.. code:: python

    assert type(v) is MyType

You can also introspect the constructor used:

.. code:: python

    assert v.constructor is MyType.MyConstructor

And the tagged objects have equality semantics, which you can use to do pattern
matching:

.. code:: python

    assert v == MyType.MyConstructor(1)
    assert v != MyType.MyConstructor(2)


See Also
========

Over the past few years, the ecosystem of libraries to help with functional
programming in Python has exploded. Here are some libraries I recommend:

- `effect`_ - a library for isolating side-effects
- `pyrsistent`_ - persistent (optimized immutable) data structures in Python
- `toolz`_ - a general library of pure FP functions
- `fn.py`_ - a Scala-inspired set of tools, including a weird lambda syntax, option type, and monads

.. _`effect`: https://pypi.python.org/pypi/effect/
.. _`pyrsistent`: https://pypi.python.org/pypi/pyrsistent/
.. _`toolz`: https://pypi.python.org/pypi/toolz
.. _`fn.py`: https://pypi.python.org/pypi/fn


Thanks
======

Thanks to Rackspace for allowing me to work on this project, and having an
*excellent* `open source employee contribution policy`_

.. _`open source employee contribution policy`: https://www.rackspace.com/blog/rackspaces-policy-on-contributing-to-open-source/


License
=======

sumtypes is licensed under the MIT license:

Copyright (C) 2014 Christopher Armstrong

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
