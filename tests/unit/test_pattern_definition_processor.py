import unittest
from pathlib import Path

from putput.pattern_definition_processor import generate_utterance_pattern_and_tokens


class TestPatternDefinitionProcessor(unittest.TestCase):
    def setUp(self) -> None:
        self._base_dir = Path(__file__).parent / 'pattern_definitions' / 'valid'

    def test_dynamic_token_patterns_only(self) -> None:
        dynamic_token_patterns_definition = {'ARTIST': ((('the beatles', 'kanye'),),)}
        input_file = self._base_dir / 'dynamic_token_patterns_only.yml'
        actual_result = generate_utterance_pattern_and_tokens(input_file, dynamic_token_patterns_definition)
        expected_result = [((((('the beatles', 'kanye'),),),), ('ARTIST', ))]
        self.assertEqual(list(actual_result), expected_result)

    def test_static_token_patterns_only(self) -> None:
        input_file = self._base_dir / 'static_token_patterns_only.yml'
        actual_result = generate_utterance_pattern_and_tokens(input_file)
        expected_result = [((((('he', 'she'), ('will',), ('want',)),), ((('to',), ('play', 'listen')),)), ('START',
                                                                                                           'PLAY'))]
        self.assertEqual(list(actual_result), expected_result)

    def test_dynamic_and_static_token_patterns(self) -> None:
        dynamic_token_patterns_definition = {'ARTIST': ((('the beatles', 'kanye'),),)}
        input_file = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        actual_result = generate_utterance_pattern_and_tokens(input_file, dynamic_token_patterns_definition)
        expected_result = [((((('he', 'she'), ('will',), ('want',)),), ((('to',), ('play', 'listen')),),
                             ((('the beatles', 'kanye'),),)), ('START', 'PLAY', 'ARTIST'))]
        self.assertEqual(list(actual_result), expected_result)

if __name__ == '__main__':
    unittest.main()
