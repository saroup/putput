"""This module provides functionality to join combos."""
import itertools
import random
from functools import reduce
from typing import Iterable
from typing import List  # pylint: disable=unused-import
from typing import Optional
from typing import Sequence
from typing import TypeVar

import numpy as np

T = TypeVar('T')

_COMBO = Sequence[Sequence[T]]
_COMBO_PRODUCT = Iterable[Sequence[T]]

class ComboOptions:
    """Options for join_combo via random sampling.

    Attributes:
        max_sample_size: Ceiling for number of components to sample.
        with_replacement: Option to include duplicates when randomly sampling. If True,
            will sample max_sample_size. If False, will sample
            min(max_sample_size, number of unique samples).
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

def join_combo(combo: _COMBO, *, combo_options: Optional[ComboOptions] = None) -> _COMBO_PRODUCT:
    """Generates a joined combo.

    A joined combo is the product, or random sampling of the product, of each component
    of a combo.

    Args:
        combo: Tuples to join.
        combo_options: Options for randomly sampling.

    Yields:
        A joined combo.
    """
    if combo_options:
        return _join_with_sampling(combo, combo_options)
    return _join_without_sampling(combo)

def _join_without_sampling(combo: _COMBO) -> _COMBO_PRODUCT:
    return itertools.product(*combo)

def _join_with_sampling(combo: _COMBO, combo_options: ComboOptions) -> _COMBO_PRODUCT:
    random.seed(combo_options.seed)
    np.random.seed(combo_options.seed)

    component_lengths = tuple(len(item) for item in combo)
    num_possible_unique_samples = reduce(lambda x, y: x * y, component_lengths)
    if combo_options.with_replacement:
        flat_item_indices = tuple(random.randint(0, num_possible_unique_samples - 1)
                                  for _ in range(combo_options.max_sample_size))
    else:
        sample_size = min(combo_options.max_sample_size, num_possible_unique_samples)
        flat_item_indices = tuple(random.sample(range(num_possible_unique_samples), sample_size))

    for flat_item_index in flat_item_indices:
        component_indices = np.unravel_index(flat_item_index, component_lengths)
        combo_components = tuple(combo[component_index][item_index]
                                 for component_index, item_index in enumerate(component_indices))
        yield combo_components
