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
