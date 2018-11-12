from typing import Any, List


class YmlValidationException(Exception):
    pass


class InputValidator:
    def __init__(self, input_dict: dict) -> None:
        self._input_dict = input_dict

    @staticmethod
    def _raise_validation_exception(message: str = 'Invalid yml') -> None:
        raise YmlValidationException(message)

    def _validate_instance(self, item: Any, instance: Any, err_msg: str = 'lol') -> None:
        if not item or not isinstance(item, instance):
            self._raise_validation_exception(err_msg)

    def _validate_tokens(self) -> None:
        if ((not 'tokens' in self._input_dict) or (not self._input_dict['tokens'])
                or (not len(self._input_dict['tokens']) <= 2) or (not isinstance(self._input_dict['tokens'], list))):
            self._raise_validation_exception()

        for token_type_dict in self._input_dict['tokens']:
            self._validate_instance(token_type_dict, dict)
            for token_type in token_type_dict:
                if token_type not in ['static', 'dynamic']:
                    self._raise_validation_exception()
                if token_type == 'static':
                    self._validate_static_tokens(token_type_dict['static'])
                if token_type == 'dynamic':
                    self._validate_dynamic_tokens(token_type_dict['dynamic'])

    def _validate_utterances(self) -> None:
        if not 'utterances' in self._input_dict or not self._input_dict['utterances']:
            self._raise_validation_exception()
        for utterance_pattern_tokens in self._input_dict['utterances']:
            self._validate_instance(utterance_pattern_tokens, list)
            for token in utterance_pattern_tokens:
                self._validate_instance(token, str)

    def _validate_static_tokens(self, static_dicts: list) -> None:
        self._validate_instance(static_dicts, list)
        for token_patterns_dict in static_dicts:
            self._validate_instance(token_patterns_dict, dict)
            for token_patterns in token_patterns_dict.values():
                self._validate_instance(token_patterns, list)
                for token_pattern in token_patterns:
                    self._validate_instance(token_pattern, list)
                    for component in token_pattern:
                        self._validate_instance(component, list)
                        for word in component:
                            self._validate_instance(word, str)

    def _validate_dynamic_tokens(self, dynamic_dicts: list) -> None:
        self._validate_instance(dynamic_dicts, list)
        for token in dynamic_dicts:
            self._validate_instance(token, str)

    def _get_static_tokens(self) -> List[str]:
        return [
            token for token_type_dict in self._input_dict['tokens'] for token_type in token_type_dict
            if token_type == 'static' for token_patterns_dict in token_type_dict['static']
            for token in token_patterns_dict.keys()
        ]

    def _get_dynamic_tokens(self) -> List[str]:
        return [
            token for token_type_dict in self._input_dict['tokens'] for token_type in token_type_dict
            if token_type == 'dynamic' for token in token_type_dict['dynamic']
        ]

    def _validate_utterance_tokens_in_static_and_dynamic(self) -> None:
        static_tokens = self._get_static_tokens()
        dynamic_tokens = self._get_dynamic_tokens()
        all_utterance_pattern_tokens = [
            token for utterance_pattern_tokens in self._input_dict['utterances'] for token in utterance_pattern_tokens
        ]

        for token in all_utterance_pattern_tokens:
            if token not in static_tokens + dynamic_tokens:
                self._raise_validation_exception()

    def _validate_at_least_dynamic_tokens_or_static_tokens_exist(self) -> None:
        if not (self._get_dynamic_tokens() or self._get_static_tokens()):
            self._raise_validation_exception()

    def _validate_only_tokens_and_utterances(self) -> None:
        for key in self._input_dict.keys():
            if key not in ['tokens', 'utterances']:
                self._raise_validation_exception()

    def validate_yml(self) -> None:
        self._validate_at_least_dynamic_tokens_or_static_tokens_exist()
        self._validate_only_tokens_and_utterances()
        self._validate_tokens()
        self._validate_utterances()
        self._validate_utterance_tokens_in_static_and_dynamic()
