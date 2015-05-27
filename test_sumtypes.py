"""Tests for sumtypes."""

from pytest import fixture

from sumtypes import sumtype, constructor


@sumtype
class MyType(object):
    MyConstructor = constructor(int)

    @constructor
    def AnotherConstructor(x, y):
        assert type(x) is str
        assert type(y) is int
        return (x, y)


@fixture
def values():
    return (MyType.MyConstructor(3),
            MyType.AnotherConstructor('something', 1))


def test_repr(values):
    v, v2 = values
    assert repr(v) == '<MyType.MyConstructor 3>'
    assert repr(v2) == "<MyType.AnotherConstructor ('something', 1)>"


def test_type(values):
    v, v2 = values
    assert type(v) is MyType
    assert type(v2) is MyType


def test_value(values):
    v, v2 = values
    assert v.value == 3
    assert v2.value == ('something', 1)


def test_constructor(values):
    v, v2 = values
    assert v.constructor is MyType.MyConstructor
    assert v2.constructor is MyType.AnotherConstructor


def test_equality(values):
    v, v2 = values
    assert v == MyType.MyConstructor(3)
    assert v != MyType.MyConstructor(2)
    assert not v != MyType.MyConstructor(3)
    assert not v == MyType.MyConstructor(2)
    assert v2 == MyType.AnotherConstructor('something', 1)
    assert v2 != MyType.AnotherConstructor('otherthing', 2)
    assert not v2 != MyType.AnotherConstructor('something', 1)
    assert not v == MyType.AnotherConstructor('othering', 2)
