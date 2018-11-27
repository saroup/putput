import os
import unittest
from typing import List, Mapping, Optional, Type

from putput.input_processor import generate_utterance_pattern_and_tokens
from putput.types import TokenPattern


class TestInputProcessorInvalidInputYml(unittest.TestCase):

    # test that defined dynamic tokens are not passed in to initializer
    def setUp(self) -> None:
        self._base_dir = os.path.join(os.path.join(os.path.dirname(__file__), 'yml_definitions'), 'invalid')

    # TODO: the dynamic_token_patterns_dict should be optional in the input processor
    def _raise_exception(self,
                         input_file_name: str,
                         exception: Type[Exception],
                         dynamic_token_patterns_dict: Optional[Mapping[str, List[TokenPattern]]] = None) -> None:
        input_file = os.path.join(self._base_dir, input_file_name)
        with self.assertRaises(exception) as cm:
            generate_utterance_pattern_and_tokens(input_file, dynamic_token_patterns_dict)
        self.assertIsInstance(cm.exception, exception)

    def test_malformed_yml(self) -> None:
        input_file_name = 'malformed_yml.yml'
        self._raise_exception(input_file_name, Exception)

    def test_token_pattern_too_few_lists(self) -> None:
        input_file_name = 'token_pattern_too_few_lists.yml'
        self._raise_exception(input_file_name, Exception)

    def test_token_pattern_too_many_lists(self) -> None:
        input_file_name = 'token_pattern_too_many_lists.yml'
        self._raise_exception(input_file_name, Exception)

    def test_token_pattern_empty_list(self) -> None:
        input_file_name = 'token_pattern_empty_list.yml'
        self._raise_exception(input_file_name, Exception)

    def test_token_pattern_list_with_non_strings(self) -> None:
        input_file_name = 'token_pattern_list_with_non_strings.yml'
        self._raise_exception(input_file_name, Exception)

    def test_token_pattern_non_list(self) -> None:
        input_file_name = 'token_pattern_non_list.yml'
        self._raise_exception(input_file_name, Exception)

    def test_dynamic_token_list(self) -> None:
        input_file_name = 'dynamic_token_list.yml'
        self._raise_exception(input_file_name, Exception)

    def test_dynamic_token_list_of_lists(self) -> None:
        input_file_name = 'dynamic_token_list_of_lists.yml'
        self._raise_exception(input_file_name, Exception)

    def test_keys_besides_tokens_and_utterances(self) -> None:
        input_file_name = 'keys_besides_tokens_and_utterances.yml'
        self._raise_exception(input_file_name, Exception)

    def test_keys_in_addition_to_tokens_and_utterances(self) -> None:
        input_file_name = 'keys_in_addition_to_tokens_and_utterances.yml'
        self._raise_exception(input_file_name, Exception)

    def test_keys_besides_static_and_dynamic(self) -> None:
        input_file_name = 'keys_besides_static_and_dynamic.yml'
        self._raise_exception(input_file_name, Exception)

    def test_keys_in_addtion_to_static_and_dynamic(self) -> None:
        input_file_name = 'keys_in_addition_to_static_and_dynamic.yml'
        self._raise_exception(input_file_name, Exception)

    def test_token_pattern_in_utterance_not_defined(self) -> None:
        input_file_name = 'token_pattern_in_utterance_not_defined.yml'
        self._raise_exception(input_file_name, Exception)

    def test_dynamic_and_static_tokens_overlap(self) -> None:
        input_file_name = 'dynamic_and_static_tokens_overlap.yml'
        self._raise_exception(input_file_name, Exception)


class TestInputProcessorValidInputYml(unittest.TestCase):
    def setUp(self) -> None:
        self._base_dir = os.path.join(os.path.join(os.path.dirname(__file__), 'yml_definitions'), 'valid')

    def test_without_static_token_patterns(self) -> None:
        dynamic_token_patterns_dict = {"ARTIST": [[["the beatles", "kanye"]]]}
        input_file = os.path.join(self._base_dir, 'without_static_token_patterns.yml')
        actual_result = generate_utterance_pattern_and_tokens(input_file, dynamic_token_patterns_dict)
        expected_result = [([[[['the beatles', 'kanye']]]], ['ARTIST'])]
        # TODO: because of random seeds, this equal should be replaced with in and length
        self.assertEqual(actual_result, expected_result)

    def test_without_dynamic_token_patterns(self) -> None:
        input_file = os.path.join(self._base_dir, 'without_dynamic_token_patterns.yml')
        actual_result = generate_utterance_pattern_and_tokens(input_file, {})
        expected_result = [([[[['he', 'she'], ['will"'], ['want']]], [[['to'], ['play', 'listen']]]], ['START',
                                                                                                       'PLAY'])]
        self.assertEqual(actual_result, expected_result)

    def test_all_options_specified(self) -> None:
        dynamic_token_patterns_dict = {"ARTIST": [[["the beatles", "kanye"]]]}
        input_file = os.path.join(self._base_dir, 'all_options_specified.yml')
        actual_result = generate_utterance_pattern_and_tokens(input_file, dynamic_token_patterns_dict)
        expected_result = [([[[['he', 'she'], ['will"'], ['want']]], [[['to'], ['play', 'listen']]],
                             [[['the beatles', 'kanye']]]], ['START', 'PLAY', 'ARTIST'])]
        self.assertEqual(actual_result, expected_result)


if __name__ == '__main__':
    unittest.main()
