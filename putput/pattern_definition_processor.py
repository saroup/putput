"""This module provides functionality to process the pattern definition into data structures for downstream use."""
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Tuple

import yaml

from putput.pattern_definition_validator import validate_pattern_definition

TokenPattern = Tuple[Tuple[str, ...], ...]
UtterancePattern = Tuple[Tuple[TokenPattern, ...], ...]

def generate_utterance_pattern_and_tokens(pattern_definition_path: Path,
                                          dynamic_token_patterns_definition: Optional[Mapping[str,
                                                                                              Tuple[TokenPattern,
                                                                                                    ...]]] = None
                                          ) -> Iterable[Tuple[UtterancePattern, Tuple[str, ...]]]:
    """This function generates UtterancePattern-token pairs.

    Args:
        pattern_definition_path: Path to the pattern defintion file.
        dynamic_token_patterns_definition: A mapping of token -> TokenPatterns. Useful
        for TokenPatterns that can only be known at runtime.

    Yields:
        UtterancePattern-token pairs.
    """
    with pattern_definition_path.open(encoding='utf-8') as pattern_definition_file:
        pattern_definition = yaml.load(pattern_definition_file)
    validate_pattern_definition(pattern_definition)
    static_token_patterns_dict = _get_static_token_patterns_dict(pattern_definition)
    token_patterns_dict = dict(static_token_patterns_dict)
    token_patterns_dict.update(dynamic_token_patterns_definition or {})
    return (
        (tuple(token_patterns_dict[token]
               for token in tokens), tuple(tokens))
        for tokens in pattern_definition['utterance_patterns']
    )

def _get_static_token_patterns_dict(pattern_definition: Dict) -> Dict[str, Tuple[TokenPattern, ...]]:
    return {
        token: _convert_token_patterns_to_tuple(token_patterns)
        for token_type_dict in pattern_definition['token_patterns']
        for token_type in token_type_dict
        if token_type == 'static'
        for token_patterns_dict in token_type_dict['static']
        for token, token_patterns in token_patterns_dict.items()
    }

def _convert_token_patterns_to_tuple(token_patterns: List[List[List[str]]]) -> Tuple[TokenPattern, ...]:
    return tuple(tuple(tuple(phrases) for phrases in token_pattern) for token_pattern in token_patterns)
