"""This module provides functionality to validate the pattern definition."""
from pathlib import Path
from typing import Any, Set

import yaml


class PatternDefinitionValidationError(Exception):
    """Exception that describes invalid pattern defintions"""


def _validate_instance(item: Any, instance: Any, err_msg: str) -> None:
    if not item or not isinstance(item, instance):
        raise PatternDefinitionValidationError(err_msg)

def _check_for_overlap(static_tokens: Set[str], dynamic_tokens: Set[str]) -> None:
    overlap = static_tokens & dynamic_tokens
    if overlap:
        err_msg = ('{} cannot be defined as both static and dynamic tokens'.format(overlap))
        raise PatternDefinitionValidationError(err_msg)

def _check_for_undefined_utterance_pattern_tokens(static_tokens: Set[str],
                                                  dynamic_tokens: Set[str],
                                                  utterance_pattern_tokens: Set[str]) -> None:
    undefined_tokens = utterance_pattern_tokens - (static_tokens | dynamic_tokens)
    if undefined_tokens:
        err_msg = '{} utterance_patterns must be defined as as a static or dynamic tokens.'.format(undefined_tokens)
        raise PatternDefinitionValidationError(err_msg)

def _validate_utterances(pattern_definition: dict) -> None:
    for utterance_pattern_tokens in pattern_definition['utterance_patterns']:
        _validate_instance(utterance_pattern_tokens, list, 'utterance_patterns must contain a list')
        for token in utterance_pattern_tokens:
            _validate_instance(token, str, 'utterance_pattern tokens must be strings')

def _validate_static_tokens(static_dicts: list) -> None:
    err_msg = 'invalid static token_patterns'
    for token_patterns_dict in static_dicts:
        _validate_instance(token_patterns_dict, dict, err_msg)
        for token_patterns in token_patterns_dict.values():
            _validate_instance(token_patterns, list, err_msg)
            for token_pattern in token_patterns:
                _validate_instance(token_pattern, list, err_msg)
                for component in token_pattern:
                    _validate_instance(component, list, err_msg)
                    for word in component:
                        _validate_instance(word, str, err_msg)

def _validate_token_patterns(pattern_definition: dict) -> None:
    _validate_instance(pattern_definition['token_patterns'], list, 'invalid token_patterns')
    for token_type_dict in pattern_definition['token_patterns']:
        _validate_instance(token_type_dict, dict, 'invalid token_patterns')
        if len(token_type_dict) > 1:
            raise PatternDefinitionValidationError('invalid token_patterns')
        if 'static' in token_type_dict:
            _validate_static_tokens(token_type_dict['static'])
        elif 'dynamic' in token_type_dict:
            for token in token_type_dict['dynamic']:
                _validate_instance(token, str, 'invalid dynamic token_patterns')
        else:
            raise PatternDefinitionValidationError('token type must be either dynamic or static')

def validate_pattern_definition(pattern_definition_path: Path) -> None:
    """Validates pattern definitions.

    Args:
        pattern_definition: The pattern definition file converted to a python dictionary.

    Raises:
        PatternDefinitionValidationError: If the pattern definition file is invalid.
    """
    try:
        with pattern_definition_path.open(encoding='utf-8') as pattern_definition_file:
            pattern_definition = yaml.load(pattern_definition_file)
        if not {'token_patterns', 'utterance_patterns'} == set(pattern_definition):
            err_msg = 'At the top level, token_patterns and utterance_patterns must exist. No other keys may exist.'
            raise PatternDefinitionValidationError(err_msg)
        _validate_token_patterns(pattern_definition)
        _validate_utterances(pattern_definition)

        static_tokens = {
            token
            for token_type_dict in pattern_definition['token_patterns']
            for token_type in token_type_dict
            if token_type == 'static'
            for token_patterns_dict in token_type_dict['static']
            for token in token_patterns_dict.keys()
        }
        dynamic_tokens = {
            token
            for token_type_dict in pattern_definition['token_patterns']
            for token_type in token_type_dict
            if token_type == 'dynamic'
            for token in token_type_dict['dynamic']
        }
        utterance_pattern_tokens = {
            token
            for utterance_pattern_tokens in pattern_definition['utterance_patterns']
            for token in utterance_pattern_tokens
        }
        _check_for_overlap(static_tokens, dynamic_tokens)
        _check_for_undefined_utterance_pattern_tokens(static_tokens, dynamic_tokens, utterance_pattern_tokens)
    except Exception as e:
        raise PatternDefinitionValidationError(e)
