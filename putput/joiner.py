"""This module provides functionality to join combinations."""
import itertools
import random
from typing import List # pylint: disable=unused-import
from typing import Optional
from typing import TypeVar

from putput.types import COMBINATION
from putput.types import COMBINATION_PRODUCT
from putput.types import COMPONENT # pylint: disable=unused-import

T = TypeVar('T')


class CombinationOptions:
    """Options for join_combination via random sampling.

    Attributes:
        max_sample_size: Ceiling for number of components to sample.
        with_replacement: Option to include duplicates when randomly sampling. If False, sample <=
            max_sample_size components using reservior sampling over the product of each component of the
            joined combination. If True, sample exactly max_sample_size components from the product, allowing
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

def join_combination(combination: COMBINATION,
                     options: Optional[CombinationOptions] = None) -> COMBINATION_PRODUCT:
    """Generates a joined combination.

    A joined combination is the product, or random sampling of the product, of each component
    of a combination.

    Args:
        combination: Tuples to join.
        options: Options for randomly sampling.

    Yields:
        A joined combination.
    """
    return _join_with_sampling(combination, options) if options else _join_without_sampling(combination)

def _join_without_sampling(combination: COMBINATION) -> COMBINATION_PRODUCT:
    return itertools.product(*combination)

def _join_with_sampling(combination: COMBINATION,
                        options: CombinationOptions) -> COMBINATION_PRODUCT:
    random.seed(options.seed)
    if options.with_replacement:
        return _join_with_replacement(combination, options.max_sample_size)
    return _join_without_replacement(combination, options.max_sample_size)

def _join_with_replacement(combination: COMBINATION, max_sample_size: int) -> COMBINATION_PRODUCT:
    for _ in range(max_sample_size):
        component_items = []
        for component in combination:
            component_items.append(random.choice(tuple(component)))
        yield tuple(component_items)

def _join_without_replacement(combination: COMBINATION,
                              max_sample_size: int) -> COMBINATION_PRODUCT:
    # https://stackoverflow.com/questions/2612648/reservoir-sampling
    joined_combination = _join_without_sampling(combination)
    result = [] # type: List[COMPONENT]
    N = 0
    for item in joined_combination:
        N += 1
        if len(result) < max_sample_size:
            result.append(item)
        else:
            s = int(random.random() * N)
            if s < max_sample_size:
                result[s] = item
    return (i for i in result)
