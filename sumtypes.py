"""
Sum Types (aka Tagged Unions) for Python.

Decorate your classes to make them a sum type::

    @sumtype
    class MyType(object):

        MyConstructor = constructor(int)

        @constructor
        def AnotherConstructor(x, y):
            assert type(x) is str
            assert type(y) is int
            return (x, y)

Then construct them by calling the constructors::

    v = MyType.MyConstructor(1)
    v2 = MyType.AnotherConstructor('foo', 2)

You can get the value from the tagged objects::

    assert v.value == 1
    assert v2.value == ('foo', 2)

The type of the tagged objects is the type you declared::

    assert type(v) is MyType

You can also introspect the constructor used::

    assert v.constructor is MyType.MyConstructor

And the tagged objects have equality semantics, which you can use to do pattern
matching::

    assert v == MyType.MyConstructor(1)
    assert v != MyType.MyConstructor(2)
"""


class constructor(object):
    """
    A wrapper/decorator to indicate that some callable is a constructor for the
    sum type that it's attached to.
    """
    def __init__(self, callable_):
        self.callable_ = callable_

    def set_klass(self, klass):
        self.klass = klass

    def set_name(self, name):
        self.name = name

    def __call__(self, *args, **kwargs):
        obj = object.__new__(self.klass)
        obj.value = self.callable_(*args, **kwargs)
        obj.constructor = self
        return obj


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
        return "<%s.%s %r>" % (klass.__name__,
                               inst.constructor.name,
                               inst.value)
    klass.__repr__ = __repr__

    def __eq__(inst, other):
        return (inst.constructor is other.constructor
                and inst.value == other.value)
    klass.__eq__ = __eq__

    def __ne__(inst, other):
        return not inst == other
    klass.__ne__ = __ne__

    for k, v in vars(klass).items():
        if type(v) is constructor:
            v.set_klass(klass)
            v.set_name(k)
    return klass
