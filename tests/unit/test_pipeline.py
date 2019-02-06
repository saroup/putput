import random
import unittest
from pathlib import Path
from typing import Mapping # pylint: disable=unused-import
from typing import Tuple
from typing import Union # pylint: disable=unused-import

from putput import CombinationOptions
from putput import Pipeline
from putput.types import AFTER_FLOW_HOOKS # pylint: disable=unused-import
from putput.types import BEFORE_FLOW_HOOKS # pylint: disable=unused-import
from putput.types import HANDLED_TOKEN
from putput.types import HANDLED_TOKENS
from putput.types import HASHABLE_TOKENS # pylint: disable=unused-import
from putput.types import TOKEN
from putput.types import TOKEN_PHRASE
from putput.types import TOKENS
from putput.types import UTTERANCE
from putput.types import UTTERANCE_COMBINATION  # pylint: disable=unused-import


class TestPipeline(unittest.TestCase):

    def setUp(self) -> None:
        self._base_dir = Path(__file__).parent / 'pattern_definitions' / 'valid'

    def test_before_flow_hooks_tokens(self) -> None:
        pattern_definition_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('kanye west', 'the beatles'),),)
        }

        before_flow_hooks = {
            ('START', 'PLAY', 'ARTIST'): (_sample_artist, _sample_play)
        } # type: Mapping[Union[TOKEN, HASHABLE_TOKENS], BEFORE_FLOW_HOOKS]

        p = Pipeline()
        p.register_hooks(before_flow_hooks, stage='BEFORE_FLOW')
        actual_utterances, actual_tokens_list = zip(*p.flow(pattern_definition_path, dynamic_token_patterns_map))
        expected_utterances = ('he will want to listen the beatles', 'she will want to listen the beatles')
        expected_tokens_list = ('[START] [PLAY] [ARTIST]', '[START] [PLAY] [ARTIST]')
        self.assertEqual(actual_utterances, expected_utterances)
        self.assertEqual(actual_tokens_list, expected_tokens_list)

    def test_bad_hook_stage_name(self) -> None:
        before_flow_hooks = {
            'DEFAULT': (_sample_artist, _sample_play)
        } # type: Mapping[Union[TOKEN, HASHABLE_TOKENS], BEFORE_FLOW_HOOKS]

        p = Pipeline()
        with self.assertRaises(ValueError) as cm:
            p.register_hooks(before_flow_hooks, stage='BAD_NAME')
        self.assertIsInstance(cm.exception, ValueError)

    def test_before_flow_hooks_default(self) -> None:
        pattern_definition_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('kanye west', 'the beatles'),),)
        }

        before_flow_hooks = {
            'DEFAULT': (_sample_artist, _sample_play)
        } # type: Mapping[Union[TOKEN, HASHABLE_TOKENS], BEFORE_FLOW_HOOKS]

        p = Pipeline()
        p.register_hooks(before_flow_hooks, stage='BEFORE_FLOW')
        actual_utterances, actual_tokens_list = zip(*p.flow(pattern_definition_path, dynamic_token_patterns_map))
        expected_utterances = ('he will want to listen the beatles', 'she will want to listen the beatles')
        expected_tokens_list = ('[START] [PLAY] [ARTIST]', '[START] [PLAY] [ARTIST]')
        self.assertEqual(actual_utterances, expected_utterances)
        self.assertEqual(actual_tokens_list, expected_tokens_list)

    def test_before_flow_hooks_tokens_and_default(self) -> None:
        pattern_definition_path = self._base_dir / 'multiple_utterance_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('kanye west', 'the beatles'),),)
        }

        before_flow_hooks = {
            ('START', 'PLAY', 'ARTIST'): (_sample_play,),
            'DEFAULT': (_sample_artist,)
        } # type: Mapping[Union[TOKEN, HASHABLE_TOKENS], BEFORE_FLOW_HOOKS]

        p = Pipeline()
        p.register_hooks(before_flow_hooks, stage='BEFORE_FLOW')
        actual_utterances, actual_tokens_list = zip(*p.flow(pattern_definition_path, dynamic_token_patterns_map))
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
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles',),),)
        }

        after_flow_hooks = {
            ('START', 'PLAY', 'ARTIST') : (_add_random_words,)
        } # type: Mapping[Union[TOKEN, HASHABLE_TOKENS], AFTER_FLOW_HOOKS]

        p = Pipeline()
        p.register_hooks(after_flow_hooks, stage='AFTER_FLOW')
        actual_utterances, actual_tokens_list = zip(*p.flow(pattern_definition_path, dynamic_token_patterns_map))
        expected_utterances = ('he will want to play the please beatles', 'he will want to listen the please beatles',
                               'she will want to play the please beatles', 'she will want to listen the please beatles')
        expected_tokens_list = ('[START] [PLAY] [ARTIST]', '[START] [PLAY] [ARTIST]',
                                '[START] [PLAY] [ARTIST]', '[START] [PLAY] [ARTIST]')
        self.assertEqual(actual_utterances, expected_utterances)
        self.assertEqual(actual_tokens_list, expected_tokens_list)

    def test_after_flow_hooks_default(self) -> None:
        pattern_definition_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles',),),)
        }

        after_flow_hooks = {
            'DEFAULT' : (_add_random_words,)
        } # type: Mapping[Union[TOKEN, HASHABLE_TOKENS], AFTER_FLOW_HOOKS]

        p = Pipeline()
        p.register_hooks(after_flow_hooks, stage='AFTER_FLOW')
        actual_utterances, actual_tokens_list = zip(*p.flow(pattern_definition_path, dynamic_token_patterns_map))
        expected_utterances = ('he will want to play the please beatles', 'he will want to listen the please beatles',
                               'she will want to play the please beatles', 'she will want to listen the please beatles')
        expected_tokens_list = ('[START] [PLAY] [ARTIST]', '[START] [PLAY] [ARTIST]',
                                '[START] [PLAY] [ARTIST]', '[START] [PLAY] [ARTIST]')
        self.assertEqual(actual_utterances, expected_utterances)
        self.assertEqual(actual_tokens_list, expected_tokens_list)

    def test_after_flow_hooks_tokens_and_default(self) -> None:
        pattern_definition_path = self._base_dir / 'multiple_utterance_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles',),),)
        }

        after_flow_hooks = {
            ('START', 'PLAY', 'ARTIST') : (_add_random_words,),
            'DEFAULT' : (_lowercase_handled_tokens,)
        } # type: Mapping[Union[TOKEN, HASHABLE_TOKENS], AFTER_FLOW_HOOKS]

        p = Pipeline()
        p.register_hooks(after_flow_hooks, stage='AFTER_FLOW')
        actual_utterances, actual_tokens_list = zip(*p.flow(pattern_definition_path, dynamic_token_patterns_map))
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
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles',),),)
        }
        token_handler_map = {
            'START': _include_phrase,
        }
        p = Pipeline()
        actual_utterances, actual_tokens_list = zip(*p.flow(pattern_definition_path,
                                                            dynamic_token_patterns_map,
                                                            token_handler_map))
        expected_utterances = ('he will want to play the beatles', 'he will want to listen the beatles',
                               'she will want to play the beatles', 'she will want to listen the beatles')
        expected_tokens_list = ('[START(he will want)] [PLAY] [ARTIST]', '[START(he will want)] [PLAY] [ARTIST]',
                                '[START(she will want)] [PLAY] [ARTIST]', '[START(she will want)] [PLAY] [ARTIST]')
        self.assertEqual(actual_utterances, expected_utterances)
        self.assertEqual(actual_tokens_list, expected_tokens_list)

    def test_token_handlers_default(self) -> None:
        pattern_definition_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles',),),)
        }
        token_handler_map = {
            'DEFAULT': _include_phrase,
        }
        p = Pipeline()
        actual_utterances, actual_tokens_list = zip(*p.flow(pattern_definition_path,
                                                            dynamic_token_patterns_map,
                                                            token_handler_map))
        expected_utterances = ('he will want to play the beatles', 'he will want to listen the beatles',
                               'she will want to play the beatles', 'she will want to listen the beatles')
        expected_tokens_list = ('[START(he will want)] [PLAY(to play)] [ARTIST(the beatles)]',
                                '[START(he will want)] [PLAY(to listen)] [ARTIST(the beatles)]',
                                '[START(she will want)] [PLAY(to play)] [ARTIST(the beatles)]',
                                '[START(she will want)] [PLAY(to listen)] [ARTIST(the beatles)]')
        self.assertEqual(actual_utterances, expected_utterances)
        self.assertEqual(actual_tokens_list, expected_tokens_list)


    def test_token_handlers_token_and_default(self) -> None:
        pattern_definition_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles',),),)
        }
        token_handler_map = {
            'START': _include_phrase,
            'DEFAULT': _remove_token,
        }
        p = Pipeline()
        actual_utterances, actual_tokens_list = zip(*p.flow(pattern_definition_path,
                                                            dynamic_token_patterns_map,
                                                            token_handler_map))
        expected_utterances = ('he will want to play the beatles', 'he will want to listen the beatles',
                               'she will want to play the beatles', 'she will want to listen the beatles')
        expected_tokens_list = ('[START(he will want)] [(to play)] [(the beatles)]',
                                '[START(he will want)] [(to listen)] [(the beatles)]',
                                '[START(she will want)] [(to play)] [(the beatles)]',
                                '[START(she will want)] [(to listen)] [(the beatles)]')
        self.assertEqual(actual_utterances, expected_utterances)
        self.assertEqual(actual_tokens_list, expected_tokens_list)

    def test_combination_options_without_replacement(self) -> None:
        pattern_definition_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles',),),)
        }
        combination_options_map = {
            ('START', 'PLAY', 'ARTIST'): CombinationOptions(max_sample_size=5, with_replacement=False, seed=0)
        } # type: Mapping[Union[TOKEN, HASHABLE_TOKENS], CombinationOptions]

        p = Pipeline()
        actual_utterances, actual_tokens_list = zip(*p.flow(pattern_definition_path,
                                                            dynamic_token_patterns_map,
                                                            combination_options_map=combination_options_map))
        expected_utterances = ('he will want to play the beatles', 'he will want to listen the beatles',
                               'she will want to play the beatles', 'she will want to listen the beatles')
        expected_tokens_list = ('[START] [PLAY] [ARTIST]', '[START] [PLAY] [ARTIST]',
                                '[START] [PLAY] [ARTIST]', '[START] [PLAY] [ARTIST]')
        self.assertEqual(actual_utterances, expected_utterances)
        self.assertEqual(actual_tokens_list, expected_tokens_list)

    def test_combination_options_with_replacement(self) -> None:
        pattern_definition_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles',),),)
        }
        max_sample_size = 5
        combination_options_map = {
            ('START', 'PLAY', 'ARTIST'): CombinationOptions(max_sample_size=max_sample_size,
                                                            with_replacement=True,
                                                            seed=0)
        } # type: Mapping[Union[TOKEN, HASHABLE_TOKENS], CombinationOptions]

        p = Pipeline()
        actual_utterances, actual_tokens_list = zip(*p.flow(pattern_definition_path,
                                                            dynamic_token_patterns_map,
                                                            combination_options_map=combination_options_map))
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
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles',),),)
        }
        max_sample_size = 5
        combination_options_map = {
            'DEFAULT': CombinationOptions(max_sample_size=max_sample_size, with_replacement=True, seed=0)
        } # type: Mapping[Union[TOKEN, HASHABLE_TOKENS], CombinationOptions]

        p = Pipeline()
        actual_utterances, actual_tokens_list = zip(*p.flow(pattern_definition_path,
                                                            dynamic_token_patterns_map,
                                                            combination_options_map=combination_options_map))
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
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles', 'kanye'),),)
        }
        combination_options_map = {
            ('ARTIST',): CombinationOptions(max_sample_size=1, with_replacement=True, seed=0),
            'DEFAULT': CombinationOptions(max_sample_size=3, with_replacement=True, seed=0)
        } # type: Mapping[Union[TOKEN, HASHABLE_TOKENS], CombinationOptions]

        p = Pipeline()
        actual_utterances, actual_tokens_list = zip(*p.flow(pattern_definition_path,
                                                            dynamic_token_patterns_map,
                                                            combination_options_map=combination_options_map))
        expected_utterances = ('she will want to listen the beatles', 'she will want to listen kanye',
                               'she will want to listen kanye', 'kanye')
        expected_tokens_list = ('[START] [PLAY] [ARTIST]', '[START] [PLAY] [ARTIST]',
                                '[START] [PLAY] [ARTIST]', '[ARTIST]')
        self.assertEqual(actual_utterances, expected_utterances)
        self.assertEqual(actual_tokens_list, expected_tokens_list)


def _include_phrase(token: TOKEN, phrase: TOKEN_PHRASE) -> HANDLED_TOKEN:
    return '[{token}({phrase})]'.format(token=token, phrase=phrase)

def _remove_token(_: TOKEN, phrase: TOKEN_PHRASE) -> HANDLED_TOKEN:
    return '[({phrase})]'.format(phrase=phrase)

def _sample_utterance_combination(utterance_combination: UTTERANCE_COMBINATION,
                                  tokens: TOKENS,
                                  token_to_sample: str,
                                  sample_size: int,
                                  ) -> Tuple[UTTERANCE_COMBINATION, TOKENS]:
    random.seed(0)
    TOKEN_INDEX = tokens.index(token_to_sample)
    utterance_combination_list = list(utterance_combination)
    sampled_combinations = tuple(random.sample(utterance_combination_list.pop(TOKEN_INDEX), sample_size))
    utterance_combination_list.insert(TOKEN_INDEX, sampled_combinations)
    utterance_combination = tuple(utterance_combination_list)
    return utterance_combination, tokens

def _sample_play(utterance_combination: UTTERANCE_COMBINATION,
                 tokens: TOKENS,
                 ) -> Tuple[UTTERANCE_COMBINATION, TOKENS]:
    return _sample_utterance_combination(utterance_combination, tokens, 'PLAY', 1)

def _sample_artist(utterance_combination: UTTERANCE_COMBINATION,
                   tokens: TOKENS,
                   ) -> Tuple[UTTERANCE_COMBINATION, TOKENS]:
    return _sample_utterance_combination(utterance_combination, tokens, 'ARTIST', 1)

def _add_random_words(utterance: UTTERANCE, handled_tokens: HANDLED_TOKENS) -> Tuple[UTTERANCE, HANDLED_TOKENS]:
    random.seed(0)
    utterances = utterance.split()
    random_words = ['hmmmm', 'uh', 'um', 'please']
    insert_index = random.randint(0, len(utterances))
    random_word = random.choice(random_words)
    utterances.insert(insert_index, random_word)
    utterance = ' '.join(utterances)
    return utterance, handled_tokens

def _lowercase_handled_tokens(utterance: UTTERANCE, handled_tokens: HANDLED_TOKENS) -> Tuple[UTTERANCE, HANDLED_TOKENS]:
    return utterance, handled_tokens.lower()

if __name__ == '__main__':
    unittest.main()
