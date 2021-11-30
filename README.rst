sumtypes
========

.. image:: https://travis-ci.org/radix/sumtypes.svg?branch=master
    :target: https://travis-ci.org/radix/sumtypes

sumtypes provides Algebraic Data Types for Python. The main benefit is the
implementation of Sum Types (aka `Tagged Unions`_), which Python doesn't have
any native representation for. Product Types are just objects with multiple
attributes.

.. _`Tagged Unions`: http://en.wikipedia.org/wiki/Tagged_union

Documentation is at https://sumtypes.readthedocs.org/

This module uses the `attrs`_ library to provide features like attribute
validation and defaults.

.. _`attrs`: http://pypi.python.org/pypi/attrs

Example
=======

Decorate your classes to make them a sum type:

.. code:: python

    import attr
    from sumtypes import sumtype, constructor, match

    @sumtype
    class MyType(object):
        # constructors specify names for their arguments
        MyConstructor = constructor('x')
        AnotherConstructor = constructor('x', 'y')

        # You can also make use of any feature of the attrs
        # package by using attr.ib in constructors
        ThirdConstructor = constructor(
            one=attr.ib(default=42),
            two=attr.ib(validator=attr.validators.instance_of(int)))

(`attrs package`_, and `attr.ib documentation`_)

.. _`attrs package`: https://pypi.python.org/pypi/attrs
.. _`attr.ib documentation`: http://attrs.readthedocs.org/en/stable/api.html#attr.ib

Then construct them by calling the constructors:

.. code:: python

    v = MyType.MyConstructor(1)
    v2 = MyType.AnotherConstructor('foo', 2)

You can get the values from the tagged objects:

.. code:: python

    assert v.x == 1
    assert v2.x == 'foo'
    assert v2.y == 2

You check the constructor used:

.. code:: python

    assert type(v) is MyType.MyConstructor

And, like Scala case classes, the constructor type is a subclass of the main
type:

.. code:: python

    assert isinstance(v, MyType)

And the tagged objects support equality:

.. code:: python

    assert v == MyType.MyConstructor(1)
    assert v != MyType.MyConstructor(2)

Simple pattern matching is also supported. To write a function over all the
cases of a sum type:

.. code:: python

    @match(MyType)
    class get_number(object):
        def MyConstructor(x): return x
        def AnotherConstructor(x, y): return y
        def ThirdConstructor(one, two): return one + two

    assert get_number(v) == 1
    assert get_number(v2) == 2

``match`` ensures that all cases are handled. If you really want to write a
'partial function' (i.e. one that doesn't cover all cases), use
``match_partial``.


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


