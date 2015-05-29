"""
Sum Types (aka Tagged Unions) for Python.

Decorate your classes to make them a sum type::

    @sumtype
    class MyType(object):

        # constructors specify names for their arguments
        MyConstructor = constructor('x')

        # you can also use `constructor` as a decorator to write initializers /
        # validators, which must return tuples corresponding to the arguments
        @constructor('x', 'y')
        def AnotherConstructor(x, y):
            assert type(x) is str
            assert type(y) is int
            return (x, y)

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

PY3 = sys.version_info[0] == 3

try:
    from itertools import izip_longest
except ImportError:
    from itertools import zip_longest as izip_longest


class _Constructor(object):
    def __init__(self, argspec):
        self._argspec = argspec
        self._func = None

    def __call__(self, func):
        self._func = func
        return self


def constructor(*argspec):
    """
    A wrapper/decorator to indicate that some callable is a constructor for the
    sum type that it's attached to.
    """
    return _Constructor(argspec)


def _cmp_iterators(i1, i2):
    sentinal = object()
    return all(a == b for a, b in izip_longest(i1, i2, fillvalue=sentinal))


def _get_attrs(obj):
    if not obj._sumtype_argspec:
        return ()
    return (getattr(obj, attr) for attr in obj._sumtype_argspec)


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
    def __repr__(inst):
        return "<%s.%s%r>" % (klass.__name__,
                              type(inst).__name__,
                              tuple(_get_attrs(inst)))
    klass.__repr__ = __repr__

    def __eq__(inst, other):
        i1 = _get_attrs(inst)
        i2 = _get_attrs(other)
        return (type(inst) is type(other) and _cmp_iterators(i1, i2))
    klass.__eq__ = __eq__

    def __ne__(inst, other):
        return not inst == other
    klass.__ne__ = __ne__

    constructor_names = []
    for cname, constructor in _get_constructors(klass):
        new_constructor = _make_constructor(cname, klass, constructor._func,
                                            constructor._argspec)
        setattr(klass, cname, new_constructor)
        constructor_names.append(cname)
    klass._sumtype_constructor_names = constructor_names
    return klass


def _make_constructor(name, type_, func, argspec):
    """Create a type specific to the constructor."""
    def init(self, *args):
        if func is not None:
            result = func(*args)
        else:
            result = args

        if argspec is not None:
            for name, value in zip(argspec, result):
                setattr(self, name, value)

    return type(name, (type_,), {'__init__': init,
                                 '_sumtype_argspec': argspec})


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
