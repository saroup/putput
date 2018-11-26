import copy
import itertools
from typing import Any, Callable, Dict, List, Optional, Tuple, no_type_check

from putput.token_pattern_joiner import join_token_pattern
from putput.types import Token, Utterance, UtterancePattern


def create_utterance_and_tokens(utterance_pattern: UtterancePattern,
                                tokens: List[Token],
                                max_sample_size: int,
                                max_retries: int,
                                seed: int = 0,
                                token_handlers: Optional[Dict[str, Callable[[str], str]]] = None
                                ) -> Tuple[Utterance, List[Token]]:
    # pylint: disable=too-many-arguments
    original_combinations = copy.deepcopy(utterance_pattern)
    @no_type_check
    def _combine(combinations):
        if _is_token_pattern(combinations):
            return join_token_pattern(combinations, max_sample_size, max_retries, seed)
        joined_combinations = [_combine(combination) for combination in combinations]
        if combinations == original_combinations:
            token_combinations = [[_get_token_handler(token, token_handlers)(word) for word in words]
                                  for words, token in zip(joined_combinations, tokens)]
            return _combine(joined_combinations), _combine(token_combinations)
        return list(itertools.chain.from_iterable(joined_combinations))
    return _combine(utterance_pattern)


def _is_token_pattern(combinations: Any) -> bool:
    return (isinstance(combinations, list) and isinstance(combinations[0], list)
            and isinstance(combinations[0][0], str))


def _get_token_handler(token: Token,
                       token_handlers: Optional[Dict[str, Callable[[str], str]]] = None) -> Callable[[str], str]:
    if token_handlers:
        token_handler = token_handlers.get(token) or token_handlers.get("DEFAULT")
    return token_handler or (lambda _: "[" + token + "]")
