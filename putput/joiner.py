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
        with_replacement: Option to include duplicates when randomly sampling. If False, sample <=
            max_sample_size components using reservior sampling over the product of each component of the
            joined combo. If True, sample exactly max_sample_size components from the product, allowing
            duplicates. Note: reservior sampling requires iterating through the entire joined combo,
            so it should not be used if the joined combo could be very large. In contrast,
            sampling with replacement does not require iterating through the joined combo,
            so it should be used if the joined combo could be very large.
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
    return _join_with_sampling(combo, combo_options) if combo_options else _join_without_sampling(combo)

def _join_without_sampling(combo: _COMBO) -> _COMBO_PRODUCT:
    return itertools.product(*combo)

def _join_with_sampling(combo: _COMBO, combo_options: ComboOptions) -> _COMBO_PRODUCT:
    random.seed(combo_options.seed)
    np.random.seed(combo_options.seed)
    if combo_options.with_replacement:
        return _join_with_replacement(combo, combo_options.max_sample_size)
    return _join_without_replacement(combo, combo_options.max_sample_size)

def _join_with_replacement(combo: _COMBO, max_sample_size: int) -> _COMBO_PRODUCT:
    for _ in range(max_sample_size):
        component_items = []
        for component in combo:
            component_items.append(random.choice(tuple(component)))
        yield tuple(component_items)

def _join_without_replacement(combo: _COMBO, max_sample_size: int) -> _COMBO_PRODUCT:
    # https://stackoverflow.com/questions/41841354/keeping-track-of-indices-change-in-numpy-reshape
    # combo = ((0, 1, 2, 3), (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21), (0, 1))
    # think of this as sampling from a 1d list, mapping that 1d list back into an
    # array of multi-dimensions, and choosing the item that corresponds to that multi dimension
    component_lengths = [len(item) for item in combo]
    flattened_components_length = reduce(lambda x, y: x * y, component_lengths)
    # TODO: This method could handle random sampling with or without replacement
    sample_size = min(max_sample_size, flattened_components_length)
    item_indices_arr = random.sample(range(flattened_components_length), sample_size)

    for item_indices in item_indices_arr:
        combo_indices = np.unravel_index(item_indices, tuple(component_lengths))
        combo_components = [combo[component_index][item_index]
                            for component_index, item_index in enumerate(combo_indices)]
        yield tuple(combo_components)
