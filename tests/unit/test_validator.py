import unittest
from pathlib import Path
from typing import Type

from yaml.scanner import ScannerError

from putput.pipeline import Pipeline
from putput.validator import PatternDefinitionValidationError


class TestValidator(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    def setUp(self) -> None:
        self._base_dir = Path(__file__).parent / 'pattern_definitions' / 'invalid'

    def _raise_exception(self,
                         pattern_def_file_name: str,
                         exception: Type[Exception]
                         ) -> None:
        pattern_def = self._base_dir / pattern_def_file_name
        with self.assertRaises(exception) as cm:
            Pipeline(pattern_def)
        self.assertIsInstance(cm.exception, exception)

    def test_token_pattern_too_few_lists(self) -> None:
        pattern_def_file_name = 'token_pattern_too_few_lists.yml'
        self._raise_exception(pattern_def_file_name, PatternDefinitionValidationError)

    def test_token_pattern_too_many_lists(self) -> None:
        pattern_def_file_name = 'token_pattern_too_many_lists.yml'
        self._raise_exception(pattern_def_file_name, PatternDefinitionValidationError)

    def test_token_pattern_empty_list(self) -> None:
        pattern_def_file_name = 'token_pattern_empty_list.yml'
        self._raise_exception(pattern_def_file_name, PatternDefinitionValidationError)

    def test_token_pattern_non_list(self) -> None:
        pattern_def_file_name = 'token_pattern_non_list.yml'
        self._raise_exception(pattern_def_file_name, PatternDefinitionValidationError)

    def test_dynamic_token_list(self) -> None:
        pattern_def_file_name = 'dynamic_token_list.yml'
        self._raise_exception(pattern_def_file_name, PatternDefinitionValidationError)

    def test_dynamic_token_list_of_lists(self) -> None:
        pattern_def_file_name = 'dynamic_token_list_of_lists.yml'
        self._raise_exception(pattern_def_file_name, PatternDefinitionValidationError)

    def test_keys_besides_tokens_and_utterances(self) -> None:
        pattern_def_file_name = 'keys_besides_tokens_and_utterances.yml'
        self._raise_exception(pattern_def_file_name, PatternDefinitionValidationError)

    def test_keys_besides_static_and_dynamic(self) -> None:
        pattern_def_file_name = 'keys_besides_static_and_dynamic.yml'
        self._raise_exception(pattern_def_file_name, PatternDefinitionValidationError)

    def test_keys_in_addtion_to_static_and_dynamic(self) -> None:
        pattern_def_file_name = 'keys_in_addition_to_static_and_dynamic.yml'
        self._raise_exception(pattern_def_file_name, PatternDefinitionValidationError)

    def test_token_pattern_in_utterance_not_defined(self) -> None:
        pattern_def_file_name = 'token_pattern_in_utterance_not_defined.yml'
        self._raise_exception(pattern_def_file_name, PatternDefinitionValidationError)

    def test_dynamic_and_static_tokens_overlap(self) -> None:
        pattern_def_file_name = 'dynamic_and_static_tokens_overlap.yml'
        self._raise_exception(pattern_def_file_name, PatternDefinitionValidationError)

    def test_malformed(self) -> None:
        pattern_def_file_name = 'malformed.yml'
        self._raise_exception(pattern_def_file_name, ScannerError)

    def test_empty(self) -> None:
        pattern_def_file_name = 'empty.yml'
        self._raise_exception(pattern_def_file_name, PatternDefinitionValidationError)

    def test_base_tokens_not_defined(self) -> None:
        pattern_def_file_name = 'base_tokens_not_defined.yml'
        self._raise_exception(pattern_def_file_name, PatternDefinitionValidationError)

    def test_base_tokens_as_list(self) -> None:
        pattern_def_file_name = 'base_tokens_as_list.yml'
        self._raise_exception(pattern_def_file_name, PatternDefinitionValidationError)

    def test_base_tokens_used_in_utterance_patterns(self) -> None:
        pattern_def_file_name = 'base_tokens_used_in_utterance_patterns.yml'
        self._raise_exception(pattern_def_file_name, PatternDefinitionValidationError)

    def test_static_and_base_tokens_overlap(self) -> None:
        pattern_def_file_name = 'static_and_base_tokens_overlap.yml'
        self._raise_exception(pattern_def_file_name, PatternDefinitionValidationError)

    def test_group_not_defined(self) -> None:
        input_file_name = 'group_not_defined.yml'
        self._raise_exception(input_file_name, PatternDefinitionValidationError)

    def test_group_as_list(self) -> None:
        input_file_name = 'group_as_list.yml'
        self._raise_exception(input_file_name, PatternDefinitionValidationError)

    def test_groups_and_base_tokens_overlap(self) -> None:
        input_file_name = 'groups_and_base_tokens_overlap.yml'
        self._raise_exception(input_file_name, PatternDefinitionValidationError)

    def test_just_range(self) -> None:
        input_file_name = 'just_range.yml'
        self._raise_exception(input_file_name, PatternDefinitionValidationError)

    def test_no_range_symbol(self) -> None:
        input_file_name = 'no_range_symbol.yml'
        self._raise_exception(input_file_name, PatternDefinitionValidationError)

    def test_range_max_less_than_min(self) -> None:
        input_file_name = 'range_max_less_than_min.yml'
        self._raise_exception(input_file_name, PatternDefinitionValidationError)

    def test_too_many_range_numbers(self) -> None:
        input_file_name = 'too_many_range_numbers.yml'
        self._raise_exception(input_file_name, PatternDefinitionValidationError)

    def test_too_many_ranges(self) -> None:
        input_file_name = 'too_many_ranges.yml'
        self._raise_exception(input_file_name, PatternDefinitionValidationError)

    def test_reserved_name_in_base_tokens(self) -> None:
        input_file_name = 'reserved_name_in_base_tokens.yml'
        self._raise_exception(input_file_name, PatternDefinitionValidationError)

    def test_reserved_name_in_token_patterns(self) -> None:
        input_file_name = 'reserved_name_in_token_patterns.yml'
        self._raise_exception(input_file_name, PatternDefinitionValidationError)

    def test_reserved_name_in_groups(self) -> None:
        input_file_name = 'reserved_name_in_groups.yml'
        self._raise_exception(input_file_name, PatternDefinitionValidationError)

    def test_optional_in_token_patterns(self) -> None:
        input_file_name = 'optional_in_token_patterns.yml'
        self._raise_exception(input_file_name, PatternDefinitionValidationError)

    def test_optional_no_paretheses(self) -> None:
        input_file_name = 'optional_no_paretheses.yml'
        self._raise_exception(input_file_name, ScannerError)

    def test_optional_one_paretheses(self) -> None:
        input_file_name = 'optional_one_paretheses.yml'
        self._raise_exception(input_file_name, PatternDefinitionValidationError)

    def test_optional_pipe_at_end(self) -> None:
        input_file_name = 'optional_pipe_at_end.yml'
        self._raise_exception(input_file_name, PatternDefinitionValidationError)

    def test_optional_too_many_pipes(self) -> None:
        input_file_name = 'optional_too_many_pipes.yml'
        self._raise_exception(input_file_name, PatternDefinitionValidationError)

    def test_optional_in_base_token(self) -> None:
        input_file_name = 'optional_in_base_token.yml'
        self._raise_exception(input_file_name, PatternDefinitionValidationError)

    def test_optional_in_token_pattern_base_token(self) -> None:
        input_file_name = 'optional_in_token_pattern_base_token.yml'
        self._raise_exception(input_file_name, PatternDefinitionValidationError)

    def test_single_range(self) -> None:
        # pylint: disable=no-self-use
        pattern_def = Path(__file__).parent / 'pattern_definitions' / 'valid' / 'groups_with_single_range.yml'
        Pipeline(pattern_def)

if __name__ == '__main__':
    unittest.main()
