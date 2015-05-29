"""Tests for sumtypes."""

from pytest import fixture, raises

from sumtypes import (
    PartialMatchError, constructor, match, match_partial, sumtype)


@sumtype
class MyType(object):
    MyConstructor = constructor('x')

    @constructor('x', 'y')
    def AnotherConstructor(x, y):
        assert type(x) is str
        assert type(y) is int
        return (x, y)


@fixture
def values():
    return (MyType.MyConstructor(3),
            MyType.AnotherConstructor('something', 1))


def test_repr(values):
    """representation shows the type, constructor, and values."""
    v, v2 = values
    assert repr(v) == '<MyType.MyConstructor(3,)>'
    assert repr(v2) == "<MyType.AnotherConstructor('something', 1)>"


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


def test_arity_mismatch():
    """
    Constructor functions must return a tuple with the same number of elements
    as the argument spec.
    """
    @sumtype
    class BadType(object):
        @constructor('x', 'y')
        def BadConstructor(x, y):
            return x

    with raises(TypeError):
        BadType.BadConstructor(1, 2)


def test_nullary_constructor():
    """Constructors don't need to have arguments."""
    @sumtype
    class List(object):
        Nil = constructor()

        @constructor('head', 'tail')
        def Cons(head, tail):
            return (head, tail)

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
