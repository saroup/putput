import unittest
from pathlib import Path
from typing import Mapping, Optional, Tuple, Type

from putput.pattern_definition_processor import TokenPattern, generate_utterance_pattern_and_tokens
from putput.pattern_definition_validator import PatternDefinitionValidationError


class TestPatternDefinitionValidator(unittest.TestCase):
    def setUp(self) -> None:
        self._base_dir = Path(__file__).parent / 'pattern_definitions' / 'invalid'

    def _raise_exception(self,
                         input_file_name: str,
                         exception: Type[PatternDefinitionValidationError],
                         dynamic_token_patterns_definition: Optional[Mapping[str, Tuple[TokenPattern, ...]]] = None
                         ) -> None:
        input_file = self._base_dir / input_file_name
        with self.assertRaises(exception) as cm:
            generate_utterance_pattern_and_tokens(input_file, dynamic_token_patterns_definition)
        self.assertIsInstance(cm.exception, exception)

    def test_token_pattern_too_few_lists(self) -> None:
        input_file_name = 'token_pattern_too_few_lists.yml'
        self._raise_exception(input_file_name, PatternDefinitionValidationError)

    def test_token_pattern_too_many_lists(self) -> None:
        input_file_name = 'token_pattern_too_many_lists.yml'
        self._raise_exception(input_file_name, PatternDefinitionValidationError)

    def test_token_pattern_empty_list(self) -> None:
        input_file_name = 'token_pattern_empty_list.yml'
        self._raise_exception(input_file_name, PatternDefinitionValidationError)

    def test_token_pattern_non_list(self) -> None:
        input_file_name = 'token_pattern_non_list.yml'
        self._raise_exception(input_file_name, PatternDefinitionValidationError)

    def test_dynamic_token_list(self) -> None:
        input_file_name = 'dynamic_token_list.yml'
        self._raise_exception(input_file_name, PatternDefinitionValidationError)

    def test_dynamic_token_list_of_lists(self) -> None:
        input_file_name = 'dynamic_token_list_of_lists.yml'
        self._raise_exception(input_file_name, PatternDefinitionValidationError)

    def test_keys_besides_tokens_and_utterances(self) -> None:
        input_file_name = 'keys_besides_tokens_and_utterances.yml'
        self._raise_exception(input_file_name, PatternDefinitionValidationError)

    def test_keys_in_addition_to_tokens_and_utterances(self) -> None:
        input_file_name = 'keys_in_addition_to_tokens_and_utterances.yml'
        self._raise_exception(input_file_name, PatternDefinitionValidationError)

    def test_keys_besides_static_and_dynamic(self) -> None:
        input_file_name = 'keys_besides_static_and_dynamic.yml'
        self._raise_exception(input_file_name, PatternDefinitionValidationError)

    def test_keys_in_addtion_to_static_and_dynamic(self) -> None:
        input_file_name = 'keys_in_addition_to_static_and_dynamic.yml'
        self._raise_exception(input_file_name, PatternDefinitionValidationError)

    def test_token_pattern_in_utterance_not_defined(self) -> None:
        input_file_name = 'token_pattern_in_utterance_not_defined.yml'
        self._raise_exception(input_file_name, PatternDefinitionValidationError)

    def test_dynamic_and_static_tokens_overlap(self) -> None:
        input_file_name = 'dynamic_and_static_tokens_overlap.yml'
        self._raise_exception(input_file_name, PatternDefinitionValidationError)

    def test_malformed_yml(self) -> None:
        input_file_name = 'malformed_yml.yml'
        self._raise_exception(input_file_name, PatternDefinitionValidationError)
