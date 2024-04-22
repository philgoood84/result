import utilities
import result


def test_iterators() -> None:
    pass


def test_dict() -> None:
    dict_test: Dict[str, int] = {'a': 12, 'b': 15}
    assert utilities.dict_get(dict_test, 'a').unwraps_or_raises() == 12
    assert result.is_err(utilities.dict_get(dict_test, 'c'))
    another_dict: Dict[int, str] = {12: 'a', 15: 'b'} 
