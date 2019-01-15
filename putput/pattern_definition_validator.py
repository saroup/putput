"""This module provides functionality to validate the pattern definition."""
from typing import Any, List


class PatternDefinitionValidationException(Exception):
    """Exception that describes invalid pattern defintions"""


def _raise_validation_exception(message: str = 'Invalid Pattern Definition') -> None:
    raise PatternDefinitionValidationException(message)

def _validate_instance(item: Any, instance: Any, err_msg: str) -> None:
    if not item or not isinstance(item, instance):
        _raise_validation_exception(err_msg)

def _validate_tokens(pattern_definition_dict: dict) -> None:
    if 'token_patterns' not in pattern_definition_dict:
        _raise_validation_exception('token_patterns key does not exist')
    if not pattern_definition_dict['token_patterns']:
        _raise_validation_exception('token_patterns do not exist')
    if len(pattern_definition_dict['token_patterns']) > 2:
        _raise_validation_exception('more than two keys under token_patterns exist. Only use "static" and "dynamic"')
    if not isinstance(pattern_definition_dict['token_patterns'], list):
        _raise_validation_exception('invalid token_patterns')

    for token_type_dict in pattern_definition_dict['token_patterns']:
        _validate_instance(token_type_dict, dict, 'invalid token_patterns')
        for token_type in token_type_dict:
            if token_type not in ['static', 'dynamic']:
                err_msg = 'token_patterns key {} found. Only use "static" and "dynamic"'.format(token_type)
                _raise_validation_exception(err_msg)
            if token_type == 'static':
                _validate_static_tokens(token_type_dict['static'])
            if token_type == 'dynamic':
                _validate_dynamic_tokens(token_type_dict['dynamic'])

def _validate_utterances(pattern_definition_dict: dict) -> None:
    if not 'utterance_patterns' in pattern_definition_dict or not pattern_definition_dict['utterance_patterns']:
        _raise_validation_exception('utterance_patterns key does not exist')
    err_msg = 'invalid utterance_patterns'
    for utterance_pattern_tokens in pattern_definition_dict['utterance_patterns']:
        _validate_instance(utterance_pattern_tokens, list, err_msg)
        for token in utterance_pattern_tokens:
            _validate_instance(token, str, err_msg)

def _validate_static_tokens(static_dicts: list) -> None:
    err_msg = 'invalid static token_patterns'
    _validate_instance(static_dicts, list, err_msg)
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

def _validate_dynamic_tokens(dynamic_dicts: list) -> None:
    err_msg = 'invalid dynamic token_patterns'
    _validate_instance(dynamic_dicts, list, err_msg)
    for token in dynamic_dicts:
        _validate_instance(token, str, err_msg)

def _get_static_tokens(pattern_definition_dict: dict) -> List[str]:
    return [
        token
        for token_type_dict in pattern_definition_dict['token_patterns']
        for token_type in token_type_dict
        if token_type == 'static'
        for token_patterns_dict in token_type_dict['static']
        for token in token_patterns_dict.keys()
    ]

def _get_dynamic_tokens(pattern_definition_dict: dict) -> List[str]:
    return [
        token
        for token_type_dict in pattern_definition_dict['token_patterns']
        for token_type in token_type_dict
        if token_type == 'dynamic'
        for token in token_type_dict['dynamic']
    ]

def _validate_utterance_tokens_in_static_and_dynamic(pattern_definition_dict: dict) -> None:
    static_tokens = _get_static_tokens(pattern_definition_dict)
    dynamic_tokens = _get_dynamic_tokens(pattern_definition_dict)
    all_utterance_pattern_tokens = [
        token
        for utterance_pattern_tokens in pattern_definition_dict['utterance_patterns']
        for token in utterance_pattern_tokens
    ]

    err_msg = 'An utterance_pattern uses an undefined token. Include the token in static or dynamic token_patterns.'
    for token in all_utterance_pattern_tokens:
        if token not in static_tokens + dynamic_tokens:
            _raise_validation_exception(err_msg)

def _validate_at_least_dynamic_tokens_or_static_tokens_exist(pattern_definition_dict: dict) -> None:
    if not (_get_dynamic_tokens(pattern_definition_dict) or _get_static_tokens(pattern_definition_dict)):
        _raise_validation_exception('Either static or dynamic token_patterns must exist')

def _validate_only_tokens_and_utterances(pattern_definition_dict: dict) -> None:
    for key in pattern_definition_dict.keys():
        if key not in ['token_patterns', 'utterance_patterns']:
            _raise_validation_exception('At the top level, a key besides token_patterns or utterance_patterns exists')

def validate_pattern_definition(pattern_definition: dict) -> None:
    """Validates pattern definitions.

    Args:
        pattern_definition: The pattern definition file converted to a python dictionary.

    Raises:
        PatternDefinitionValidationException: If the pattern definition file is invalid.
    """
    _validate_only_tokens_and_utterances(pattern_definition)
    _validate_at_least_dynamic_tokens_or_static_tokens_exist(pattern_definition)
    _validate_tokens(pattern_definition)
    _validate_utterances(pattern_definition)
    _validate_utterance_tokens_in_static_and_dynamic(pattern_definition)
