import unittest
from pathlib import Path
from typing import Callable, List, Mapping, Optional, Tuple

from putput.joiner import CombinationOptions
from putput.pattern_definition_processor import TokenPattern, generate_utterance_pattern_and_tokens
from putput.utterance_token_generator import generate_utterances_and_tokens


class TestPatternDefinition(unittest.TestCase):
    def setUp(self) -> None:
        self._base_dir = Path(__file__).parent / 'pattern_definitions'

    def _verify(self,
                pattern_definition_fname: str,
                expected_utterances: List[List[str]],
                expected_tokens_iterable: List[List[str]],
                token_handlers: Optional[Mapping[str, Callable[[str, str], str]]] = None,
                combination_options: Optional[CombinationOptions] = None,
                dynamic_token_patterns_definition: Optional[Mapping[str, Tuple[TokenPattern, ...]]] = None) -> None:
        # pylint: disable=too-many-locals, too-many-arguments
        actual_utterances = [[] for i in range(len(expected_utterances))] # type: List[List[str]]
        actual_tokens_iterable = [[] for i in range(len(expected_tokens_iterable))] # type: List[List[str]]

        pattern_definition_path = self._base_dir / pattern_definition_fname
        input_gen = enumerate(generate_utterance_pattern_and_tokens(pattern_definition_path,
                                                                    dynamic_token_patterns_definition))
        for count, (utterance_pattern, tokens) in input_gen:
            ut_gen = generate_utterances_and_tokens(utterance_pattern,
                                                    tokens,
                                                    combination_options=combination_options,
                                                    token_handlers=token_handlers)
            for utterance, token_str in ut_gen:
                actual_utterances[count].append(utterance)
                actual_tokens_iterable[count].append(token_str)

        for collections in [actual_utterances, actual_tokens_iterable, expected_utterances, expected_tokens_iterable]:
            for collection in collections:
                collection.sort()

        actual_expected_results = [zip(actual_utterances, expected_utterances),
                                   zip(actual_tokens_iterable, expected_tokens_iterable)]
        for results in actual_expected_results:
            for actual_results, expected_results in results:
                for actual_result in actual_results:
                    self.assertIn(actual_result, expected_results)
                if combination_options:
                    self.assertLessEqual(len(actual_results), combination_options.max_sample_size)
                else:
                    self.assertEqual(len(actual_results), len(expected_results))

    def test_static_token_patterns_only(self) -> None:
        expected_utterances = [['hey speaker', 'ok speaker']]
        expected_tokens_iterable = [['[WAKE]'] * 2]
        pattern_definition_fname = 'static_token_patterns_only.yml'
        self._verify(pattern_definition_fname, expected_utterances, expected_tokens_iterable)

    def test_dynamic_token_patterns_only(self) -> None:
        dynamic_token_patterns_definition = {
            'WAKE': ((('hey speaker', 'ok speaker'),),)
        }
        expected_utterances = [['hey speaker', 'ok speaker']]
        expected_tokens_iterable = [['[WAKE]'] * 2]
        pattern_definition_fname = 'dynamic_token_patterns_only.yml'
        self._verify(pattern_definition_fname,
                     expected_utterances,
                     expected_tokens_iterable,
                     dynamic_token_patterns_definition=dynamic_token_patterns_definition)

    def test_multiple_utterance_patterns(self) -> None:
        expected_utterances = [
            [
                'hey speaker he wants to play', 'hey speaker he wants to listen to',
                'hey speaker he needs to play', 'hey speaker he needs to listen to',
                'hey speaker she needs to play', 'hey speaker she needs to listen to',
                'hey speaker she wants to play', 'hey speaker she wants to listen to',
                'hey speaker play', 'hey speaker turn on',
                'ok speaker he wants to play', 'ok speaker he wants to listen to',
                'ok speaker he needs to play', 'ok speaker he needs to listen to',
                'ok speaker she needs to play', 'ok speaker she needs to listen to',
                'ok speaker she wants to play', 'ok speaker she wants to listen to',
                'ok speaker play', 'ok speaker turn on'
            ], [
                'hey speaker', 'ok speaker'
            ]
        ]
        expected_tokens_iterable = [
            ['[WAKE] [PLAY]'] * 20,
            ['[WAKE]'] * 2
        ]

        pattern_definition_fname = 'multiple_utterance_patterns.yml'
        self._verify(pattern_definition_fname, expected_utterances, expected_tokens_iterable)

    def test_static_and_dynamic_token_patterns(self) -> None:
        pass

    def test_custom_token_handlers(self) -> None:
        pass

    def test_combination_options(self) -> None:
        pass

    def test_everything_together(self) -> None:
        pass
