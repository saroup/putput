import random
from functools import reduce
from typing import List, Set, Tuple

from putput.types import TokenPattern


def _get_sample_size(token_pattern: TokenPattern, max_sample_size: int) -> int:
    words_len = (len(words) for words in token_pattern)
    return min(reduce(lambda x, y: x * y, words_len), max_sample_size)


def _compute_join_indices(token_pattern: TokenPattern,
                          max_sample_size: int,
                          max_retries: int,
                          seed: int) -> List[Tuple[int, ...]]:
    join_indices: Set[Tuple[int, ...]] = set()
    num_retry = 0
    sample_size = _get_sample_size(token_pattern, max_sample_size)
    random.seed(seed)
    while (len(join_indices) < sample_size) and (num_retry < max_retries):
        sampled_indices = tuple(random.choice(range(len(words))) for words in token_pattern)
        if sampled_indices not in join_indices:
            join_indices.add(sampled_indices)
            num_retry = 0
        else:
            num_retry += 1
    return list(join_indices)


def join_token_pattern(token_pattern: TokenPattern, max_sample_size: int, max_retries: int, seed: int) -> List[str]:
    if max_sample_size <= 0:
        raise ValueError("max_sample_size must be > 0")
    if max_retries <= 0:
        raise ValueError("max_retries must be > 0")
    return [
        ' '.join([words[i] for i, words in zip(indices, token_pattern)])
        for indices in _compute_join_indices(token_pattern, max_sample_size, max_retries, seed)
    ]
