from dataclasses import dataclass
from functools import partial, wraps
from typing import Callable, Protocol
import inspect

type Result[S, E] = Ok[S] | Err[E]

class _Protocol[T](Protocol):
    value: T
    @classmethod
    def pure[T, E](cls, value: T) -> Result[T, E]:
        ...

    def map[T, S, E](self, f: Callable[T, S]) -> Result[S, E]:
        ...

    def apply[T, S, E](self, rf: Result[Callable[T, S], E]) -> Result[S, E]:
        ...

    def map2[T, S, U, E](self, s: Result[S, E], f: Callable[[T, S], U]) -> Result[U, E]:
        return s.apply(self.map(lambda t: partial(f, t)))

    def map3[T, S, U, V, E](self, s: Result[S, E], u: Result[U, E], f: Callable[[T, S, U], V]) -> Result[V, E]:
        return u.apply(self.map2(s, lambda ts, ss: partial(f, ts, ss)))

    def map4[T, S, U, V, W, E](self, s: Result[S, E], u: Result[U, E], v: Result[V, E], f: Callable[[T, S, U, V], W]) -> Result[W, E]:
        return v.apply(self.map3(s, u, lambda ts, ss, us: partial(f, ts, ss, us)))

    def and_then[T, S, E](self, f: Callable[T, Result[S, E]]) -> Result[S, E]:
        ...
    
    def join[T, E](self) -> Result[T, E]:
        ...

    def and_then2[T, S, U, E](self, s: Result[S, E], f: Callable[[T, S], Result[U, E]]) -> Result[U, E]:
        return self.map2(s, f).join()

    def and_then3[T, S, U, V, E](self, s: Result[S, E], u: Result[U, E], f: Callable[[T, S, U], Result[V, E]]) -> Result[V, E]:
        return self.map3(s, u, f).join()

    def and_then4[T, S, U, V, W, E](self, s: Result[S, E], u: Result[U, E], v: Result[V, E], f: Callable[[T, S, U, V], Result[W, E]]) -> Result[W, E]:
        return self.map4(s, u, v, f).join()

    def m_compose[T, S, U, E](self, f1: Callable[T, Result[S, E]], f2: Callable[S, Result[U, E]]) -> Result[U, E]:
        return self.and_then(f1).and_then(f2)

    def unwraps_or_raises[T](self) -> T:
        ...


@dataclass(frozen = True)
class Ok[Success](_Protocol):
    __slots__ = ('value',)
    value: Success

    @classmethod
    def pure[Success, E](cls, value: Success) -> Result[Success, E]:
        return Ok(value= value)

    def map[Success, T, E](self, f: Callable[Success, T]) -> Result[T, E]:
        return Ok.pure(f(self.value))

    def apply[Success, T, E](self, rf: Result[Callable[Success, T], E]) -> Result[T, E]:
        match rf:
            case Ok(value= f):
                return self.map(f)
            case Err():
                return rf

    def and_then[Success, T, E](self, f: Callable[Success, Result[T, E]]) -> Result[T, E]:
        return f(self.value)

    def join[Success, E](self) -> Result[Success, E]:
        match self.value:
            case Ok() | Err():
                return self.value.join()
            case _:
                return self

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    def unwraps_or_raises[T](self) -> T:
        return self.value



@dataclass(frozen = True)
class Err[Error: Exception](_Protocol):
    __slots__ = ('value',)
    value: Error

    @classmethod
    def pure[S, Error](cls, value: Error = Exception) -> Result[S, Error]:
        return Err(value= value)

    def map[Error, T, E](self, f: Callable[..., T]) -> Result[T, E]:
        return self

    def apply[T, S, E](self, rf: Result[Callable[T, S], E]) -> Result[S, E]:
        return self

    def and_then[T, Error, E](self, f: Callable[..., Result[T, E]]) -> Result[T, Error]:
        return self

    def join[T, Error](self) -> Result[T, Error]:
        match self.value:
            case Err():
                return self.value.join()
            case _:
                return self

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def unwraps_or_raises[T](self) -> T:
        raise self.value


def as_result[**P, R, E: Exception](*exceptions: E) -> Callable[[Callable[P, R]], Callable[P, Result[R, E]]]:
    """
    Copied from python/result
    Make a decorator to turn a function into one that returns a ``Result``.

    Regular return values are turned into ``Ok(return_value)``. Raised
    exceptions of the specified exception type(s) are turned into ``Err(exc)``.
    """
    if not exceptions or not all(
        inspect.isclass(exception) and issubclass(exception, BaseException)
        for exception in exceptions
    ):
        raise TypeError("as_result() requires one or more exception types")

    def decorator(f: Callable[P, R]) -> Callable[P, Result[R, E]]:
        """
        Decorator to turn a function into one that returns a ``Result``.
        """

        @wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[R, E]:
            try:
                return Ok(f(*args, **kwargs)).join()
            except exceptions as exc:
                return Err(exc).join()

        return wrapper

    return decorator

"""
Non object like functions
"""
def is_ok[S, E](result: Result[S, E]) -> bool:
    return result.is_ok()

def is_err[S, E](result: Result[S, E]) -> bool:
    return (result.is_ok() == False)

def unwraps_or_raises[S, E](result: Result[S, E]) -> S:
    return result.unwraps_or_raises()

