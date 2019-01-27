"""This module provides functionality to join combinations."""
import itertools
import random
from typing import Iterable, List, Optional, Tuple, TypeVar # pylint: disable=unused-import

T = TypeVar('T')


class CombinationOptions:
    """Options for join_combination via random sampling.

    Attributes:
        max_sample_size: Ceiling for number of elements to sample.
        with_replacement: Option to include duplicates when randomly sampling. If False, sample <=
            max_sample_size elements using reservior sampling over the product of each element of the
            joined combination. If True, sample exactly max_sample_size elements from the product, allowing
            duplicates. Note: reservior sampling requires iterating through the entire joined combination,
            so it should not be used if the joined combination could be very large. In contrast,
            sampling with replacement does not require iterating through the joined combination,
            so it should be used if the joined combination could be very large.
        seed: initializer for random generator.
    Raises:
        ValueError: If max_sample_size <= 0.
    """
    def __init__(self, *, max_sample_size: int, with_replacement: bool, seed: int) -> None:
        if max_sample_size <= 0:
            raise ValueError('max_sample_size = {}, but needs to be > 0'.format(max_sample_size))
        self._max_sample_size = max_sample_size
        self._with_replacement = with_replacement
        self._seed = seed

    @property
    def max_sample_size(self):
        """Read only attribute."""
        return self._max_sample_size

    @property
    def with_replacement(self):
        """Read only attribute."""
        return self._with_replacement

    @property
    def seed(self):
        """Read only attribute."""
        return self._seed

    def __hash__(self):
        """Ensures instances of the class with the same attributes hash to the same value."""
        return hash((self._max_sample_size, self._with_replacement, self._seed))

def join_combination(combination: Tuple[Tuple[T, ...], ...],
                     options: Optional[CombinationOptions] = None) -> Iterable[Tuple[T, ...]]:
    """Generates a joined combination.

    A joined combination is the product, or random sampling of the product, of each element
    of a combination.

    Args:
        combination: Tuples to join.
        options: Options for randomly sampling.

    Yields:
        A joined combination.
    """
    return _join_with_sampling(combination, options) if options else _join_without_sampling(combination)

def _join_without_sampling(combination: Tuple[Tuple[T, ...], ...]) -> Iterable[Tuple[T, ...]]:
    return itertools.product(*combination)

def _join_with_sampling(combination: Tuple[Tuple[T, ...], ...],
                        options: CombinationOptions) -> Iterable[Tuple[T, ...]]:
    random.seed(options.seed)
    if options.with_replacement:
        return _join_with_replacement(combination, options.max_sample_size)
    return _join_without_replacement(combination, options.max_sample_size)

def _join_with_replacement(combination: Tuple[Tuple[T, ...], ...], max_sample_size: int) -> Iterable[Tuple[T, ...]]:
    for _ in range(max_sample_size):
        component_items = []
        for component in combination:
            component_items.append(random.choice(tuple(component)))
        yield tuple(component_items)

def _join_without_replacement(combination: Tuple[Tuple[T, ...], ...],
                              max_sample_size: int) -> Tuple[Tuple[T, ...], ...]:
    # https://stackoverflow.com/questions/2612648/reservoir-sampling
    joined_combination = _join_without_sampling(combination)
    result = [] # type: List[Tuple[T, ...]]
    N = 0
    for item in joined_combination:
        N += 1
        if len(result) < max_sample_size:
            result.append(item)
        else:
            s = int(random.random() * N)
            if s < max_sample_size:
                result[s] = item
    return tuple(result)
