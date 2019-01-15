"""This module provides functionality to join combinations."""
import itertools
import random
from typing import Iterable, List, Optional, Tuple # pylint: disable=unused-import


class CombinationOptions:
    """Options for joining combinations using reservior sampling.

    See the putput.joiner.join_combination docstring for more information about
    joining combinations.

    Attributes:
        max_sample_size: Ceiling for number of joined combinations to sample.
        seed: initializer for random generator.
    Raises:
        ValueError: If max_sample_size <= 0.
    """
    def __init__(self, *, max_sample_size: int, seed: int) -> None:
        if max_sample_size <= 0:
            raise ValueError("max_sample_size = {}, but needs to be > 0".format(max_sample_size))
        self._max_sample_size = max_sample_size
        self._seed = seed

    @property
    def max_sample_size(self):
        """Read only attribute"""
        return self._max_sample_size

    @property
    def seed(self):
        """Read only attribute"""
        return self._seed

    def __hash__(self):
        """Ensures instances of the class with the same attributes hash to the same value"""
        return hash((self._max_sample_size, self._seed))

def join_combination(combination: Iterable[Iterable[str]],
                     options: Optional[CombinationOptions] = None) -> Iterable[str]:
    """This function generates a joined combination.

    A joined combination is the product, or random sampling of the product, of a each element
    of a combination.

    Args:
        combination: Iterables to join.
        options: Options for randomly sampling joined Iterables using reservior sampling.

    Yields:
        A joined combination.
    """
    return _join_sample_combination(combination, options) if options else _join_all_combination(combination)

def _join_all_combination(combination: Iterable[Iterable[str]]) -> Iterable[str]:
    return (' '.join(product) for product in itertools.product(*combination))

def _join_sample_combination(combination, options: CombinationOptions) -> Iterable[str]:
    return (sample for sample in _reservior_sample(_join_all_combination(combination), options))

def _reservior_sample(joined_combinations: Iterable[str], options: CombinationOptions) -> Tuple[str, ...]:
    # https://stackoverflow.com/questions/2612648/reservoir-sampling
    random.seed(options.seed)
    result = []  # type: List[str]
    N = 0
    for item in joined_combinations:
        N += 1
        if len(result) < options.max_sample_size:
            result.append(item)
        else:
            s = int(random.random() * N)
            if s < options.max_sample_size:
                result[s] = item
    return tuple(result)
