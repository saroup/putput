import random
import unittest
from pathlib import Path
from typing import Callable, Mapping, Tuple, Union # pylint: disable=unused-import

from putput import CombinationOptions, Pipeline


class TestPipeline(unittest.TestCase):

    def setUp(self) -> None:
        self._base_dir = Path(__file__).parent / 'pattern_definitions' / 'valid'

    def test_before_flow_hooks_tokens(self) -> None:
        pattern_definition_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_to_token_patterns = {
            'ARTIST': ((('kanye west', 'the beatles'),),)
        }

        before_flow_hooks = {
            ('START', 'PLAY', 'ARTIST'): (_sample_artist, _sample_play)
        } # type: Mapping[Union[str, Tuple[str, ...]], Tuple[Callable[[Tuple[Tuple[str, ...], ...], Tuple[str, ...]], Tuple[Tuple[Tuple[str, ...], ...], Tuple[str, ...]]], ...]]

        p = Pipeline()
        p.register_hooks(before_flow_hooks, stage='BEFORE_FLOW')
        actual_utterances, actual_tokens_list = zip(*p.flow(pattern_definition_path, dynamic_token_to_token_patterns))
        expected_utterances = ('he will want to listen the beatles', 'she will want to listen the beatles')
        expected_tokens_list = ('[START] [PLAY] [ARTIST]', '[START] [PLAY] [ARTIST]')
        self.assertEqual(actual_utterances, expected_utterances)
        self.assertEqual(actual_tokens_list, expected_tokens_list)

    def test_before_flow_hooks_default(self) -> None:
        pattern_definition_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_to_token_patterns = {
            'ARTIST': ((('kanye west', 'the beatles'),),)
        }

        before_flow_hooks = {
            'DEFAULT': (_sample_artist, _sample_play)
        } # type: Mapping[Union[str, Tuple[str, ...]], Tuple[Callable[[Tuple[Tuple[str, ...], ...], Tuple[str, ...]], Tuple[Tuple[Tuple[str, ...], ...], Tuple[str, ...]]], ...]]

        p = Pipeline()
        p.register_hooks(before_flow_hooks, stage='BEFORE_FLOW')
        actual_utterances, actual_tokens_list = zip(*p.flow(pattern_definition_path, dynamic_token_to_token_patterns))
        expected_utterances = ('he will want to listen the beatles', 'she will want to listen the beatles')
        expected_tokens_list = ('[START] [PLAY] [ARTIST]', '[START] [PLAY] [ARTIST]')
        self.assertEqual(actual_utterances, expected_utterances)
        self.assertEqual(actual_tokens_list, expected_tokens_list)

    def test_before_flow_hooks_tokens_and_default(self) -> None:
        pattern_definition_path = self._base_dir / 'multiple_utterance_patterns.yml'
        dynamic_token_to_token_patterns = {
            'ARTIST': ((('kanye west', 'the beatles'),),)
        }

        before_flow_hooks = {
            ('START', 'PLAY', 'ARTIST'): (_sample_play,),
            'DEFAULT': (_sample_artist,)
        } # type: Mapping[Union[str, Tuple[str, ...]], Tuple[Callable[[Tuple[Tuple[str, ...], ...], Tuple[str, ...]], Tuple[Tuple[Tuple[str, ...], ...], Tuple[str, ...]]], ...]]

        p = Pipeline()
        p.register_hooks(before_flow_hooks, stage='BEFORE_FLOW')
        actual_utterances, actual_tokens_list = zip(*p.flow(pattern_definition_path, dynamic_token_to_token_patterns))
        expected_utterances = ('he will want to listen kanye west', 'he will want to listen the beatles',
                               'she will want to listen kanye west', 'she will want to listen the beatles',
                               'the beatles')
        expected_tokens_list = ('[START] [PLAY] [ARTIST]', '[START] [PLAY] [ARTIST]',
                                '[START] [PLAY] [ARTIST]', '[START] [PLAY] [ARTIST]',
                                '[ARTIST]')
        self.assertEqual(actual_utterances, expected_utterances)
        self.assertEqual(actual_tokens_list, expected_tokens_list)

    def test_after_flow_hooks_tokens(self) -> None:
        pattern_definition_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_to_token_patterns = {
            'ARTIST': ((('the beatles',),),)
        }

        after_flow_hooks = {
            ('START', 'PLAY', 'ARTIST') : (_add_random_words,)
        } # type: Mapping[Union[str, Tuple[str, ...]], Tuple[Callable[[str, str], Tuple[str, str]], ...]]

        p = Pipeline()
        p.register_hooks(after_flow_hooks, stage='AFTER_FLOW')
        actual_utterances, actual_tokens_list = zip(*p.flow(pattern_definition_path, dynamic_token_to_token_patterns))
        expected_utterances = ('he will want to play the please beatles', 'he will want to listen the please beatles',
                               'she will want to play the please beatles', 'she will want to listen the please beatles')
        expected_tokens_list = ('[START] [PLAY] [ARTIST]', '[START] [PLAY] [ARTIST]',
                                '[START] [PLAY] [ARTIST]', '[START] [PLAY] [ARTIST]')
        self.assertEqual(actual_utterances, expected_utterances)
        self.assertEqual(actual_tokens_list, expected_tokens_list)

    def test_after_flow_hooks_default(self) -> None:
        pattern_definition_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_to_token_patterns = {
            'ARTIST': ((('the beatles',),),)
        }

        after_flow_hooks = {
            'DEFAULT' : (_add_random_words,)
        } # type: Mapping[Union[str, Tuple[str, ...]], Tuple[Callable[[str, str], Tuple[str, str]], ...]]

        p = Pipeline()
        p.register_hooks(after_flow_hooks, stage='AFTER_FLOW')
        actual_utterances, actual_tokens_list = zip(*p.flow(pattern_definition_path, dynamic_token_to_token_patterns))
        expected_utterances = ('he will want to play the please beatles', 'he will want to listen the please beatles',
                               'she will want to play the please beatles', 'she will want to listen the please beatles')
        expected_tokens_list = ('[START] [PLAY] [ARTIST]', '[START] [PLAY] [ARTIST]',
                                '[START] [PLAY] [ARTIST]', '[START] [PLAY] [ARTIST]')
        self.assertEqual(actual_utterances, expected_utterances)
        self.assertEqual(actual_tokens_list, expected_tokens_list)

    def test_after_flow_hooks_tokens_and_default(self) -> None:
        pattern_definition_path = self._base_dir / 'multiple_utterance_patterns.yml'
        dynamic_token_to_token_patterns = {
            'ARTIST': ((('the beatles',),),)
        }

        after_flow_hooks = {
            ('START', 'PLAY', 'ARTIST') : (_add_random_words,),
            'DEFAULT' : (_lowercase_handled_tokens,)
        } # type: Mapping[Union[str, Tuple[str, ...]], Tuple[Callable[[str, str], Tuple[str, str]], ...]]

        p = Pipeline()
        p.register_hooks(after_flow_hooks, stage='AFTER_FLOW')
        actual_utterances, actual_tokens_list = zip(*p.flow(pattern_definition_path, dynamic_token_to_token_patterns))
        expected_utterances = ('he will want to play the please beatles', 'he will want to listen the please beatles',
                               'she will want to play the please beatles', 'she will want to listen the please beatles',
                               'the beatles')
        expected_tokens_list = ('[START] [PLAY] [ARTIST]', '[START] [PLAY] [ARTIST]',
                                '[START] [PLAY] [ARTIST]', '[START] [PLAY] [ARTIST]',
                                '[artist]')
        self.assertEqual(actual_utterances, expected_utterances)
        self.assertEqual(actual_tokens_list, expected_tokens_list)

    def test_token_handlers_token(self) -> None:
        pattern_definition_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_to_token_patterns = {
            'ARTIST': ((('the beatles',),),)
        }
        token_to_token_handlers = {
            'START': _include_phrase,
        }
        p = Pipeline()
        actual_utterances, actual_tokens_list = zip(*p.flow(pattern_definition_path, dynamic_token_to_token_patterns, token_to_token_handlers))
        expected_utterances = ('he will want to play the beatles', 'he will want to listen the beatles',
                               'she will want to play the beatles', 'she will want to listen the beatles')
        expected_tokens_list = ('[START(he will want)] [PLAY] [ARTIST]', '[START(he will want)] [PLAY] [ARTIST]',
                                '[START(she will want)] [PLAY] [ARTIST]', '[START(she will want)] [PLAY] [ARTIST]')
        self.assertEqual(actual_utterances, expected_utterances)
        self.assertEqual(actual_tokens_list, expected_tokens_list)

    def test_token_handlers_default(self) -> None:
        pattern_definition_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_to_token_patterns = {
            'ARTIST': ((('the beatles',),),)
        }
        token_to_token_handlers = {
            'DEFAULT': _include_phrase,
        }
        p = Pipeline()
        actual_utterances, actual_tokens_list = zip(*p.flow(pattern_definition_path, dynamic_token_to_token_patterns, token_to_token_handlers))
        expected_utterances = ('he will want to play the beatles', 'he will want to listen the beatles',
                               'she will want to play the beatles', 'she will want to listen the beatles')
        expected_tokens_list = ('[START(he will want)] [PLAY(to play)] [ARTIST(the beatles)]', '[START(he will want)] [PLAY(to listen)] [ARTIST(the beatles)]',
                                '[START(she will want)] [PLAY(to play)] [ARTIST(the beatles)]', '[START(she will want)] [PLAY(to listen)] [ARTIST(the beatles)]')
        self.assertEqual(actual_utterances, expected_utterances)
        self.assertEqual(actual_tokens_list, expected_tokens_list)


    def test_token_handlers_token_and_default(self) -> None:
        pattern_definition_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_to_token_patterns = {
            'ARTIST': ((('the beatles',),),)
        }
        token_to_token_handlers = {
            'START': _include_phrase,
            'DEFAULT': _remove_token,
        }
        p = Pipeline()
        actual_utterances, actual_tokens_list = zip(*p.flow(pattern_definition_path, dynamic_token_to_token_patterns, token_to_token_handlers))
        expected_utterances = ('he will want to play the beatles', 'he will want to listen the beatles',
                               'she will want to play the beatles', 'she will want to listen the beatles')
        expected_tokens_list = ('[START(he will want)] [(to play)] [(the beatles)]', '[START(he will want)] [(to listen)] [(the beatles)]',
                                '[START(she will want)] [(to play)] [(the beatles)]', '[START(she will want)] [(to listen)] [(the beatles)]')
        self.assertEqual(actual_utterances, expected_utterances)
        self.assertEqual(actual_tokens_list, expected_tokens_list)

    def test_combination_options_without_replacement(self) -> None:
        pattern_definition_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_to_token_patterns = {
            'ARTIST': ((('the beatles',),),)
        }
        tokens_to_combination_options = {
            ('START', 'PLAY', 'ARTIST'): CombinationOptions(max_sample_size=5, with_replacement=False, seed=0)
        } # type: Mapping[Union[str, Tuple[str, ...]], CombinationOptions]

        p = Pipeline()
        actual_utterances, actual_tokens_list = zip(*p.flow(pattern_definition_path,
                                                            dynamic_token_to_token_patterns,
                                                            tokens_to_combination_options=tokens_to_combination_options))
        expected_utterances = ('he will want to play the beatles', 'he will want to listen the beatles',
                               'she will want to play the beatles', 'she will want to listen the beatles')
        expected_tokens_list = ('[START] [PLAY] [ARTIST]', '[START] [PLAY] [ARTIST]',
                                '[START] [PLAY] [ARTIST]', '[START] [PLAY] [ARTIST]')
        self.assertEqual(actual_utterances, expected_utterances)
        self.assertEqual(actual_tokens_list, expected_tokens_list)

    def test_combination_options_with_replacement(self) -> None:
        pattern_definition_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_to_token_patterns = {
            'ARTIST': ((('the beatles',),),)
        }
        max_sample_size = 5
        tokens_to_combination_options = {
            ('START', 'PLAY', 'ARTIST'): CombinationOptions(max_sample_size=max_sample_size, with_replacement=True, seed=0)
        } # type: Mapping[Union[str, Tuple[str, ...]], CombinationOptions]

        p = Pipeline()
        actual_utterances, actual_tokens_list = zip(*p.flow(pattern_definition_path,
                                                            dynamic_token_to_token_patterns,
                                                            tokens_to_combination_options=tokens_to_combination_options))
        expected_utterances = ('she will want to listen the beatles', 'she will want to listen the beatles',
                               'she will want to listen the beatles', 'he will want to play the beatles',
                               'he will want to play the beatles')
        expected_tokens_list = ('[START] [PLAY] [ARTIST]', '[START] [PLAY] [ARTIST]',
                                '[START] [PLAY] [ARTIST]', '[START] [PLAY] [ARTIST]',
                                '[START] [PLAY] [ARTIST]')
        self.assertEqual(actual_utterances, expected_utterances)
        self.assertEqual(actual_tokens_list, expected_tokens_list)

    def test_combination_options_default(self) -> None:
        pattern_definition_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_to_token_patterns = {
            'ARTIST': ((('the beatles',),),)
        }
        max_sample_size = 5
        tokens_to_combination_options = {
            'DEFAULT': CombinationOptions(max_sample_size=max_sample_size, with_replacement=True, seed=0)
        } # type: Mapping[Union[str, Tuple[str, ...]], CombinationOptions]

        p = Pipeline()
        actual_utterances, actual_tokens_list = zip(*p.flow(pattern_definition_path,
                                                            dynamic_token_to_token_patterns,
                                                            tokens_to_combination_options=tokens_to_combination_options))
        expected_utterances = ('she will want to listen the beatles', 'she will want to listen the beatles',
                               'she will want to listen the beatles', 'he will want to play the beatles',
                               'he will want to play the beatles')
        expected_tokens_list = ('[START] [PLAY] [ARTIST]', '[START] [PLAY] [ARTIST]',
                                '[START] [PLAY] [ARTIST]', '[START] [PLAY] [ARTIST]',
                                '[START] [PLAY] [ARTIST]')
        self.assertEqual(actual_utterances, expected_utterances)
        self.assertEqual(actual_tokens_list, expected_tokens_list)

    def test_combination_options_tokens_and_default(self) -> None:
        pattern_definition_path = self._base_dir / 'multiple_utterance_patterns.yml'
        dynamic_token_to_token_patterns = {
            'ARTIST': ((('the beatles', 'kanye'),),)
        }
        tokens_to_combination_options = {
            ('ARTIST',): CombinationOptions(max_sample_size=1, with_replacement=True, seed=0),
            'DEFAULT': CombinationOptions(max_sample_size=3, with_replacement=True, seed=0)
        } # type: Mapping[Union[str, Tuple[str, ...]], CombinationOptions]

        p = Pipeline()
        actual_utterances, actual_tokens_list = zip(*p.flow(pattern_definition_path,
                                                            dynamic_token_to_token_patterns,
                                                            tokens_to_combination_options=tokens_to_combination_options))
        expected_utterances = ('she will want to listen the beatles', 'she will want to listen kanye', 'she will want to listen kanye', 'kanye')
        expected_tokens_list = ('[START] [PLAY] [ARTIST]', '[START] [PLAY] [ARTIST]', '[START] [PLAY] [ARTIST]', '[ARTIST]')
        self.assertEqual(actual_utterances, expected_utterances)
        self.assertEqual(actual_tokens_list, expected_tokens_list)


def _include_phrase(token: str, phrase: str) -> str:
    return '[{token}({phrase})]'.format(token=token, phrase=phrase)

def _remove_token(_: str, phrase: str) -> str:
    return '[({phrase})]'.format(phrase=phrase)

def _sample_utterance_combination(utterance_combination: Tuple[Tuple[str, ...], ...],
                                  tokens: Tuple[str, ...],
                                  token_to_sample: str,
                                  sample_size: int,
                                  ) -> Tuple[Tuple[Tuple[str, ...], ...], Tuple[str, ...]]:
    random.seed(0)
    TOKEN_INDEX = tokens.index(token_to_sample)
    utterance_combination_list = list(utterance_combination)
    sampled_combinations = tuple(random.sample(utterance_combination_list.pop(TOKEN_INDEX), sample_size))
    utterance_combination_list.insert(TOKEN_INDEX, sampled_combinations)
    utterance_combination = tuple(utterance_combination_list)
    return utterance_combination, tokens

def _sample_play(utterance_combination: Tuple[Tuple[str, ...], ...],
                 tokens: Tuple[str, ...],
                 ) -> Tuple[Tuple[Tuple[str, ...], ...], Tuple[str, ...]]:
    return _sample_utterance_combination(utterance_combination, tokens, 'PLAY', 1)

def _sample_artist(utterance_combination: Tuple[Tuple[str, ...], ...],
                   tokens: Tuple[str, ...],
                   ) -> Tuple[Tuple[Tuple[str, ...], ...], Tuple[str, ...]]:
    return _sample_utterance_combination(utterance_combination, tokens, 'ARTIST', 1)

def _add_random_words(utterance: str, handled_tokens: str) -> Tuple[str, str]:
    random.seed(0)
    utterances = utterance.split()
    random_words = ['hmmmm', 'uh', 'um', 'please']
    insert_index = random.randint(0, len(utterances))
    random_word = random.choice(random_words)
    utterances.insert(insert_index, random_word)
    utterance = ' '.join(utterances)
    return utterance, handled_tokens

def _lowercase_handled_tokens(utterance: str, handled_tokens: str) -> Tuple[str, str]:
    return utterance, handled_tokens.lower()

if __name__ == '__main__':
    unittest.main()
