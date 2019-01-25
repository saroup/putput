"""This module provides functionality to generate utterances and tokens after processing the pattern definition."""
import itertools
from functools import wraps
from typing import Any, Callable, Dict, List, Iterable, Mapping, Optional, Tuple # pylint: disable=unused-import

from putput.joiner import CombinationOptions, join_combination
from putput.pattern_definition_processor import UtterancePattern


def generate_utterances_and_tokens(utterance_pattern: UtterancePattern,
                                   tokens: Tuple[str, ...],
                                   token_handlers: Optional[Mapping[str, Callable[[str, str], str]]] = None,
                                   combination_options: Optional[CombinationOptions] = None
                                   ) -> Iterable[Tuple[str, str]]:
    """This function generates utterance-token pairs.

    Args:
        utterance_pattern: TokenPatterns for each token defined under 'utterance_patterns'
            in the pattern definition file. One output of the function
            putput.pattern_definition_processor.generate_utterance_pattern_and_tokens.
        tokens: Tokens that describe the utterance_pattern, as defined by
            each list under 'utterance_patterns' in the pattern definition file.
            One output of the function putput.pattern_definition_processor.generate_utterance_pattern_and_tokens.
        token_handlers: A mapping of token -> token handler function. The token handler function's parameters
            are (token, tokenized_phrase). A token handler function determines how its corresponding
            token should be tokenized. By default, a token is tokenized to '[TOKEN]'. To change
            the default behavior for every token, specify a mapping of 'DEFAULT' -> token handler function.
        combination_options: Options for randomly sampling utterance-token pairs. Useful for limiting the
            output number of utterance-token pairs and speeding up the consumption time of the
            generator.

    Yields:
        utterance-token pairs.
    """
    utterance_combination = _compute_utterance_combination(utterance_pattern)
    token_combination = _compute_token_combination(utterance_combination, tokens, token_handlers)

    utterances = join_combination(utterance_combination, combination_options)
    tokens_iterable = join_combination(token_combination, combination_options)
    return ((utterance, tokens) for utterance, tokens in zip(utterances, tokens_iterable))

def _compute_utterance_combination(utterance_pattern: UtterancePattern,
                                   combination_options: Optional[CombinationOptions] = None
                                   ) -> Tuple[Tuple[str, ...], ...]:
    return tuple(
        tuple(itertools.chain.from_iterable(_join_token_pattern(token_pattern, combination_options)
                                            for token_pattern in token_patterns))
        for token_patterns in utterance_pattern
    )

def _memoize(function: Callable) -> Callable:
    # https://stackoverflow.com/questions/815110/is-there-a-decorator-to-simply-cache-function-return-values
    memo = {}  # type: Dict[List[Any], Callable]
    @wraps(function)
    def wrapper(*args):
        if args in memo:
            return memo[args]
        rv = function(*args)
        memo[args] = rv
        return rv
    return wrapper

@_memoize
def _join_token_pattern(token_pattern: Tuple[Tuple[str, ...], ...],
                        combination_options: Optional[CombinationOptions]) -> Tuple[str, ...]:
    return tuple(join_combination(token_pattern, combination_options))

def _compute_token_combination(utterance_combinations: Tuple[Tuple[str, ...], ...],
                               tokens: Iterable[str],
                               token_handlers: Optional[Mapping[str, Callable[[str, str], str]]] = None
                               ) -> Tuple[Tuple[str, ...], ...]:
    return tuple(tuple(_get_token_handler(token, token_handlers)(token, word) for word in words)
                 for words, token in zip(utterance_combinations, tokens))

def _get_token_handler(token: str,
                       token_handlers: Optional[Mapping[str, Callable[[str, str], str]]] = None
                       ) -> Callable[[str, str], str]:
    default_token_handler = lambda token, _: '[' + token + ']'
    if token_handlers:
        return token_handlers.get(token) or token_handlers.get('DEFAULT') or default_token_handler
    return default_token_handler
