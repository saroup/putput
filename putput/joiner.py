"""This module provides functionality to join combos."""
import itertools
import random
import sys
from functools import reduce
from typing import Iterable
from typing import List  # pylint: disable=unused-import
from typing import Optional
from typing import Sequence
from typing import TypeVar

import numpy as np

from putput.logger import get_logger

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
    if not all(combo):
        raise ValueError('Invalid combo: components must not be empty.')
    if combo_options:
        return _join_with_sampling(combo, combo_options)
    return _join_without_sampling(combo)

def _join_without_sampling(combo: _COMBO) -> _COMBO_PRODUCT:
    return itertools.product(*combo)

def _join_with_sampling(combo: _COMBO, combo_options: ComboOptions) -> _COMBO_PRODUCT:
    random.seed(combo_options.seed)
    np.random.seed(combo_options.seed)

    component_lengths = tuple(len(item) for item in combo)
    num_unique_samples = reduce(lambda x, y: x * y, component_lengths)

    if combo_options.with_replacement:
        sample_size = combo_options.max_sample_size
    else:
        sample_size = min(combo_options.max_sample_size, num_unique_samples)

    can_be_sampled = num_unique_samples <= sys.maxsize and _is_valid_to_unravel(component_lengths)
    if can_be_sampled:
        if combo_options.with_replacement:
            flat_item_indices = tuple(random.randint(0, num_unique_samples - 1)
                                      for _ in range(sample_size))
        else:
            flat_item_indices = tuple(random.sample(range(num_unique_samples), sample_size))

        for flat_item_index in flat_item_indices:
            component_indices = np.unravel_index(flat_item_index, component_lengths)
            combo_components = tuple(combo[component_index][item_index]
                                     for component_index, item_index in enumerate(component_indices))
            yield combo_components
    else:
        logger = get_logger(__name__)
        warning_msg = ('Number of possible combinations exceeds sys.maxsize OR np.unravel received invalid dimensions.'
                       ' Defaulting to joining without sampling, capped to the specified sample size.')
        logger.warning(warning_msg)
        for i, c_components in enumerate(_join_without_sampling(combo)):
            if i >= sample_size:
                break
            yield c_components

def _is_valid_to_unravel(dimensions: Sequence[int]) -> bool:
    try:
        np.unravel_index(0, dimensions)
        return True
    except ValueError: # pragma: no cover
        # not covered in unittests because creating components with large lengths takes too long.
        # catches the following issue for certain large numbers: https://github.com/numpy/numpy/issues/9538.
        return False
