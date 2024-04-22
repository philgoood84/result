# Test for the result container
from functools import partial
from result import _Protocol, Result, Ok, Err, as_result, is_err
import operator as op
import pytest
from typing import Dict, Callable



def test_ok() -> None:
    ok = Ok.pure(2)
    assert ok.value == 2

def stringify[T](value: T) -> str:
    return f"{value}"

def test_ok_protocols() -> None:
    two = Ok.pure(2)
    three = Ok.pure(3)
    five = Ok.pure(5)
    ten = Ok.pure(10)
    err = Err.pure(ZeroDivisionError)
    assert not is_err(two)

    ok_string = Ok.pure('2')
    assert ok_string == two.map(stringify)
    with pytest.raises(TypeError):
        instance: Result[int] = two.map(lambda x: x + 'z')


    assert two.apply(Ok.pure(stringify)) == ok_string
    assert is_err(two.apply(Err.pure(stringify)))

    assert two.map2(three, op.add) == five
    assert is_err(two.map2(err, op.add))

    assert two.map3(three, five, lambda x, y, z: x + y + z) == ten
    assert two.map4(three, five, ten, lambda x, y, z, a: x + y + z + a) == Ok.pure(20)

def test_err_protocol() -> None:
    two = Ok.pure(2)
    three = Ok.pure(3)
    five = Ok.pure(5)
    ten = Ok.pure(10)
    err = Err.pure(ZeroDivisionError)


    assert is_err(err)

    assert is_err(err.map(stringify))

    assert is_err(err.apply(Ok.pure(stringify)))
    assert is_err(err.apply(Err.pure(stringify)))

    assert is_err(err.map2(two, op.add))

    assert is_err(two.map3(two, err, lambda x, y, z: x + y + z))
    assert is_err(two.map3(err, two, lambda x, y, z: x + y + z))
    assert is_err(err.map3(two, two, lambda x, y, z: x + y + z))

    assert is_err(err.map4(three, five, ten, lambda x, y, z, a: x + y + z + a))
    assert is_err(two.map4(err, five, ten, lambda x, y, z, a: x + y + z + a))
    assert is_err(two.map4(three, err, ten, lambda x, y, z, a: x + y + z + a))
    assert is_err(two.map4(three, five, err, lambda x, y, z, a: x + y + z + a))


def test_pure_and_join() -> None:
    assert Ok.pure(Ok.pure(2)).join() == Ok.pure(2)
    assert is_err(Ok.pure(Err.pure()).join())
    assert is_err(Err.pure(Ok.pure(2)).join())
    assert is_err(Err.pure(Err.pure(KeyError)).join())

def test_decorator_and_and_then() -> None:
    zero = Ok.pure(0)
    two = Ok.pure(2)
    three = Ok.pure(3)

    @as_result(ZeroDivisionError)
    def _sum_and_divide(first: int, second: int, third: int, fourth: int) -> int:
        return (first + second + third) / fourth

    assert two.and_then(partial(_sum_and_divide, 1, 1, 0)).unwraps_or_raises() == 1
    assert is_err(zero.and_then(partial(_sum_and_divide, 1, 1, 0)))
