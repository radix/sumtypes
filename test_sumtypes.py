"""Tests for sumtypes."""

from pytest import fixture, raises

import attr

from sumtypes import (
    PartialMatchError, constructor, match, match_partial, sumtype)


@sumtype(frozen=True)
class MyType(object):
    MyConstructor = constructor('x')
    AnotherConstructor = constructor('x', 'y')


@sumtype
class AttrsType(object):
    A = constructor(x=attr.ib(validator=attr.validators.instance_of(int)),
                    y=attr.ib(validator=attr.validators.instance_of(str)))


@fixture
def values():
    return (MyType.MyConstructor(3),
            MyType.AnotherConstructor('something', 1))


def test_repr(values):
    """representation shows the type, constructor, and values."""
    v, v2 = values
    assert repr(v) == 'MyType.MyConstructor(x=3)'
    assert repr(v2) == "MyType.AnotherConstructor(x='something', y=1)"


def test_type(values):
    """Type of the values is the constructor, which subclasses the ADT."""
    v, v2 = values
    assert type(v) is MyType.MyConstructor
    assert isinstance(v, MyType)
    assert type(v2) is MyType.AnotherConstructor
    assert isinstance(v2, MyType)


def test_attributes(values):
    """The data can be accessed through attributes named with the argspec."""
    v, v2 = values
    assert v.x == 3
    assert v2.x == 'something'
    assert v2.y == 1


def test_equality(values):
    """Values are equal if both the constructors and values are equal."""
    v, v2 = values
    assert v == MyType.MyConstructor(3)
    assert v != MyType.MyConstructor(2)
    assert not v != MyType.MyConstructor(3)
    assert not v == MyType.MyConstructor(2)
    assert v2 == MyType.AnotherConstructor('something', 1)
    assert v2 != MyType.AnotherConstructor('otherthing', 2)
    assert not v2 != MyType.AnotherConstructor('something', 1)
    assert not v == MyType.AnotherConstructor('othering', 2)


def test_match(values):
    """@match allows writing functions over all the cases of an ADT."""
    v, v2 = values

    @match(MyType)
    class get_value(object):
        def MyConstructor(x):
            return x

        def AnotherConstructor(x, y):
            return y

    assert get_value(v) == 3
    assert get_value(v2) == 1


def test_match_default(values):
    v, v2 = values

    @match(MyType)
    class get_value(object):
        def MyConstructor(x): return x
        def _(value): return value

    assert get_value(v) == 3
    assert get_value(v2) == v2


def test_partial_match_error():
    """
    :obj:`PartialMatchError` is raised if a @match doesn't cover all cases.
    """
    with raises(PartialMatchError):
        @match(MyType)
        class get_partial_value(object):
            def MyConstructor(x):
                return x


def test_match_partial(values):
    """@match_partial allows not covering all the cases."""
    v, v2 = values

    @match_partial(MyType)
    class get_partial_value(object):
        def MyConstructor(x):
            return x

    assert get_partial_value(v) == 3


def test_partial_match_delayed_error(values):
    """
    When @match_partial is applied to an constructor which it doesn't cover,
    :obj:`PartialMatchError` is raised.
    """
    v, v2 = values

    @match_partial(MyType)
    class get_partial_value(object):
        def MyConstructor(x):
            return x

    with raises(PartialMatchError):
        get_partial_value(v2)


def test_nullary_constructor():
    """Constructors don't need to have arguments."""
    @sumtype
    class List(object):
        Nil = constructor()
        Cons = constructor('head', 'tail')

    l = List.Cons(1, List.Nil())
    assert l == List.Cons(1, List.Nil())


def test_no_conversion_constructors():
    """Constructors don't need to have conversion functions supplied."""
    @sumtype
    class List(object):
        Nil = constructor()
        Cons = constructor('head', 'tail')

    l = List.Cons(1, List.Nil())
    assert l == List.Cons(1, List.Nil())


def test_hash():
    """Values are hashed based on their values, not identity."""
    assert {MyType.MyConstructor(1): 2}[MyType.MyConstructor(1)] == 2


def test_hash_counts_constructor():
    """
    Different values of the same type but same underlying representation do not
    count as equivalent in dicts.
    """
    @sumtype(frozen=True)
    class T(object):
        Nil = constructor()
        Nil2 = constructor()

    assert T.Nil2() not in {T.Nil(): 'foo'}


def test_attrs():
    a = AttrsType.A(x=1, y='foo')
    assert a.x == 1
    assert a.y == 'foo'


def test_attrs_positional():
    a = AttrsType.A(1, 'foo')
    assert a == AttrsType.A(x=1, y='foo')
