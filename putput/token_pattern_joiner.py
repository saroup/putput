import random
from functools import reduce
from typing import List, Set, Tuple

from putput.types import TokenPattern


class TokenPatternJoiner:
    def __init__(self, token_pattern: TokenPattern, max_sample_size: int, max_retries: int, seed: int = 0) -> None:
        if max_sample_size <= 0:
            raise ValueError("max_sample_size must be > 0")
        if max_retries <= 0:
            raise ValueError("max_retries must be > 0")
        self._token_pattern = token_pattern
        self._max_retries = max_retries
        self._sample_size = self._get_sample_size(max_sample_size)
        self._seed = seed
        self.__join_indices: List[Tuple[int, ...]] = []

    @property
    def _join_indices(self) -> List[Tuple[int, ...]]:
        if not self.__join_indices:
            self.__join_indices = self._compute_join_indices()
        return self.__join_indices

    def _get_sample_size(self, max_sample_size: int) -> int:
        words_len = (len(words) for words in self._token_pattern)
        return min(reduce(lambda x, y: x * y, words_len), max_sample_size)

    def _join_token_pattern(self) -> List[str]:
        return [
            ' '.join([words[i] for i, words in zip(indices, self._token_pattern)]) for indices in self._join_indices
        ]

    def _compute_join_indices(self) -> List[Tuple[int, ...]]:
        join_indices: Set[Tuple[int, ...]] = set()
        num_retry = 0
        random.seed(self._seed)
        while (len(join_indices) < self._sample_size) and (num_retry < self._max_retries):
            sampled_indices = tuple(random.choice(range(len(words))) for words in self._token_pattern)
            if sampled_indices not in join_indices:
                join_indices.add(sampled_indices)
                num_retry = 0
            else:
                num_retry += 1
        return list(join_indices)

    def join(self) -> List[str]:
        return self._join_token_pattern()
