"""
Decorate your classes to make them a sum type::

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
.. _`attr.ib documentation`:
   http://attrs.readthedocs.org/en/stable/api.html#attr.ib

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

    @match(MyType)
    class get_number(object):
        def MyConstructor(x): return x
        def AnotherConstructor(x, y): return y
        def ThirdConstructor(one, two): return one + two

    assert get_number(v) == 1
    assert get_number(v2) == 2

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


def constructor(*attrnames, **attribs):
    """
    Register a constructor for the parent sum type.

    Note that ``*attrnames`` and ``**attribs`` are mutually exclusive.

    :param attrnames: each argument should be either a simple string indicating
        the name of an attribute
    :param attribs: variables specified with `attr.ib`_ instances, from the
        `attrs package`_.

    .. _`attr.ib`:
       http://attrs.readthedocs.org/en/stable/api.html#attr.ib
    """
    if attribs and attrnames:
        raise TypeError(
            "Can't mix positional and keyword arguments in constructors")
    if attribs:
        attrs = sorted(list(attribs.items()), key=lambda item: item[1].counter)
    else:
        attrs = [(name, attr.ib()) for name in attrnames]
    return _Constructor(attrs)


def _cmp_iterators(i1, i2):
    sentinal = object()
    return all(a == b for a, b in izip_longest(i1, i2, fillvalue=sentinal))


def _get_attrs(obj):
    return (getattr(obj, attr[0]) for attr in obj._sumtype_attribs)


def _get_constructors(klass):
    for k, v in list(vars(klass).items()):
        if type(v) is _Constructor:
            yield k, v


def sumtype(*args, **kwargs):
    """
    A class decorator that treats the class like a sum type.

    Constructors should be wrapped/decorated with :obj:`constructor`.

    Note that this will overwrite ``__repr__``, ``__eq__``, and ``__ne__`` on
    your objects. ``__init__`` is untouched, but it would be kind of weird to
    make something a sum type *and* have an ``__init__``, so I recommend
    against that.
    """
    if len(args) == 1 and len(kwargs) == 0 and type(args[0] is type):
        return _real_decorator(args[0], {})
    else:
        return lambda klass: _real_decorator(klass, kwargs)


def _real_decorator(klass, kwargs):
    constructor_names = []
    for cname, constructor in _get_constructors(klass):
        new_constructor = _make_constructor(
            cname, klass, constructor._attrs, kwargs
        )
        setattr(klass, cname, new_constructor)
        constructor_names.append(cname)
    klass._sumtype_constructor_names = constructor_names
    return klass


def _make_constructor(name, type_, attrs, kwargs):
    """Create a type specific to the constructor."""
    d = dict(attrs)
    d['_sumtype_attribs'] = [x for x in attrs]
    t = type(name, (type_,), d)
    t = attr.s(t, repr_ns=type_.__name__, **kwargs)
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
            def NamedNum(_, num): return num
            def AnonymousNum(num): return num

        assert get_num(MyType.NamedNum('foo', 1)) == 1
        assert get_num(MyType.AnonymousNum(2)) == 2

    If not all constructors are handled, :obj:`PartialMatchError` will be
    raised. However, a default case can be implemented by defining a method
    named ``_``, and it will be passed the value::

        @match(MyType)
        class get_name(object):
            def NamedNum(name, _): return name
            def _(_): return 'default'
    """
    def matchit(klass):
        klass_attrs = set(dir(klass))
        constructor_names = set(adt._sumtype_constructor_names)
        unhandled = constructor_names - klass_attrs
        if unhandled and '_' not in klass_attrs:
            raise PartialMatchError(unhandled)
        return _matchit(klass)
    return matchit


def _matchit(klass):
    def run(value):
        constructor_type = type(value)
        args = _get_attrs(value)
        cname = constructor_type.__name__
        handler = getattr(klass, cname, None)
        if handler is None:
            handler = getattr(klass, '_', None)
            if handler is None:
                raise PartialMatchError([cname])
            else:
                args = [value]
        if PY3:
            case = handler
        else:
            case = handler.im_func
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
