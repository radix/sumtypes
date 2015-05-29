"""
Sum Types (aka Tagged Unions) for Python.

Decorate your classes to make them a sum type::

    @sumtype
    class MyType(object):
        # constructors specify names for their arguments
        MyConstructor = constructor('x')
        AnotherConstructor = constructor('x', 'y')

        # You can also make use of any feature of the excellent `attribs`_
        # package by using attr.ib instances in constructors
        ThirdConstructor = constructor(
            ('one', attr.ib(default=42)))

Then construct them by calling the constructors::

    v = MyType.MyConstructor(1)
    v2 = MyType.AnotherConstructor('foo', 2)

You can get the values from the tagged objects::

    assert v.x == 1
    assert v2.x == 'foo'
    assert v2.y == 2

You check the constructor used::

    assert type(v) is MyType.MyConstructor

And, like Scala case classes, the constructor type is a subclass of the main
type::

    assert isinstance(v, MyType)

And the tagged objects support equality::

    assert v == MyType.MyConstructor(1)
    assert v != MyType.MyConstructor(2)

Simple pattern matching is also supported. To write a function over all the
cases of a sum type::

    @match
    class get_number(object):
        def MyConstructor(x): return x
        def AnotherConstructor(x, y): return y

:func:`match` ensures that all cases are handled. If you really want to write a
'partial function' (i.e. one that doesn't cover all cases), use
:func:`match_partial`.
"""

import sys

import attr

PY3 = sys.version_info[0] == 3

try:
    from itertools import izip_longest
except ImportError:
    from itertools import zip_longest as izip_longest


class _Constructor(object):
    def __init__(self, attrs):
        self._attrs = attrs


def constructor(*argspec):
    """
    Register a constructor for the parent sum type.

    :param argspec: each argument should be either a simple string indicating
    the name of an attribute, or the result of :func:`attrib`.
    """
    attrs = [(ib, attr.ib()) if not isinstance(ib, tuple) else ib
             for ib in argspec]
    return _Constructor(attrs)


def _cmp_iterators(i1, i2):
    sentinal = object()
    return all(a == b for a, b in izip_longest(i1, i2, fillvalue=sentinal))


def _get_attrs(obj):
    return (getattr(obj, attr[0]) for attr in obj._sumtype_attribs)


def _get_constructors(klass):
    for k, v in vars(klass).items():
        if type(v) is _Constructor:
            yield k, v


def sumtype(klass):
    """
    A class decorator that treats the class like a sum type.

    Constructors should be wrapped/decorated with :obj:`constructor`.

    Note that this will overwrite ``__repr__``, ``__eq__``, and ``__ne__`` on
    your objects. ``__init__`` is untouched, but it would be kind of weird to
    make something a sum type *and* have an ``__init__``, so I recommend
    against that.
    """
    constructor_names = []
    for cname, constructor in _get_constructors(klass):
        new_constructor = _make_constructor(cname, klass, constructor._attrs)
        setattr(klass, cname, new_constructor)
        constructor_names.append(cname)
    klass._sumtype_constructor_names = constructor_names
    return klass


def _make_constructor(name, type_, attrs):
    """Create a type specific to the constructor."""
    d = dict(attrs)
    d['_sumtype_attribs'] = [x for x in attrs]
    t = type(name, (type_,), d)
    t = attr.s(t, repr_ns=type_.__name__)
    return t


class PartialMatchError(Exception):
    """Raised when a match function doesn't cover all cases."""
    def __init__(self, unhandled_cases):
        self.unhandled_cases = unhandled_cases

    def __str__(self):
        return "Unhandled cases: %r" % (self.unhandled_cases,)


def match(adt):
    """
    A class decorator that lets you write functions over all the constructors
    of a sum type. You provide the cases by naming the methods of the class the
    same as the constructors of the type, and the appropriate one will be
    called based on the way the value was constructed.

    e.g.::

        @sumtype
        class MyType(object):
            NamedNum = constructor('name', 'num')
            AnonymousNum = constructor('num')

        @match(MyType)
        class get_num(object):
            def NamedNum(name, num): return num
            def AnonymousNum(num): return num

        assert get_num(MyType.NamedNum('foo', 1)) == 1
        assert get_num(MyType.AnonymousNum(2)) == 2

    If not all constructors are handled, :obj:`PartialMatchError` will be
    raised.
    """
    def matchit(klass):
        constructor_names = set(adt._sumtype_constructor_names)
        unhandled = constructor_names - set(dir(klass))
        if unhandled:
            raise PartialMatchError(unhandled)
        return _matchit(klass)
    return matchit


def _matchit(klass):
    def run(value):
        constructor_type = type(value)
        cname = constructor_type.__name__
        handler = getattr(klass, cname, None)
        if handler is None:
            raise PartialMatchError([cname])
        if PY3:
            case = handler
        else:
            case = handler.im_func
        args = _get_attrs(value)
        return case(*args)

    if hasattr(klass, '__name__'):
        run.__name__ = klass.__name__
    if hasattr(klass, '__doc__'):
        run.__doc__ = klass.__doc__
    return run


def match_partial(adt):
    """
    Like :func:`match`, but it allows not covering all the constructor cases.

    In the case that
    """
    return _matchit
