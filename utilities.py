from typing import Callable, Dict, Iterator
from result import Result, as_result, unwraps_or_raises

#################################################################################################
# Iterator
#################################################################################################
@as_result(Exception)
def sequence[S, E](results: Iterator[Result[S, E]]) -> Iterator[S]:
    return (result.unwraps_or_raises for result in results)

def oks[S, E](results: Iterator[Result[S, E]]) -> Iterator[S]:
    return map(unwraps_or_raises, filter(is_ok, results))

def errs[S, E](results: Iterator[Result[S, E]]) -> Iterator[Result[S, E]]:
    return filter(is_ok, results) 

def or_else[S, T, U, E](argument: S, first: Callable[S, Result[T, E]], second: Callable[S, Result[U, E]]) -> Result[T | U, E]:
    return oneOf(argument, (first, second))

@as_result(Exception)
def oneOf[S, T, E](argument: S, functions: Iterator[Callable[S, Result[T, E]]]) -> Result[T, E]:
    results = (f(argument) for f in funtions)
    return next(filter(result.is_ok() for result in results))


#################################################################################################
# Dict
#################################################################################################
@as_result(KeyError)
def dict_get[T, U](dictionary: Dict[T, U], key: T) -> U:
    return dictionary[key]
