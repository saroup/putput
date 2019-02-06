"""This module provides functionality to generate utterances and tokens after processing the pattern definition."""
import itertools
from functools import lru_cache
from pathlib import Path
from typing import Dict # pylint: disable=unused-import
from typing import Iterable
from typing import Mapping
from typing import Optional
from typing import Tuple

import yaml

from putput.joiner import CombinationOptions
from putput.joiner import join_combination
from putput.types import BASE_TOKEN
from putput.types import EXPANDED_TOKEN_PATTERN
from putput.types import EXPANDED_UTTERANCE_PATTERN
from putput.types import HANDLED_TOKENS
from putput.types import HASHABLE_TOKEN_PATTERN
from putput.types import HASHABLE_TOKEN_PATTERNS
from putput.types import TOKEN
from putput.types import TOKEN_COMBINATION
from putput.types import TOKEN_COMPONENT
from putput.types import TOKEN_HANDLER
from putput.types import TOKEN_PATTERNS
from putput.types import TOKEN_PATTERNS_WITH_BASE_TOKENS
from putput.types import TOKENS
from putput.types import UTTERANCE
from putput.types import UTTERANCE_COMBINATION
from putput.validator import validate_pattern_definition



def generate_utterance_combinations_and_tokens(pattern_definition_path: Path,
                                               dynamic_token_patterns_map: Optional[Mapping[TOKEN,
                                                                                            TOKEN_PATTERNS]] = None
                                               ) -> Iterable[Tuple[UTTERANCE_COMBINATION, TOKENS]]:
    pattern_definition = _load_pattern_definition(pattern_definition_path)
    validate_pattern_definition(pattern_definition)
    token_patterns_map = _get_token_patterns_map(pattern_definition, dynamic_token_patterns_map)

    for tokens in pattern_definition['utterance_patterns']:
        expanded_utterance_pattern = tuple(token_patterns_map[token] for token in tokens)
        utterance_combination = _compute_utterance_combination(expanded_utterance_pattern)
        yield utterance_combination, tuple(tokens)

def generate_utterances_and_handled_tokens(utterance_combination: UTTERANCE_COMBINATION,
                                           tokens: TOKENS,
                                           token_handler_map: Optional[Mapping[TOKEN, TOKEN_HANDLER]] = None,
                                           combination_options: Optional[CombinationOptions] = None
                                           ) -> Iterable[Tuple[UTTERANCE, HANDLED_TOKENS]]:
    handled_token_combination = _compute_handled_token_combination(utterance_combination,
                                                                   tokens,
                                                                   token_handler_map)
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

def _get_token_patterns_map(pattern_definition: Mapping,
                            dynamic_token_patterns_map: Optional[Mapping[TOKEN, TOKEN_PATTERNS]] = None
                            ) -> Mapping[TOKEN, TOKEN_PATTERNS]:
    token_patterns_map = {} # type: Dict[TOKEN, TOKEN_PATTERNS]
    static_token_patterns_map = _get_static_token_patterns_map(pattern_definition)
    token_patterns_map.update(static_token_patterns_map)
    token_patterns_map.update(dynamic_token_patterns_map or {})
    return token_patterns_map

def _get_base_token_map(pattern_definition: Mapping) -> Mapping[BASE_TOKEN, TOKEN_COMPONENT]:
    base_token_map = {next(iter(base_token_map.keys())): next(iter(base_token_map.values()))
                      for base_token_map in pattern_definition['base_tokens']}
    return base_token_map

def _get_static_token_patterns_map(pattern_definition: Mapping) -> Mapping[TOKEN, TOKEN_PATTERNS]:
    return {
        token: _process_static_token_patterns(pattern_definition, token_patterns)
        for token_type_map in pattern_definition['token_patterns']
        for token_type in token_type_map
        if token_type == 'static'
        for static_token_patterns_map in token_type_map['static']
        for token, token_patterns in static_token_patterns_map.items()
    }

def _process_static_token_patterns(pattern_definition: Mapping,
                                   token_patterns: TOKEN_PATTERNS_WITH_BASE_TOKENS
                                   ) -> TOKEN_PATTERNS:
    if 'base_tokens' in pattern_definition:
        token_patterns = _expand_base_tokens(pattern_definition, token_patterns)
    return _convert_token_patterns_to_tuples(token_patterns)

def _convert_token_patterns_to_tuples(token_patterns: TOKEN_PATTERNS) -> HASHABLE_TOKEN_PATTERNS:
    return tuple(tuple(tuple(phrases) for phrases in token_pattern) for token_pattern in token_patterns)

def _expand_base_tokens(pattern_definition: Mapping, token_patterns: TOKEN_PATTERNS_WITH_BASE_TOKENS) -> TOKEN_PATTERNS:
    base_token_map = _get_base_token_map(pattern_definition)
    return tuple(tuple(base_token_map[component] if isinstance(component, str) else component
                       for component in token_pattern) for token_pattern in token_patterns)

def _compute_utterance_combination(expanded_utterance_pattern: EXPANDED_UTTERANCE_PATTERN) -> UTTERANCE_COMBINATION:
    utterance_combination = []
    for token_patterns in expanded_utterance_pattern:
        hashable_token_patterns = _convert_token_patterns_to_tuples(token_patterns)
        expanded_token_patterns = tuple(_expand_token_pattern(token_pattern)
                                        for token_pattern in hashable_token_patterns)
        utterance_components = tuple(itertools.chain.from_iterable(expanded_token_patterns))
        utterance_combination.append(utterance_components)
    return tuple(utterance_combination)

def _compute_handled_token_combination(utterance_combination: UTTERANCE_COMBINATION,
                                       tokens: TOKENS,
                                       token_handler_map: Optional[Mapping[TOKEN, TOKEN_HANDLER]] = None
                                       ) -> TOKEN_COMBINATION:
    handled_token_combination = []
    for utterance_component, token in zip(utterance_combination, tokens):
        token_components = tuple(_get_token_handler(token, token_handler_map)(token, phrase_to_tokenize)
                                 for phrase_to_tokenize in utterance_component)
        handled_token_combination.append(token_components)
    return tuple(handled_token_combination)

def _get_token_handler(token: TOKEN,
                       token_handler_map: Optional[Mapping[TOKEN, TOKEN_HANDLER]] = None
                       ) -> TOKEN_HANDLER:
    default_token_handler = lambda token, _: '[' + token + ']'
    if token_handler_map:
        return token_handler_map.get(token) or token_handler_map.get('DEFAULT') or default_token_handler
    return default_token_handler

@lru_cache(maxsize=None)
def _expand_token_pattern(token_pattern: HASHABLE_TOKEN_PATTERN) -> EXPANDED_TOKEN_PATTERN:
    return tuple(' '.join(phrase) for phrase in join_combination(token_pattern))
