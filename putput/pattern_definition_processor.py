"""This module provides functionality to process the pattern definition into data structures for downstream use."""
from pathlib import Path
from typing import Iterable, List, Mapping, Optional, Tuple

from putput.pattern_definition_validator import validate_pattern_definition

TokenPattern = Tuple[Tuple[str, ...], ...]
UtterancePattern = Tuple[Tuple[TokenPattern, ...], ...]

_TokenToTokenPatterns = Mapping[str, Tuple[TokenPattern, ...]]

def generate_utterance_pattern_and_tokens(pattern_definition_path: Path,
                                          dynamic_token_to_token_patterns: Optional[_TokenToTokenPatterns] = None
                                          ) -> Iterable[Tuple[UtterancePattern, Tuple[str, ...]]]:
    """Generates UtterancePattern-token pairs for downstream processing.

    Args:
        pattern_definition_path: Path to the pattern definition file.
        dynamic_token_to_token_patterns: A mapping of token -> TokenPatterns. Useful
        for TokenPatterns that can only be known at runtime.

    Yields:
        UtterancePattern-token pairs.
    """
    pattern_definition = validate_pattern_definition(pattern_definition_path)
    token_to_token_patterns = _get_token_to_token_patterns(pattern_definition, dynamic_token_to_token_patterns)

    for tokens in pattern_definition['utterance_patterns']:
        token_patterns = []
        for token in tokens:
            token_patterns.append(token_to_token_patterns[token])
        yield tuple(token_patterns), tuple(tokens)

def _get_token_to_token_patterns(pattern_definition: Mapping,
                                 dynamic_token_to_token_patterns: Optional[_TokenToTokenPatterns] = None
                                 ) -> _TokenToTokenPatterns:
    static_token_to_token_patterns = _get_static_token_to_token_patterns(pattern_definition)
    token_to_token_patterns = dict(static_token_to_token_patterns)
    token_to_token_patterns.update(dynamic_token_to_token_patterns or {})
    return token_to_token_patterns

def _get_static_token_to_token_patterns(pattern_definition: Mapping) -> _TokenToTokenPatterns:
    return {
        static_token: _convert_static_token_patterns_to_tuple(static_token_patterns)
        for token_type_dict in pattern_definition['token_patterns']
        for token_type in token_type_dict
        if token_type == 'static'
        for static_token_to_token_patterns in token_type_dict['static']
        for static_token, static_token_patterns in static_token_to_token_patterns.items()
    }

def _convert_static_token_patterns_to_tuple(token_patterns: List[List[List[str]]]) -> Tuple[TokenPattern, ...]:
    return tuple(tuple(tuple(phrases) for phrases in token_pattern) for token_pattern in token_patterns)
