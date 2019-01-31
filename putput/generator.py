"""This module provides functionality to generate utterances and tokens after processing the pattern definition."""
import itertools
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Tuple # pylint: disable=unused-import

import yaml

from putput.joiner import CombinationOptions, join_combination
from putput.validator import validate_pattern_definition


def process_pattern_definition(pattern_definition_path: Path,
                               dynamic_token_to_token_patterns: Optional[Mapping[str, Tuple[Tuple[Tuple[str, ...], ...], ...]]] = None
                               ) -> Iterable[Tuple[Tuple[Tuple[str, ...], ...], Tuple[str, ...]]]:
    pattern_definition = _load_pattern_definition(pattern_definition_path)
    validate_pattern_definition(pattern_definition)
    token_to_token_patterns = _get_token_to_token_patterns(pattern_definition, dynamic_token_to_token_patterns)

    for tokens in pattern_definition['utterance_patterns']:
        token_patterns = []
        for token in tokens:
            token_patterns.append(token_to_token_patterns[token])
        utterance_pattern = tuple(token_patterns)
        utterance_combination = _compute_utterance_combination(utterance_pattern)
        yield utterance_combination, tuple(tokens)

def generate_utterances_and_handled_tokens(utterance_combination: Tuple[Tuple[str, ...], ...],
                                           tokens: Tuple[str, ...],
                                           token_to_token_handlers: Optional[Mapping[str, Callable[[str, str], str]]] = None,
                                           combination_options: Optional[CombinationOptions] = None
                                           ) -> Iterable[Tuple[str, str]]:
    handled_token_combination = _compute_handled_token_combination(utterance_combination,
                                                                   tokens,
                                                                   token_to_token_handlers)
    combination_indices = tuple(tuple(i for i in range(len(component))) for component in utterance_combination)
    for indices in join_combination(combination_indices, combination_options):
        utterance = []
        handled_tokens = []
        for utterance_component, token_component, index in zip(utterance_combination,
                                                               handled_token_combination,
                                                               indices):
            utterance.append(utterance_component[index])
            handled_tokens.append(token_component[index])
        yield ' '.join(utterance), ' '.join(handled_tokens)

def _load_pattern_definition(pattern_definition_path: Path) -> Mapping:
    with pattern_definition_path.open(encoding='utf-8') as pattern_definition_file:
        pattern_definition = yaml.load(pattern_definition_file)
    return pattern_definition

def _get_token_to_token_patterns(pattern_definition: Mapping,
                                 dynamic_token_to_token_patterns: Optional[Mapping[str, Tuple[Tuple[Tuple[str, ...], ...], ...]]] = None
                                 ) -> Mapping[str, Tuple[Tuple[Tuple[str, ...], ...], ...]]:
    static_token_to_token_patterns = _get_static_token_to_token_patterns(pattern_definition)
    token_to_token_patterns = dict(static_token_to_token_patterns)
    token_to_token_patterns.update(dynamic_token_to_token_patterns or {})
    return token_to_token_patterns

def _get_base_token_dict(pattern_definition: Mapping) -> Dict[str, List]:
    return {next(iter(base_token_dict.keys())):next(iter(base_token_dict.values()))[0] for base_token_dict in pattern_definition['base_tokens']}

def _get_static_token_to_token_patterns(pattern_definition: Mapping) -> Mapping[str, Tuple[Tuple[Tuple[str, ...], ...], ...]]:
    return {
        static_token: _convert_static_token_patterns_to_tuple(static_token_patterns, pattern_definition)
        for token_type_dict in pattern_definition['token_patterns']
        for token_type in token_type_dict
        if token_type == 'static'
        for static_token_to_token_patterns in token_type_dict['static']
        for static_token, static_token_patterns in static_token_to_token_patterns.items()
    }

def _convert_static_token_patterns_to_tuple(token_patterns: List[List[List[str]]], pattern_definition: Mapping) -> Tuple[Tuple[Tuple[str, ...], ...], ...]:
    if 'base_tokens' in pattern_definition:
        base_token_dict = _get_base_token_dict(pattern_definition)
        expanded_token_patterns = []
        for token_pattern in token_patterns:
            expanded_token_pattern = []
            for phrases in token_pattern:
                for word in phrases:
                    if word in base_token_dict:
                        phrases = base_token_dict[word]
                expanded_token_pattern.append(phrases)
            expanded_token_patterns.append(expanded_token_pattern)
        token_patterns = expanded_token_patterns
    return tuple(tuple(tuple(phrases) for phrases in token_pattern) for token_pattern in token_patterns)

def _compute_utterance_combination(utterance_pattern: Tuple[Tuple[Tuple[Tuple[str, ...], ...], ...], ...]) -> Tuple[Tuple[str, ...], ...]:
    utterance_combination = []
    for token_patterns in utterance_pattern:
        utterance_components = []
        for token_pattern in token_patterns:
            utterance_component = _join_token_pattern(token_pattern)
            utterance_components.append(utterance_component)
        chained_utterance_components = tuple(itertools.chain.from_iterable(utterance_components))
        utterance_combination.append(chained_utterance_components)
    return tuple(utterance_combination)

def _compute_handled_token_combination(utterance_combination: Tuple[Tuple[str, ...], ...],
                                       tokens: Tuple[str, ...],
                                       token_handlers: Optional[Mapping[str, Callable[[str, str], str]]] = None
                                       ) -> Tuple[Tuple[str, ...], ...]:
    handled_token_combination = []
    for token_phrases, token in zip(utterance_combination, tokens):
        token_components = []
        for token_phrase in token_phrases:
            token_handler = _get_token_handler(token, token_handlers)
            token_component = token_handler(token, token_phrase)
            token_components.append(token_component)
        handled_token_combination.append(tuple(token_components))
    return tuple(handled_token_combination)

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
