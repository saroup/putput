import unittest
from pathlib import Path
from typing import Type

from yaml.scanner import ScannerError

from putput.generator import generate_utterance_combinations_and_tokens
from putput.validator import PatternDefinitionValidationError


class TestValidator(unittest.TestCase):
    def setUp(self) -> None:
        self._base_dir = Path(__file__).parent / 'pattern_definitions' / 'invalid'

    def _raise_exception(self,
                         pattern_definition_file_name: str,
                         exception: Type[Exception]
                         ) -> None:
        pattern_definition = self._base_dir / pattern_definition_file_name
        with self.assertRaises(exception) as cm:
            for _ in generate_utterance_combinations_and_tokens(pattern_definition):
                break
        self.assertIsInstance(cm.exception, exception)

    def test_token_pattern_too_few_lists(self) -> None:
        pattern_definition_file_name = 'token_pattern_too_few_lists.yml'
        self._raise_exception(pattern_definition_file_name, PatternDefinitionValidationError)

    def test_token_pattern_too_many_lists(self) -> None:
        pattern_definition_file_name = 'token_pattern_too_many_lists.yml'
        self._raise_exception(pattern_definition_file_name, PatternDefinitionValidationError)

    def test_token_pattern_empty_list(self) -> None:
        pattern_definition_file_name = 'token_pattern_empty_list.yml'
        self._raise_exception(pattern_definition_file_name, PatternDefinitionValidationError)

    def test_token_pattern_non_list(self) -> None:
        pattern_definition_file_name = 'token_pattern_non_list.yml'
        self._raise_exception(pattern_definition_file_name, PatternDefinitionValidationError)

    def test_dynamic_token_list(self) -> None:
        pattern_definition_file_name = 'dynamic_token_list.yml'
        self._raise_exception(pattern_definition_file_name, PatternDefinitionValidationError)

    def test_dynamic_token_list_of_lists(self) -> None:
        pattern_definition_file_name = 'dynamic_token_list_of_lists.yml'
        self._raise_exception(pattern_definition_file_name, PatternDefinitionValidationError)

    def test_keys_besides_tokens_and_utterances(self) -> None:
        pattern_definition_file_name = 'keys_besides_tokens_and_utterances.yml'
        self._raise_exception(pattern_definition_file_name, PatternDefinitionValidationError)

    def test_keys_besides_static_and_dynamic(self) -> None:
        pattern_definition_file_name = 'keys_besides_static_and_dynamic.yml'
        self._raise_exception(pattern_definition_file_name, PatternDefinitionValidationError)

    def test_keys_in_addtion_to_static_and_dynamic(self) -> None:
        pattern_definition_file_name = 'keys_in_addition_to_static_and_dynamic.yml'
        self._raise_exception(pattern_definition_file_name, PatternDefinitionValidationError)

    def test_token_pattern_in_utterance_not_defined(self) -> None:
        pattern_definition_file_name = 'token_pattern_in_utterance_not_defined.yml'
        self._raise_exception(pattern_definition_file_name, PatternDefinitionValidationError)

    def test_dynamic_and_static_tokens_overlap(self) -> None:
        pattern_definition_file_name = 'dynamic_and_static_tokens_overlap.yml'
        self._raise_exception(pattern_definition_file_name, PatternDefinitionValidationError)

    def test_malformed(self) -> None:
        pattern_definition_file_name = 'malformed.yml'
        self._raise_exception(pattern_definition_file_name, ScannerError)

    def test_empty(self) -> None:
        pattern_definition_file_name = 'empty.yml'
        self._raise_exception(pattern_definition_file_name, PatternDefinitionValidationError)

    def test_base_tokens_not_defined(self) -> None:
        pattern_definition_file_name = 'base_tokens_not_defined.yml'
        self._raise_exception(pattern_definition_file_name, PatternDefinitionValidationError)

    def test_base_tokens_as_list(self) -> None:
        pattern_definition_file_name = 'base_tokens_as_list.yml'
        self._raise_exception(pattern_definition_file_name, PatternDefinitionValidationError)

    def test_base_tokens_used_in_utterance_patterns(self) -> None:
        pattern_definition_file_name = 'base_tokens_used_in_utterance_patterns.yml'
        self._raise_exception(pattern_definition_file_name, PatternDefinitionValidationError)

    def test_static_and_base_tokens_overlap(self) -> None:
        pattern_definition_file_name = 'static_and_base_tokens_overlap.yml'
        self._raise_exception(pattern_definition_file_name, PatternDefinitionValidationError)

if __name__ == '__main__':
    unittest.main()
