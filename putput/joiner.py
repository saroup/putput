"""This module provides functionality to join combinations."""
import itertools
import random
from typing import Iterable, List, Optional, Tuple # pylint: disable=unused-import


class CombinationOptions:
    """Options for join_combination via random sampling.

    Attributes:
        max_sample_size: Ceiling for number of elements to sample.
        with_replacement: Option to include duplicates when randomly sampling. If False, sample <=
            max_sample_size elements using reservior sampling over the product of each element of the
            joined combination. If True, sample exactly max_sample_size elements from the product and speed up the
            consumption time of the generator returned by join_combination, making time proportional to
            max_sample_size.
        seed: initializer for random generator.
    Raises:
        ValueError: If max_sample_size <= 0.
    """
    def __init__(self, *, max_sample_size: int, with_replacement: bool, seed: int) -> None:
        if max_sample_size <= 0:
            raise ValueError("max_sample_size = {}, but needs to be > 0".format(max_sample_size))
        self._max_sample_size = max_sample_size
        self._with_replacement = with_replacement
        self._seed = seed

    @property
    def max_sample_size(self):
        """Read only attribute"""
        return self._max_sample_size

    @property
    def with_replacement(self):
        """Read only attribute"""
        return self._with_replacement

    @property
    def seed(self):
        """Read only attribute"""
        return self._seed

    def __hash__(self):
        """Ensures instances of the class with the same attributes hash to the same value"""
        return hash((self._max_sample_size, self._with_replacement, self._seed))

def join_combination(combination: Iterable[Iterable[str]],
                     options: Optional[CombinationOptions] = None) -> Iterable[str]:
    """This function generates a joined combination.

    A joined combination is the product, or random sampling of the product, of a each element
    of a combination.

    Args:
        combination: Iterables to join.
        options: Options for randomly sampling.

    Yields:
        A joined combination.
    """
    return _join_sample_combination(combination, options) if options else _join_all_combination(combination)

def _join_all_combination(combination: Iterable[Iterable[str]]) -> Iterable[str]:
    return (' '.join(product) for product in itertools.product(*combination))

def _join_sample_combination(combination: Iterable[Iterable[str]], options: CombinationOptions) -> Iterable[str]:
    random.seed(options.seed)
    if options.with_replacement:
        return _sample_with_replacement(combination, options.max_sample_size)
    return _sample_without_replacement(combination, options.max_sample_size)

def _sample_with_replacement(combination: Iterable[Iterable[str]], max_sample_size: int) -> Iterable[str]:
    return (' '.join(random.choice(tuple(component)) for component in combination) for i in range(max_sample_size))

def _sample_without_replacement(combination: Iterable[Iterable[str]], max_sample_size: int) -> Iterable[str]:
    # https://stackoverflow.com/questions/2612648/reservoir-sampling
    joined_combination = _join_all_combination(combination)
    result = []  # type: List[str]
    N = 0
    for item in joined_combination:
        N += 1
        if len(result) < max_sample_size:
            result.append(item)
        else:
            s = int(random.random() * N)
            if s < max_sample_size:
                result[s] = item
    return (sample for sample in result)
