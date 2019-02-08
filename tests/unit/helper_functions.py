import unittest
from collections import Counter
from typing import Any
from typing import Iterable
from typing import Sequence
from typing import Tuple
from typing import TypeVar

T = TypeVar('T')

def compare(s: Iterable[T], t: Iterable[T]) -> bool:
    return Counter(s) == Counter(t)

def compare_all_pairs(self: unittest.TestCase, pairs: Sequence[Tuple[Any, Any]]) -> None:
    for actual, expected in pairs:
        self.assertCountEqual(actual, expected)
