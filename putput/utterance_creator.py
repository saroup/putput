import copy
import itertools
from typing import Callable, Dict, List, Optional, Tuple, Union, no_type_check

from putput.token_creators.token_creator_factory import TokenCreatorFactory
from putput.token_pattern_joiner import TokenPatternJoiner
from putput.types import TokenPattern, Utterance, UtterancePattern, UtterancePatternTokens

_Combinations = Union[UtterancePattern, List[TokenPattern], TokenPattern]


class UtteranceCreator:
    def __init__(self,
                 max_sample_size: int,
                 max_retries: int,
                 seed: int,
                 token_handlers: Optional[Dict[str, Callable[..., str]]] = None) -> None:
        if max_sample_size <= 0:
            raise ValueError("max_sample_size must be > 0")
        if max_retries <= 0:
            raise ValueError("max_retries must be > 0")
        self._max_sample_size = max_sample_size
        self._max_retries = max_retries
        self._seed = seed
        self._token_creator_factory = TokenCreatorFactory(token_handlers)

    def create_utterance_and_tokens(
            self, utterance_pattern: UtterancePattern,
            utterance_pattern_tokens: UtterancePatternTokens) -> Tuple[Utterance, UtterancePatternTokens]:
        original_combinations = copy.deepcopy(utterance_pattern)

        @no_type_check
        def _combine(combinations: _Combinations):
            if self._is_token_pattern(combinations):
                return TokenPatternJoiner(combinations, self._max_retries, self._max_sample_size, self._seed).join()
            joined_combinations = [_combine(combination) for combination in combinations]
            if combinations == original_combinations:
                token_combinations = [[self._token_creator_factory.token_creator(pattern)(word) for word in words]
                                      for words, pattern in zip(joined_combinations, utterance_pattern_tokens)]
                return _combine(joined_combinations), _combine(token_combinations)
            return list(itertools.chain.from_iterable(joined_combinations))

        return _combine(utterance_pattern)

    @staticmethod
    def _is_token_pattern(combinations: _Combinations) -> bool:
        return (isinstance(combinations, list) and isinstance(combinations[0], list)
                and isinstance(combinations[0][0], str))
