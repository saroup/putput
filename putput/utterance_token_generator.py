"""This module provides functionality to generate utterances and tokens after processing the pattern definition."""
import itertools
from functools import wraps
from typing import Any, Callable, Iterable, List, Mapping, Optional, Tuple # pylint: disable=unused-import

from putput.joiner import CombinationOptions, join_combination
from putput.pattern_definition_processor import UtterancePattern


def generate_utterances_and_tokens(utterance_pattern: UtterancePattern,
                                   utterance_pattern_tokens: Tuple[str, ...],
                                   token_handlers: Optional[Mapping[str, Callable[[str, str], str]]] = None,
                                   combination_options: Optional[CombinationOptions] = None
                                   ) -> Iterable[Tuple[str, str]]:
    """This function generates utterance-token pairs.

    Args:
        utterance_pattern: TokenPatterns for each token defined under 'utterance_patterns'
            in the pattern definition file. One output of the function
            putput.pattern_definition_processor.generate_utterance_pattern_and_tokens.
        utterance_pattern_tokens: Tokens that describe the utterance_pattern, as defined by
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
    token_combination = _compute_token_combination(utterance_combination, utterance_pattern_tokens, token_handlers)

    combination_indices = tuple(tuple(i for i in range(len(component))) for component in utterance_combination)
    for indices in join_combination(combination_indices, combination_options):
        utterance = []
        tokens = []
        for utterance_component, token_component, index in zip(utterance_combination, token_combination, indices):
            utterance.append(utterance_component[index])
            tokens.append(token_component[index])
        yield ' '.join(utterance), ' '.join(tokens)

def _compute_utterance_combination(utterance_pattern: UtterancePattern) -> Tuple[Tuple[str, ...], ...]:
    utterance_combination = []
    for token_patterns in utterance_pattern:
        utterance_components = []
        for token_pattern in token_patterns:
            utterance_component = _join_token_pattern(token_pattern)
            utterance_components.append(utterance_component)
        chained_utterance_components = tuple(itertools.chain.from_iterable(utterance_components))
        utterance_combination.append(chained_utterance_components)
    return tuple(utterance_combination)

def _compute_token_combination(utterance_combination: Tuple[Tuple[str, ...], ...],
                               tokens: Iterable[str],
                               token_handlers: Optional[Mapping[str, Callable[[str, str], str]]] = None
                               ) -> Tuple[Tuple[str, ...], ...]:
    token_combination = []
    for token_phrases, token in zip(utterance_combination, tokens):
        token_components = []
        for token_phrase in token_phrases:
            token_handler = _get_token_handler(token, token_handlers)
            token_component = token_handler(token, token_phrase)
            token_components.append(token_component)
        token_combination.append(tuple(token_components))
    return tuple(token_combination)

def _get_token_handler(token: str,
                       token_handlers: Optional[Mapping[str, Callable[[str, str], str]]] = None
                       ) -> Callable[[str, str], str]:
    default_token_handler = lambda token, _: '[' + token + ']'
    if token_handlers:
        return token_handlers.get(token) or token_handlers.get('DEFAULT') or default_token_handler
    return default_token_handler

def _memoize(function: Callable) -> Callable:
    # https://stackoverflow.com/questions/815110/is-there-a-decorator-to-simply-cache-function-return-values
    memo = {}  # type: Mapping[List[Any], Callable]
    @wraps(function)
    def wrapper(*args):
        if args in memo:
            return memo[args]
        rv = function(*args)
        memo[args] = rv
        return rv
    return wrapper

@_memoize
def _join_token_pattern(token_pattern: Tuple[Tuple[str, ...], ...]) -> Tuple[str, ...]:
    joined_token_pattern = []
    for token_pattern_component in join_combination(token_pattern):
        joined_token_pattern.append(' '.join(token_pattern_component))
    return tuple(joined_token_pattern)
