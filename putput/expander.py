"""This module provides functionality to generate utterances and tokens after processing the pattern definition."""
import re
from functools import lru_cache
from itertools import chain
from itertools import product
from itertools import repeat
from pathlib import Path
from typing import Dict  # pylint: disable=unused-import
from typing import Iterable
from typing import List  # pylint: disable=unused-import
from typing import Mapping
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union
from typing import cast

import yaml

from putput.joiner import join_combo
from putput.types import COMBO
from putput.types import GROUP
from putput.types import TOKEN_PATTERN
from putput.types import TOKEN_PATTERNS_MAP
from putput.validator import RANGE_REGEX
from putput.validator import validate_pattern_def

# TODO: get rid of types, all public ones (i/o of functions) should be without _
_TOKEN_PATTERNS_WITH_BASE_TOKENS = Sequence[Sequence[Union[str, Sequence[str]]]]
_BASE_ITEM_MAP = Mapping[str, Sequence[str]]
_EXPANDED_BASE_ITEM_MAP = Mapping[str, Sequence[Sequence[str]]]
_HASHABLE_TOKEN_PATTERN = Tuple[Tuple[str, ...], ...]

def expand(pattern_def_path: Path,
           *,
           dynamic_token_patterns_map: Optional[TOKEN_PATTERNS_MAP] = None
           ) -> Tuple[int, Iterable[Tuple[COMBO, Sequence[str], Sequence[GROUP]]]]:
    """Yields utterance_combo, tokens, group"""
    pattern_def = _load_pattern_def(pattern_def_path)
    validate_pattern_def(pattern_def)
    group_map = _get_base_item_map(pattern_def, 'groups')
    utterance_patterns, groups = _expand_utterance_patterns_groups(_expand_utterance_patterns_ranges(
        pattern_def['utterance_patterns']), group_map)

    def _expand() -> Iterable[Tuple[COMBO, Sequence[str], Sequence[GROUP]]]:
        token_patterns_map = _get_token_patterns_map(pattern_def, dynamic_token_patterns_map=dynamic_token_patterns_map)
        for utterance_pattern, group in zip(utterance_patterns, groups):
            utterance_combo = _compute_utterance_combo(utterance_pattern, token_patterns_map)
            yield utterance_combo, tuple(utterance_pattern), tuple(group)
    return len(utterance_patterns), _expand()

def _expand_utterance_patterns_ranges(utterance_patterns: Sequence[Sequence[str]]) -> Sequence[Sequence[str]]:
    return tuple(chain.from_iterable(map(_expand_ranges, utterance_patterns)))

def _expand_ranges(utterance_pattern: Sequence[str]) -> Sequence[Sequence[str]]:
    ranges = tuple(map(_parse_range_token, utterance_pattern))
    ranges_and_tokens = filter(lambda r_and_t: not re.match(RANGE_REGEX, r_and_t[2]),
                               map(lambda r_and_t: r_and_t[0] + (r_and_t[1],),
                                   zip(ranges[1:] + ((0, 0),), utterance_pattern)))
    expanded_utterance_pattern = tuple(map(tuple, map(chain.from_iterable, # type: ignore
                                                      product(*map(_expand_tokens, ranges_and_tokens))))) # type: ignore
    return cast(Sequence[Sequence[str]], expanded_utterance_pattern)

def _parse_range_token(token: str) -> Tuple[int, int]:
    if re.match(RANGE_REGEX, token):
        if '-' not in token:
            return int(token), int(token) + 1
        min_range, max_range = token.split('-')
        return int(min_range), int(max_range) + 1
    return (0, 0)

def _expand_tokens(range_token: Tuple[int, int, str]) -> Sequence[Sequence[str]]:
    min_range, max_range, token = range_token
    if min_range == 0 and max_range == 0:
        return ((token,),)
    return tuple(map(lambda i: (token,) * i, range(min_range, max_range)))

def _load_pattern_def(pattern_def_path: Path) -> Mapping:
    with pattern_def_path.open(encoding='utf-8') as pattern_def_file:
        pattern_def = yaml.load(pattern_def_file, Loader=yaml.BaseLoader)
    return pattern_def

def _get_token_patterns_map(pattern_def: Mapping,
                            *,
                            dynamic_token_patterns_map: Optional[TOKEN_PATTERNS_MAP] = None
                            ) -> TOKEN_PATTERNS_MAP:
    token_patterns_map = {} # type: Dict[str, Sequence[TOKEN_PATTERN]]
    static_token_patterns_map = _get_static_token_patterns_map(pattern_def)
    token_patterns_map.update(static_token_patterns_map)
    token_patterns_map.update(dynamic_token_patterns_map or {})
    return token_patterns_map

def _get_base_item_map(pattern_def: Mapping, base_key: str) -> _BASE_ITEM_MAP:
    if base_key in pattern_def:
        return {next(iter(base_item_map.keys())): tuple(next(iter(base_item_map.values())))
                for base_item_map in pattern_def[base_key]}
    return {}

def _get_static_token_patterns_map(pattern_def: Mapping) -> TOKEN_PATTERNS_MAP:
    return {
        token: _expand_static_token_patterns(pattern_def, token_patterns)
        for token_type_map in pattern_def['token_patterns']
        for token_type in token_type_map
        if token_type == 'static'
        for static_token_patterns_map in token_type_map['static']
        for token, token_patterns in static_token_patterns_map.items()
    }

def _expand_static_token_patterns(pattern_def: Mapping,
                                  token_patterns: _TOKEN_PATTERNS_WITH_BASE_TOKENS
                                  ) -> Sequence[TOKEN_PATTERN]:
    if 'base_tokens' in pattern_def:
        token_patterns = _expand_base_tokens(pattern_def, token_patterns)
    return _convert_token_patterns_to_tuples(token_patterns)

def _convert_token_patterns_to_tuples(token_patterns: Sequence[TOKEN_PATTERN]) -> Tuple[_HASHABLE_TOKEN_PATTERN, ...]:
    return tuple(tuple(tuple(phrases) for phrases in token_pattern) for token_pattern in token_patterns)

def _expand_base_tokens(pattern_def: Mapping,
                        token_patterns: _TOKEN_PATTERNS_WITH_BASE_TOKENS
                        ) -> Sequence[TOKEN_PATTERN]:
    base_token_map = _get_base_item_map(pattern_def, 'base_tokens')
    return tuple(tuple(base_token_map[component] if isinstance(component, str) else component
                       for component in token_pattern) for token_pattern in token_patterns)

def _expand_utterance_patterns_groups(utterance_patterns: Sequence[Sequence[str]],
                                      group_map: _BASE_ITEM_MAP
                                      ) -> Tuple[Sequence[Sequence[str]], Sequence[Sequence[GROUP]]]:
    expanded_group_map = {name: _expand_ranges(pattern) for name, pattern in group_map.items()}
    expanded_utterance_patterns = tuple(chain.from_iterable(map(_expand_groups,
                                                                utterance_patterns, repeat(expanded_group_map))))
    expanded_groups = tuple(chain.from_iterable(map(_create_groups,
                                                    utterance_patterns, repeat(expanded_group_map))))
    return expanded_utterance_patterns, expanded_groups

def _create_groups(utterance_pattern: Sequence[str],
                   expanded_group_map: Mapping[str, Sequence[Sequence[str]]]
                   ) -> Iterable[Sequence[GROUP]]:
    groups = map(_get_groups, utterance_pattern, repeat(expanded_group_map))
    return product(*groups)

def _expand_groups(utterance_pattern: Sequence[str],
                   expanded_group_map: Mapping[str, Sequence[Sequence[str]]]
                   ) -> Iterable[Sequence[str]]:
    utterance_pattern_replaced_groups = map(lambda token, group_map: group_map.get(token, ((token,),)),
                                            utterance_pattern, repeat(expanded_group_map))
    expanded_groups = map(tuple, map(chain.from_iterable, product(*utterance_pattern_replaced_groups))) # type: ignore
    return cast(Iterable[Sequence[str]], expanded_groups)

def _get_groups(token: str, expanded_group_map: Mapping[str, Sequence[Sequence[str]]]) -> Iterable[GROUP]:
    if token not in expanded_group_map:
        return (('None', 1),)
    return map(lambda token, group: (token, len(group)), repeat(token), expanded_group_map[token])

def _compute_utterance_combo(utterance_pattern: Sequence[str], token_patterns_map: TOKEN_PATTERNS_MAP) -> COMBO:
    expanded_utterance_pattern = tuple(token_patterns_map[token] for token in utterance_pattern)
    utterance_combo = []
    for token_patterns in expanded_utterance_pattern:
        hashable_token_patterns = _convert_token_patterns_to_tuples(token_patterns)
        expanded_token_patterns = tuple(_expand_token_pattern(token_pattern)
                                        for token_pattern in hashable_token_patterns)
        utterance_components = tuple(chain.from_iterable(expanded_token_patterns))
        utterance_combo.append(utterance_components)
    return tuple(utterance_combo)

@lru_cache(maxsize=None)
def _expand_token_pattern(token_pattern: _HASHABLE_TOKEN_PATTERN) -> Sequence[str]:
    return tuple(' '.join(phrase) for phrase in join_combo(token_pattern))
