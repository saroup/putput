from typing import Any, List, Optional


class YmlValidationException(Exception):
    pass


def _raise_validation_exception(message: str = 'Invalid yml') -> None:
    raise YmlValidationException(message)


def _validate_instance(item: Any, instance: Any, err_msg: Optional[str] = None) -> None:
    if not item or not isinstance(item, instance):
        if err_msg:
            _raise_validation_exception(err_msg)
        else:
            _raise_validation_exception()


def _validate_tokens(input_dict: dict) -> None:
    if ((not 'tokens' in input_dict) or
            (not input_dict['tokens']) or
            (not len(input_dict['tokens']) <= 2) or
            (not isinstance(input_dict['tokens'], list))):
        _raise_validation_exception()
    for token_type_dict in input_dict['tokens']:
        _validate_instance(token_type_dict, dict)
        for token_type in token_type_dict:
            if token_type not in ['static', 'dynamic']:
                _raise_validation_exception()
            if token_type == 'static':
                _validate_static_tokens(token_type_dict['static'])
            if token_type == 'dynamic':
                _validate_dynamic_tokens(token_type_dict['dynamic'])


def _validate_utterances(input_dict: dict) -> None:
    if not 'utterances' in input_dict or not input_dict['utterances']:
        _raise_validation_exception()
    for utterance_pattern_tokens in input_dict['utterances']:
        _validate_instance(utterance_pattern_tokens, list)
        for token in utterance_pattern_tokens:
            _validate_instance(token, str)


def _validate_static_tokens(static_dicts: list) -> None:
    _validate_instance(static_dicts, list)
    for token_patterns_dict in static_dicts:
        _validate_instance(token_patterns_dict, dict)
        for token_patterns in token_patterns_dict.values():
            _validate_instance(token_patterns, list)
            for token_pattern in token_patterns:
                _validate_instance(token_pattern, list)
                for component in token_pattern:
                    _validate_instance(component, list)
                    for word in component:
                        _validate_instance(word, str)


def _validate_dynamic_tokens(dynamic_dicts: list) -> None:
    _validate_instance(dynamic_dicts, list)
    for token in dynamic_dicts:
        _validate_instance(token, str)


def _get_static_tokens(input_dict: dict) -> List[str]:
    return [
        token
        for token_type_dict in input_dict['tokens']
        for token_type in token_type_dict
        if token_type == 'static'
        for token_patterns_dict in token_type_dict['static']
        for token in token_patterns_dict.keys()
    ]


def _get_dynamic_tokens(input_dict: dict) -> List[str]:
    return [
        token
        for token_type_dict in input_dict['tokens']
        for token_type in token_type_dict
        if token_type == 'dynamic'
        for token in token_type_dict['dynamic']
    ]


def _validate_utterance_tokens_in_static_and_dynamic(input_dict: dict) -> None:
    static_tokens = _get_static_tokens(input_dict)
    dynamic_tokens = _get_dynamic_tokens(input_dict)
    all_utterance_pattern_tokens = [
        token
        for utterance_pattern_tokens in input_dict['utterances']
        for token in utterance_pattern_tokens
    ]

    for token in all_utterance_pattern_tokens:
        if token not in static_tokens + dynamic_tokens:
            _raise_validation_exception()


def _validate_at_least_dynamic_tokens_or_static_tokens_exist(input_dict: dict) -> None:
    if not (_get_dynamic_tokens(input_dict) or _get_static_tokens(input_dict)):
        _raise_validation_exception()


def _validate_only_tokens_and_utterances(input_dict: dict) -> None:
    for key in input_dict.keys():
        if key not in ['tokens', 'utterances']:
            _raise_validation_exception()


def validate_yml(input_dict: dict) -> None:
    _validate_at_least_dynamic_tokens_or_static_tokens_exist(input_dict)
    _validate_only_tokens_and_utterances(input_dict)
    _validate_tokens(input_dict)
    _validate_utterances(input_dict)
    _validate_utterance_tokens_in_static_and_dynamic(input_dict)
