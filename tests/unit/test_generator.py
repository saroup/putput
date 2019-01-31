import unittest
from pathlib import Path

from putput.generator import (generate_utterances_and_handled_tokens,
                              process_pattern_definition)
from putput.joiner import CombinationOptions


class TestProcessPatternDefinition(unittest.TestCase):
    def setUp(self) -> None:
        self._base_dir = Path(__file__).parent / 'pattern_definitions' / 'valid'

    def test_dynamic_token_patterns_only(self) -> None:
        dynamic_token_to_token_patterns = {'ARTIST': ((('the beatles', 'kanye'),),)}
        input_file = self._base_dir / 'dynamic_token_patterns_only.yml'
        expected_utterance_combination = ((('the beatles', 'kanye'),),)
        expected_tokens = (('ARTIST',),)
        actual_utterance_combination, actual_tokens = zip(*process_pattern_definition(input_file, dynamic_token_to_token_patterns))
        self.assertEqual(actual_utterance_combination, expected_utterance_combination)
        self.assertEqual(actual_tokens, expected_tokens)

    def test_static_token_patterns_only(self) -> None:
        input_file = self._base_dir / 'static_token_patterns_only.yml'
        actual_utterance_combination, actual_tokens = zip(*process_pattern_definition(input_file))
        expected_utterance_combination = ((('he will want', 'she will want'), ('to play', 'to listen')),)
        expected_tokens = (('START', 'PLAY'),)
        self.assertEqual(actual_utterance_combination, expected_utterance_combination)
        self.assertEqual(actual_tokens, expected_tokens)

    def test_dynamic_and_static_token_patterns(self) -> None:
        dynamic_token_to_token_patterns = {'ARTIST': ((('the beatles', 'kanye'),),)}
        input_file = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        actual_utterance_combination, actual_tokens = zip(*process_pattern_definition(input_file, dynamic_token_to_token_patterns))
        expected_utterance_combination = ((('he will want', 'she will want'), ('to play', 'to listen'), ('the beatles', 'kanye')),)
        expected_tokens = (('START', 'PLAY', 'ARTIST'),)
        self.assertEqual(actual_utterance_combination, expected_utterance_combination)
        self.assertEqual(actual_tokens, expected_tokens)

    def test_static_and_base_tokens(self) -> None:
        input_file = self._base_dir / 'static_and_base_tokens.yml'
        print(process_pattern_definition(input_file))
        actual_utterance_combination, actual_tokens = zip(*process_pattern_definition(input_file))
        print(actual_utterance_combination, actual_tokens)
        expected_utterance_combination = ((('he will want', 'she will want'), ('to play', 'to listen')),)
        expected_tokens = (('START', 'PLAY'),)
        self.assertEqual(actual_utterance_combination, expected_utterance_combination)
        self.assertEqual(actual_tokens, expected_tokens)

    def test_keys_in_addition_to_utterance_patterns_token_patterns(self) -> None:
        dynamic_token_to_token_patterns = {'ARTIST': ((('the beatles', 'kanye'),),)}
        input_file = self._base_dir / 'keys_in_addition_to_utterance_patterns_tokens_patterns.yml'
        actual_utterance_combination, actual_tokens = zip(*process_pattern_definition(input_file, dynamic_token_to_token_patterns))
        expected_utterance_combination = ((('he will want', 'she will want'), ('to play', 'to listen'), ('the beatles', 'kanye')),)
        expected_tokens = (('START', 'PLAY', 'ARTIST'),)
        self.assertEqual(actual_utterance_combination, expected_utterance_combination)
        self.assertEqual(actual_tokens, expected_tokens)

class TestGenerateUtterancesAndHandledTokens(unittest.TestCase):

    def test_one_token(self) -> None:
        utterance_combination = (('the beatles', 'kanye'),)
        tokens = ('ARTIST',)
        actual_utterances, actual_handled_tokens = zip(*generate_utterances_and_handled_tokens(utterance_combination, tokens))
        expected_utterances = ('the beatles', 'kanye')
        expected_handled_tokens = ('[ARTIST]', '[ARTIST]')
        self.assertEqual(actual_utterances, expected_utterances)
        self.assertEqual(actual_handled_tokens, expected_handled_tokens)

    def test_multiple_tokens(self) -> None:
        utterance_combination = (('he will want', 'she will want'), ('to play', 'to listen'))
        tokens = ('START', 'PLAY')
        actual_utterances, actual_handled_tokens = zip(*generate_utterances_and_handled_tokens(utterance_combination, tokens))
        expected_utterances = ('he will want to play', 'he will want to listen', 'she will want to play', 'she will want to listen')
        expected_handled_tokens = ('[START] [PLAY]', '[START] [PLAY]', '[START] [PLAY]', '[START] [PLAY]')
        self.assertEqual(actual_utterances, expected_utterances)
        self.assertEqual(actual_handled_tokens, expected_handled_tokens)

    def test_default_token_handler(self) -> None:
        _custom_token_handler = lambda token, tokenized_phrase: '[{}({})]'.format(token, tokenized_phrase)
        utterance_combination = (('he will want', 'she will want'), ('to play', 'to listen'))
        tokens = ('START', 'PLAY')
        token_to_token_handlers = {'DEFAULT': _custom_token_handler}
        actual_utterances, actual_handled_tokens = zip(*generate_utterances_and_handled_tokens(utterance_combination, tokens, token_to_token_handlers))
        expected_utterances = ('he will want to play', 'he will want to listen', 'she will want to play', 'she will want to listen')
        expected_handled_tokens = ('[START(he will want)] [PLAY(to play)]', '[START(he will want)] [PLAY(to listen)]', '[START(she will want)] [PLAY(to play)]', '[START(she will want)] [PLAY(to listen)]')
        self.assertEqual(actual_utterances, expected_utterances)
        self.assertEqual(actual_handled_tokens, expected_handled_tokens)

    def test_token_token_handler(self) -> None:
        _custom_token_handler = lambda token, tokenized_phrase: '[{}({})]'.format(token, tokenized_phrase)
        utterance_combination = (('he will want', 'she will want'), ('to play', 'to listen'))
        tokens = ('START', 'PLAY')
        token_to_token_handlers = {'START': _custom_token_handler}
        actual_utterances, actual_handled_tokens = zip(*generate_utterances_and_handled_tokens(utterance_combination, tokens, token_to_token_handlers))
        expected_utterances = ('he will want to play', 'he will want to listen', 'she will want to play', 'she will want to listen')
        expected_handled_tokens = ('[START(he will want)] [PLAY]', '[START(he will want)] [PLAY]', '[START(she will want)] [PLAY]', '[START(she will want)] [PLAY]')
        self.assertEqual(actual_utterances, expected_utterances)
        self.assertEqual(actual_handled_tokens, expected_handled_tokens)

    def test_token_and_default_token_handler(self) -> None:
        _start_token_handler = lambda token, tokenized_phrase: '[{}({})]'.format(token, tokenized_phrase)
        _default_token_handler = lambda token, tokenized_phrase: '[{}(default)]'.format(token)
        utterance_combination = (('he will want', 'she will want'), ('to play', 'to listen'))
        tokens = ('START', 'PLAY')
        token_to_token_handlers = {'START': _start_token_handler, 'DEFAULT': _default_token_handler}
        actual_utterances, actual_handled_tokens = zip(*generate_utterances_and_handled_tokens(utterance_combination, tokens, token_to_token_handlers))
        expected_utterances = ('he will want to play', 'he will want to listen', 'she will want to play', 'she will want to listen')
        expected_handled_tokens = ('[START(he will want)] [PLAY(default)]', '[START(he will want)] [PLAY(default)]', '[START(she will want)] [PLAY(default)]', '[START(she will want)] [PLAY(default)]')
        self.assertEqual(actual_utterances, expected_utterances)
        self.assertEqual(actual_handled_tokens, expected_handled_tokens)

    def test_combination_options_with_replacement(self) -> None:
        utterance_combination = (('he will want', 'she will want'), ('to play', 'to listen'))
        tokens = ('START', 'PLAY')
        combination_options = CombinationOptions(max_sample_size=6, with_replacement=False, seed=0)
        actual_utterances, actual_handled_tokens = zip(*generate_utterances_and_handled_tokens(utterance_combination, tokens, combination_options=combination_options))
        expected_utterances = ('he will want to play', 'he will want to listen', 'she will want to play', 'she will want to listen')
        expected_handled_tokens = ('[START] [PLAY]', '[START] [PLAY]', '[START] [PLAY]', '[START] [PLAY]')
        self.assertEqual(actual_utterances, expected_utterances)
        self.assertEqual(actual_handled_tokens, expected_handled_tokens)

    def test_combination_options_without_replacement(self) -> None:
        utterance_combination = (('he will want', 'she will want'), ('to play', 'to listen'))
        tokens = ('START', 'PLAY')
        combination_options = CombinationOptions(max_sample_size=6, with_replacement=True, seed=0)
        actual_utterances, actual_handled_tokens = zip(*generate_utterances_and_handled_tokens(utterance_combination, tokens, combination_options=combination_options))
        expected_utterances = ('she will want to listen', 'he will want to listen', 'she will want to listen', 'she will want to listen', 'she will want to play', 'he will want to listen')
        expected_handled_tokens = ('[START] [PLAY]', '[START] [PLAY]', '[START] [PLAY]', '[START] [PLAY]', '[START] [PLAY]', '[START] [PLAY]')
        self.assertEqual(actual_utterances, expected_utterances)
        self.assertEqual(actual_handled_tokens, expected_handled_tokens)

if __name__ == '__main__':
    unittest.main()
