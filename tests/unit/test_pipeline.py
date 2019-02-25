# pylint: disable=too-many-lines
import logging
import random
import unittest
from pathlib import Path
from typing import Sequence
from typing import Tuple

from putput import ComboOptions
from putput import Pipeline
from putput.presets import displaCy
from putput.presets import iob2
from tests.unit.helper_functions import compare_all_pairs


class TestPipeline(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    def setUp(self) -> None:
        self._disable_progress_bar = True
        self.maxDiff = None
        self._base_dir = Path(__file__).parent / 'pattern_definitions' / 'valid'

    def test_before_joining_hooks_tokens(self) -> None:
        pattern_def_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('kanye west', 'the beatles'),),)
        }

        expansion_hooks_map = {
            ('START', 'PLAY', 'ARTIST'): (_sample_artist, _sample_play)
        }

        p = Pipeline(pattern_def_path,
                     expansion_hooks_map=expansion_hooks_map,
                     dynamic_token_patterns_map=dynamic_token_patterns_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('he will want to listen the beatles', 'she will want to listen the beatles')
        expected_tokens_list = (('[START(he will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'))
        expected_groups = (('{None([START(he will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_before_joining_hooks_default(self) -> None:
        pattern_def_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('kanye west', 'the beatles'),),)
        }

        expansion_hooks_map = {
            'DEFAULT': (_sample_artist, _sample_play)
        }

        p = Pipeline(pattern_def_path,
                     expansion_hooks_map=expansion_hooks_map,
                     dynamic_token_patterns_map=dynamic_token_patterns_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('he will want to listen the beatles', 'she will want to listen the beatles')
        expected_tokens_list = (('[START(he will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'))
        expected_groups = (('{None([START(he will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_before_joining_hooks_tokens_and_default(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_utterance_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('kanye west', 'the beatles'),),)
        }

        expansion_hooks_map = {
            ('START', 'PLAY', 'ARTIST'): (_sample_play,),
            'DEFAULT': (_sample_artist,)
        }

        p = Pipeline(pattern_def_path,
                     expansion_hooks_map=expansion_hooks_map,
                     dynamic_token_patterns_map=dynamic_token_patterns_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('he will want to listen kanye west', 'he will want to listen the beatles',
                               'she will want to listen kanye west', 'she will want to listen the beatles',
                               'the beatles')
        expected_tokens_list = (('[START(he will want)]', '[PLAY(to listen)]', '[ARTIST(kanye west)]'),
                                ('[START(he will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to listen)]', '[ARTIST(kanye west)]'),
                                ('[START(she will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[ARTIST(the beatles)]',))
        expected_groups = (('{None([START(he will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(kanye west)])}'),
                           ('{None([START(he will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(kanye west)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([ARTIST(the beatles)])}',))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_final_hook(self) -> None:
        pattern_def_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles',),),)
        }
        p = Pipeline(pattern_def_path,
                     final_hook=lambda x, y, z: (x, y, z),
                     dynamic_token_patterns_map=dynamic_token_patterns_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('he will want to play the beatles', 'he will want to listen the beatles',
                               'she will want to play the beatles', 'she will want to listen the beatles')
        expected_tokens_list = (('[START(he will want)]', '[PLAY(to play)]', '[ARTIST(the beatles)]'),
                                ('[START(he will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to play)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'))
        expected_groups = (('{None([START(he will want)])}', '{None([PLAY(to play)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(he will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to play)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_after_joining_hooks_tokens(self) -> None:
        pattern_def_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles',),),)
        }

        combo_hooks_map = {
            ('START', 'PLAY', 'ARTIST') : (_add_random_words,)
        }

        p = Pipeline(pattern_def_path,
                     combo_hooks_map=combo_hooks_map,
                     dynamic_token_patterns_map=dynamic_token_patterns_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('he will want to play the please beatles', 'he will want to listen the please beatles',
                               'she will want to play the please beatles', 'she will want to listen the please beatles')
        expected_tokens_list = (('[START(he will want)]', '[PLAY(to play)]', '[ARTIST(the beatles)]'),
                                ('[START(he will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to play)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'))
        expected_groups = (('{None([START(he will want)])}', '{None([PLAY(to play)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(he will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to play)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_combo_hooks_tuple_non_str(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        combo_hooks_map = {
            ('START', 'PLAY', 10) : (_add_random_words,)
        }
        with self.assertRaises(ValueError):
            Pipeline(pattern_def_path, combo_hooks_map=combo_hooks_map)

    def test_combo_hooks_non_str(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        combo_hooks_map = {
            10 : (_add_random_words,)
        }
        with self.assertRaises(ValueError):
            Pipeline(pattern_def_path, combo_hooks_map=combo_hooks_map)

    def test_maps_with_utterance_pattern_as_key_expands(self) -> None:
        pattern_def_path = self._base_dir / 'nested_group_tokens_and_ranges.yml'
        expansion_hooks_map = {
            ('WAKE', 'PLAY_PHRASE'): (_group_nonsense,)
        }
        combo_hooks_map = {
            ('WAKE', 'PLAY_PHRASE') : (_add_random_words,)
        }
        combo_options_map = {
            ('WAKE', 'PLAY_PHRASE'): ComboOptions(max_sample_size=2, with_replacement=False, seed=0)
        }

        p = Pipeline(pattern_def_path,
                     expansion_hooks_map=expansion_hooks_map,
                     combo_hooks_map=combo_hooks_map,
                     combo_options_map=combo_options_map)

        keys = (('WAKE', 'START', 'PLAY'),
                ('WAKE', 'START', 'PLAY', 'PLAY'),
                ('WAKE', 'START', 'PLAY', 'PLAY', 'PLAY'),
                ('WAKE', 'START', 'PLAY', 'PLAY', 'PLAY', 'PLAY'))

        pairs = [(keys, p.expansion_hooks_map.keys()), # type: ignore
                 (keys, p.combo_hooks_map.keys()), # type: ignore
                 (keys, p.combo_options_map.keys())] # type: ignore
        compare_all_pairs(self, pairs)


    def test_maps_with_utterance_pattern_as_key_applies(self) -> None:
        # pylint: disable=too-many-locals
        pattern_def_path = self._base_dir / 'nested_group_tokens_and_ranges.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles',),),)
        }

        expansion_hooks_map = {
            ('WAKE', 'PLAY_PHRASE'): (_group_nonsense,)
        }

        combo_hooks_map = {
            ('WAKE', 'PLAY_PHRASE'): (_add_random_words, _add_commas_to_groups)
        }

        combo_options_map = {
            ('WAKE', 'PLAY_PHRASE'): ComboOptions(max_sample_size=1, with_replacement=False, seed=0)
        }

        p = Pipeline(pattern_def_path,
                     combo_options_map=combo_options_map,
                     combo_hooks_map=combo_hooks_map,
                     expansion_hooks_map=expansion_hooks_map,
                     dynamic_token_patterns_map=dynamic_token_patterns_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi she wants please to listen',
                               'hi she wants to listen to please listen',
                               'hi she wants to listen to please listen to play to play',
                               'hi she wants to listen to please listen to play')
        expected_tokens_list = (('[WAKE(hi)]', '[START(she wants)]', '[PLAY(to listen)]'),
                                ('[WAKE(hi)]', '[START(she wants)]', '[PLAY(to listen)]', '[PLAY(to listen)]'),
                                ('[WAKE(hi)]', '[START(she wants)]', '[PLAY(to listen)]', '[PLAY(to listen)]',
                                 '[PLAY(to play)]'),
                                ('[WAKE(hi)]', '[START(she wants)]', '[PLAY(to listen)]', '[PLAY(to listen)]',
                                 '[PLAY(to play)]', '[PLAY(to play)]'))
        expected_groups = (('{nonsense([WAKE(hi)])},', '{PLAY_PHRASE([START(she wants)] [PLAY(to listen)])},'),
                           ('{nonsense([WAKE(hi)])},',
                            '{PLAY_PHRASE([START(she wants)] [PLAY(to listen)] [PLAY(to listen)])},'),
                           ('{nonsense([WAKE(hi)])},',
                            '{PLAY_PHRASE([START(she wants)] [PLAY(to listen)] [PLAY(to listen)] [PLAY(to play)])},'),
                           ('{nonsense([WAKE(hi)])},',
                            '{PLAY_PHRASE([START(she wants)] [PLAY(to listen)] [PLAY(to listen)] \
[PLAY(to play)] [PLAY(to play)])},'))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_after_joining_hooks_default(self) -> None:
        pattern_def_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles',),),)
        }

        combo_hooks_map = {
            'DEFAULT' : (_add_random_words, _add_commas_to_groups)
        }

        p = Pipeline(pattern_def_path,
                     combo_hooks_map=combo_hooks_map,
                     dynamic_token_patterns_map=dynamic_token_patterns_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('he will want to play the please beatles', 'he will want to listen the please beatles',
                               'she will want to play the please beatles', 'she will want to listen the please beatles')
        expected_tokens_list = (('[START(he will want)]', '[PLAY(to play)]', '[ARTIST(the beatles)]'),
                                ('[START(he will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to play)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'))
        expected_groups = (('{None([START(he will want)])},', '{None([PLAY(to play)])},',
                            '{None([ARTIST(the beatles)])},'),
                           ('{None([START(he will want)])},', '{None([PLAY(to listen)])},',
                            '{None([ARTIST(the beatles)])},'),
                           ('{None([START(she will want)])},', '{None([PLAY(to play)])},',
                            '{None([ARTIST(the beatles)])},'),
                           ('{None([START(she will want)])},', '{None([PLAY(to listen)])},',
                            '{None([ARTIST(the beatles)])},'))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_after_joining_hooks_tokens_and_default(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_utterance_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles',),),)
        }

        combo_hooks_map = {
            ('START', 'PLAY', 'ARTIST') : (_add_random_words,),
            'DEFAULT' : (_lowercase_handled_tokens,)
        }

        p = Pipeline(pattern_def_path,
                     combo_hooks_map=combo_hooks_map,
                     dynamic_token_patterns_map=dynamic_token_patterns_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('he will want to play the please beatles', 'he will want to listen the please beatles',
                               'she will want to play the please beatles', 'she will want to listen the please beatles',
                               'the beatles')
        expected_tokens_list = (('[START(he will want)]', '[PLAY(to play)]', '[ARTIST(the beatles)]'),
                                ('[START(he will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to play)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[artist(the beatles)]',))
        expected_groups = (('{None([START(he will want)])}', '{None([PLAY(to play)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(he will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to play)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([ARTIST(the beatles)])}',))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_token_handlers_token(self) -> None:
        pattern_def_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles',),),)
        }
        token_handler_map = {
            'START': _just_tokens,
        }
        p = Pipeline(pattern_def_path,
                     token_handler_map=token_handler_map,
                     dynamic_token_patterns_map=dynamic_token_patterns_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('he will want to play the beatles', 'he will want to listen the beatles',
                               'she will want to play the beatles', 'she will want to listen the beatles')
        expected_tokens_list = (('[START]', '[PLAY(to play)]', '[ARTIST(the beatles)]'),
                                ('[START]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[START]', '[PLAY(to play)]', '[ARTIST(the beatles)]'),
                                ('[START]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'))
        expected_groups = (('{None([START])}', '{None([PLAY(to play)])}', '{None([ARTIST(the beatles)])}'),
                           ('{None([START])}', '{None([PLAY(to listen)])}', '{None([ARTIST(the beatles)])}'),
                           ('{None([START])}', '{None([PLAY(to play)])}', '{None([ARTIST(the beatles)])}'),
                           ('{None([START])}', '{None([PLAY(to listen)])}', '{None([ARTIST(the beatles)])}'))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_token_handlers_default(self) -> None:
        pattern_def_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles',),),)
        }
        token_handler_map = {
            'DEFAULT': _just_tokens,
        }
        p = Pipeline(pattern_def_path,
                     token_handler_map=token_handler_map,
                     dynamic_token_patterns_map=dynamic_token_patterns_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('he will want to play the beatles', 'he will want to listen the beatles',
                               'she will want to play the beatles', 'she will want to listen the beatles')
        expected_tokens_list = (('[START]', '[PLAY]', '[ARTIST]'),
                                ('[START]', '[PLAY]', '[ARTIST]'),
                                ('[START]', '[PLAY]', '[ARTIST]'),
                                ('[START]', '[PLAY]', '[ARTIST]'))
        expected_groups = (('{None([START])}', '{None([PLAY])}', '{None([ARTIST])}'),
                           ('{None([START])}', '{None([PLAY])}', '{None([ARTIST])}'),
                           ('{None([START])}', '{None([PLAY])}', '{None([ARTIST])}'),
                           ('{None([START])}', '{None([PLAY])}', '{None([ARTIST])}'))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_token_handlers_token_and_default(self) -> None:
        pattern_def_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles',),),)
        }
        token_handler_map = {
            'START': _just_tokens,
            'DEFAULT': _remove_token,
        }
        p = Pipeline(pattern_def_path,
                     token_handler_map=token_handler_map,
                     dynamic_token_patterns_map=dynamic_token_patterns_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('he will want to play the beatles', 'he will want to listen the beatles',
                               'she will want to play the beatles', 'she will want to listen the beatles')
        expected_tokens_list = (('[START]', '[(to play)]', '[(the beatles)]',),
                                ('[START]', '[(to play)]', '[(the beatles)]',),
                                ('[START]', '[(to listen)]', '[(the beatles)]',),
                                ('[START]', '[(to listen)]', '[(the beatles)]'))
        expected_groups = (('{None([START])}', '{None([(to play)])}', '{None([(the beatles)])}'),
                           ('{None([START])}', '{None([(to listen)])}', '{None([(the beatles)])}'),
                           ('{None([START])}', '{None([(to play)])}', '{None([(the beatles)])}'),
                           ('{None([START])}', '{None([(to listen)])}', '{None([(the beatles)])}'))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_group_handlers_group(self) -> None:
        pattern_def_path = self._base_dir / 'static_and_base_tokens_and_group_tokens.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles',),),)
        }
        group_handler_map = {
            'PLAY_PHRASE': _remove_group,
        }
        p = Pipeline(pattern_def_path,
                     group_handler_map=group_handler_map,
                     dynamic_token_patterns_map=dynamic_token_patterns_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play', 'hi he will want to listen',
                               'hi she will want to play', 'hi she will want to listen')
        expected_tokens_list = (('[WAKE(hi)]', '[START(he will want)]', '[PLAY(to play)]'),
                                ('[WAKE(hi)]', '[START(he will want)]', '[PLAY(to listen)]'),
                                ('[WAKE(hi)]', '[START(she will want)]', '[PLAY(to play)]'),
                                ('[WAKE(hi)]', '[START(she will want)]', '[PLAY(to listen)]'))
        expected_groups = (('{None([WAKE(hi)])}', '{([START(he will want)] [PLAY(to play)])}'),
                           ('{None([WAKE(hi)])}', '{([START(he will want)] [PLAY(to listen)])}'),
                           ('{None([WAKE(hi)])}', '{([START(she will want)] [PLAY(to play)])}'),
                           ('{None([WAKE(hi)])}', '{([START(she will want)] [PLAY(to listen)])}'))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_group_handlers_default(self) -> None:
        pattern_def_path = self._base_dir / 'static_and_base_tokens_and_group_tokens.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles',),),)
        }
        group_handler_map = {
            'DEFAULT': _just_groups,
        }
        p = Pipeline(pattern_def_path,
                     group_handler_map=group_handler_map,
                     dynamic_token_patterns_map=dynamic_token_patterns_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play', 'hi he will want to listen',
                               'hi she will want to play', 'hi she will want to listen')
        expected_tokens_list = (('[WAKE(hi)]', '[START(he will want)]', '[PLAY(to play)]'),
                                ('[WAKE(hi)]', '[START(he will want)]', '[PLAY(to listen)]'),
                                ('[WAKE(hi)]', '[START(she will want)]', '[PLAY(to play)]'),
                                ('[WAKE(hi)]', '[START(she will want)]', '[PLAY(to listen)]'))
        expected_groups = (('[None]', '[PLAY_PHRASE]'),
                           ('[None]', '[PLAY_PHRASE]'),
                           ('[None]', '[PLAY_PHRASE]'),
                           ('[None]', '[PLAY_PHRASE]'))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_group_handlers_group_and_default(self) -> None:
        pattern_def_path = self._base_dir / 'static_and_base_tokens_and_group_tokens.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles',),),)
        }
        group_handler_map = {
            'None': _remove_group,
            'DEFAULT': _just_groups,
        }
        p = Pipeline(pattern_def_path,
                     group_handler_map=group_handler_map,
                     dynamic_token_patterns_map=dynamic_token_patterns_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play', 'hi he will want to listen',
                               'hi she will want to play', 'hi she will want to listen')
        expected_tokens_list = (('[WAKE(hi)]', '[START(he will want)]', '[PLAY(to play)]'),
                                ('[WAKE(hi)]', '[START(he will want)]', '[PLAY(to listen)]'),
                                ('[WAKE(hi)]', '[START(she will want)]', '[PLAY(to play)]'),
                                ('[WAKE(hi)]', '[START(she will want)]', '[PLAY(to listen)]'))
        expected_groups = (('{([WAKE(hi)])}', '[PLAY_PHRASE]'),
                           ('{([WAKE(hi)])}', '[PLAY_PHRASE]'),
                           ('{([WAKE(hi)])}', '[PLAY_PHRASE]'),
                           ('{([WAKE(hi)])}', '[PLAY_PHRASE]'))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_combo_options_without_replacement(self) -> None:
        pattern_def_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles',),),)
        }
        combo_options_map = {
            ('START', 'PLAY', 'ARTIST'): ComboOptions(max_sample_size=5, with_replacement=False, seed=0)
        }

        p = Pipeline(pattern_def_path,
                     dynamic_token_patterns_map=dynamic_token_patterns_map,
                     combo_options_map=combo_options_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('he will want to play the beatles', 'he will want to listen the beatles',
                               'she will want to play the beatles', 'she will want to listen the beatles')
        expected_tokens_list = (('[START(she will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[START(he will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[START(he will want)]', '[PLAY(to play)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to play)]', '[ARTIST(the beatles)]'))
        expected_groups = (('{None([START(she will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(he will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(he will want)])}', '{None([PLAY(to play)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to play)])}',
                            '{None([ARTIST(the beatles)])}'))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_combo_options_with_replacement(self) -> None:
        pattern_def_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles',),),)
        }
        max_sample_size = 5
        combo_options_map = {
            ('START', 'PLAY', 'ARTIST'): ComboOptions(max_sample_size=max_sample_size,
                                                      with_replacement=True,
                                                      seed=0)
        }

        p = Pipeline(pattern_def_path,
                     dynamic_token_patterns_map=dynamic_token_patterns_map,
                     combo_options_map=combo_options_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('she will want to listen the beatles', 'she will want to listen the beatles',
                               'he will want to play the beatles', 'she will want to play the beatles',
                               'she will want to listen the beatles')
        expected_tokens_list = (('[START(she will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[START(he will want)]', '[PLAY(to play)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to play)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'))
        expected_groups = (('{None([START(she will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(he will want)])}', '{None([PLAY(to play)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to play)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_combo_options_default(self) -> None:
        pattern_def_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles',),),)
        }
        max_sample_size = 5
        combo_options_map = {
            'DEFAULT': ComboOptions(max_sample_size=max_sample_size, with_replacement=True, seed=0)
        }

        p = Pipeline(pattern_def_path,
                     dynamic_token_patterns_map=dynamic_token_patterns_map,
                     combo_options_map=combo_options_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('she will want to listen the beatles',
                               'she will want to listen the beatles',
                               'he will want to play the beatles',
                               'she will want to play the beatles',
                               'she will want to listen the beatles')
        expected_tokens_list = (('[START(she will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[START(he will want)]', '[PLAY(to play)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to play)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'))
        expected_groups = (('{None([START(she will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(he will want)])}', '{None([PLAY(to play)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to play)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_combo_options_tokens_and_default(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_utterance_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles', 'kanye'),),)
        }
        combo_options_map = {
            ('ARTIST',): ComboOptions(max_sample_size=1, with_replacement=True, seed=0),
            'DEFAULT': ComboOptions(max_sample_size=3, with_replacement=True, seed=0)
        }

        p = Pipeline(pattern_def_path,
                     dynamic_token_patterns_map=dynamic_token_patterns_map,
                     combo_options_map=combo_options_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('she will want to listen the beatles', 'she will want to listen the beatles',
                               'he will want to play the beatles', 'kanye')
        expected_tokens_list = (('[START(she will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[START(he will want)]', '[PLAY(to play)]', '[ARTIST(the beatles)]'),
                                ('[ARTIST(kanye)]',))
        expected_groups = (('{None([START(she will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(he will want)])}', '{None([PLAY(to play)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([ARTIST(kanye)])}',))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_iob2_preset_tokens_to_include(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        p = Pipeline.from_preset(iob2.preset(tokens_to_include=('WAKE',)), pattern_def_path)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play',
                               'hi he will want to listen',
                               'hi she will want to play',
                               'hi she will want to listen',
                               'hi')
        expected_tokens_list = (('B-WAKE', 'O O O', 'O O'),
                                ('B-WAKE', 'O O O', 'O O'),
                                ('B-WAKE', 'O O O', 'O O'),
                                ('B-WAKE', 'O O O', 'O O'),
                                ('B-WAKE',))
        expected_groups = (('B-None', 'B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE'),
                           ('B-None', 'B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE'),
                           ('B-None', 'B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE'),
                           ('B-None', 'B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE'),
                           ('B-None',))
        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_iob2_preset_tokens_to_exclude(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        p = Pipeline.from_preset(iob2.preset(tokens_to_exclude=('WAKE',)), pattern_def_path)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play',
                               'hi he will want to listen',
                               'hi she will want to play',
                               'hi she will want to listen',
                               'hi')
        expected_tokens_list = (('O', 'B-START I-START I-START', 'B-PLAY I-PLAY'),
                                ('O', 'B-START I-START I-START', 'B-PLAY I-PLAY'),
                                ('O', 'B-START I-START I-START', 'B-PLAY I-PLAY'),
                                ('O', 'B-START I-START I-START', 'B-PLAY I-PLAY'),
                                ('O',))
        expected_groups = (('B-None', 'B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE'),
                           ('B-None', 'B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE'),
                           ('B-None', 'B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE'),
                           ('B-None', 'B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE'),
                           ('B-None',))
        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_iob2_preset_tokens_to_include_and_tokens_to_exclude(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        with self.assertRaises(ValueError):
            Pipeline.from_preset(iob2.preset(tokens_to_include=('WAKE',),
                                             tokens_to_exclude=('PLAY',)),
                                 pattern_def_path)

    def test_iob2_preset_groups_to_include_and_groups_to_exclude(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        with self.assertRaises(ValueError):
            Pipeline.from_preset(iob2.preset(groups_to_include=('PLAY_SONG',),
                                             groups_to_exclude=('PLAY_ARTIST',)),
                                 pattern_def_path)

    def test_preset_str_invalid(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        with self.assertRaises(ValueError):
            Pipeline.from_preset('INVALID', pattern_def_path)

    def test_iob2_preset_groups_to_include(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        p = Pipeline.from_preset(iob2.preset(groups_to_include=('PLAY_PHRASE',)), pattern_def_path)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play',
                               'hi he will want to listen',
                               'hi she will want to play',
                               'hi she will want to listen',
                               'hi')
        expected_tokens_list = (('B-WAKE', 'B-START I-START I-START', 'B-PLAY I-PLAY'),
                                ('B-WAKE', 'B-START I-START I-START', 'B-PLAY I-PLAY'),
                                ('B-WAKE', 'B-START I-START I-START', 'B-PLAY I-PLAY'),
                                ('B-WAKE', 'B-START I-START I-START', 'B-PLAY I-PLAY'),
                                ('B-WAKE',))
        expected_groups = (('O', 'B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE'),
                           ('O', 'B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE'),
                           ('O', 'B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE'),
                           ('O', 'B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE'),
                           ('O',))
        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_iob2_preset_groups_to_exclude(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        p = Pipeline.from_preset(iob2.preset(groups_to_exclude=('PLAY_PHRASE',)), pattern_def_path)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play',
                               'hi he will want to listen',
                               'hi she will want to play',
                               'hi she will want to listen',
                               'hi')
        expected_tokens_list = (('B-WAKE', 'B-START I-START I-START', 'B-PLAY I-PLAY'),
                                ('B-WAKE', 'B-START I-START I-START', 'B-PLAY I-PLAY'),
                                ('B-WAKE', 'B-START I-START I-START', 'B-PLAY I-PLAY'),
                                ('B-WAKE', 'B-START I-START I-START', 'B-PLAY I-PLAY'),
                                ('B-WAKE',))
        expected_groups = (('B-None', 'O O O O O'),
                           ('B-None', 'O O O O O'),
                           ('B-None', 'O O O O O'),
                           ('B-None', 'O O O O O'),
                           ('B-None',))
        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_iob2_str_preset(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        p = Pipeline.from_preset('IOB2', pattern_def_path)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play',
                               'hi he will want to listen',
                               'hi she will want to play',
                               'hi she will want to listen',
                               'hi')
        expected_tokens_list = (('B-WAKE', 'B-START I-START I-START', 'B-PLAY I-PLAY'),
                                ('B-WAKE', 'B-START I-START I-START', 'B-PLAY I-PLAY'),
                                ('B-WAKE', 'B-START I-START I-START', 'B-PLAY I-PLAY'),
                                ('B-WAKE', 'B-START I-START I-START', 'B-PLAY I-PLAY'),
                                ('B-WAKE',))
        expected_groups = (('B-None', 'B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE'),
                           ('B-None', 'B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE'),
                           ('B-None', 'B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE'),
                           ('B-None', 'B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE'),
                           ('B-None',))
        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_displaCy_func_preset(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        p = Pipeline.from_preset(displaCy.preset(), pattern_def_path)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_tokens_visualizer, actual_groups_visualizer = zip(*generator)
        exp_tokens_visualizer = ({'text': 'hi he will want to play',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'WAKE'},
                                           {'start': 3, 'end': 15, 'label': 'START'},
                                           {'start': 16, 'end': 23, 'label': 'PLAY'}],
                                  'title': 'Tokens'},
                                 {'text': 'hi he will want to listen',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'WAKE'},
                                           {'start': 3, 'end': 15, 'label': 'START'},
                                           {'start': 16, 'end': 25, 'label': 'PLAY'}],
                                  'title': 'Tokens'},
                                 {'text': 'hi she will want to play',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'WAKE'},
                                           {'start': 3, 'end': 16, 'label': 'START'},
                                           {'start': 17, 'end': 24, 'label': 'PLAY'}],
                                  'title': 'Tokens'},
                                 {'text': 'hi she will want to listen',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'WAKE'},
                                           {'start': 3, 'end': 16, 'label': 'START'},
                                           {'start': 17, 'end': 26, 'label': 'PLAY'}],
                                  'title': 'Tokens'},
                                 {'text': 'hi',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'WAKE'}],
                                  'title': 'Tokens'})
        exp_groups_visualizer = ({'text': 'hi he will want to play',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'None'},
                                           {'start': 3, 'end': 23, 'label': 'PLAY_PHRASE'}],
                                  'title': 'Groups'},
                                 {'text': 'hi he will want to listen',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'None'},
                                           {'start': 3, 'end': 25, 'label': 'PLAY_PHRASE'}],
                                  'title': 'Groups'},
                                 {'text': 'hi she will want to play',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'None'},
                                           {'start': 3, 'end': 24, 'label': 'PLAY_PHRASE'}],
                                  'title': 'Groups'},
                                 {'text': 'hi she will want to listen',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'None'},
                                           {'start': 3, 'end': 26, 'label': 'PLAY_PHRASE'}],
                                  'title': 'Groups'},
                                 {'text': 'hi',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'None'}],
                                  'title': 'Groups'})
        pairs = [(actual_tokens_visualizer, exp_tokens_visualizer),
                 (actual_groups_visualizer, exp_groups_visualizer)]
        compare_all_pairs(self, pairs)

    def test_displaCy_str_preset(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        p = Pipeline.from_preset('DISPLACY', pattern_def_path)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_tokens_visualizer, actual_groups_visualizer = zip(*generator)
        exp_tokens_visualizer = ({'text': 'hi he will want to play',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'WAKE'},
                                           {'start': 3, 'end': 15, 'label': 'START'},
                                           {'start': 16, 'end': 23, 'label': 'PLAY'}],
                                  'title': 'Tokens'},
                                 {'text': 'hi he will want to listen',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'WAKE'},
                                           {'start': 3, 'end': 15, 'label': 'START'},
                                           {'start': 16, 'end': 25, 'label': 'PLAY'}],
                                  'title': 'Tokens'},
                                 {'text': 'hi she will want to play',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'WAKE'},
                                           {'start': 3, 'end': 16, 'label': 'START'},
                                           {'start': 17, 'end': 24, 'label': 'PLAY'}],
                                  'title': 'Tokens'},
                                 {'text': 'hi she will want to listen',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'WAKE'},
                                           {'start': 3, 'end': 16, 'label': 'START'},
                                           {'start': 17, 'end': 26, 'label': 'PLAY'}],
                                  'title': 'Tokens'},
                                 {'text': 'hi',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'WAKE'}],
                                  'title': 'Tokens'})
        exp_groups_visualizer = ({'text': 'hi he will want to play',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'None'},
                                           {'start': 3, 'end': 23, 'label': 'PLAY_PHRASE'}],
                                  'title': 'Groups'},
                                 {'text': 'hi he will want to listen',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'None'},
                                           {'start': 3, 'end': 25, 'label': 'PLAY_PHRASE'}],
                                  'title': 'Groups'},
                                 {'text': 'hi she will want to play',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'None'},
                                           {'start': 3, 'end': 24, 'label': 'PLAY_PHRASE'}],
                                  'title': 'Groups'},
                                 {'text': 'hi she will want to listen',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'None'},
                                           {'start': 3, 'end': 26, 'label': 'PLAY_PHRASE'}],
                                  'title': 'Groups'},
                                 {'text': 'hi',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'None'}],
                                  'title': 'Groups'})
        pairs = [(actual_tokens_visualizer, exp_tokens_visualizer),
                 (actual_groups_visualizer, exp_groups_visualizer)]
        compare_all_pairs(self, pairs)

    def test_default_logger(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        p = Pipeline.from_preset(iob2.preset(groups_to_exclude=('PLAY_PHRASE',)), pattern_def_path)
        self.assertEqual(p.logger.level, logging.WARNING)

def _just_groups(group_name: str, _: Sequence[str]) -> str:
    return '[{group_name}]'.format(group_name=group_name)

def _remove_group(_: str, handled_tokens: Sequence[str]) -> str:
    return '{{({handled_tokens})}}'.format(handled_tokens=' '.join(handled_tokens))

def _just_tokens(token: str, _: str) -> str:
    return '[{token}]'.format(token=token)

def _remove_token(_: str, phrase: str) -> str:
    return '[({phrase})]'.format(phrase=phrase)

def _sample_utterance_combo(utterance_combo: Sequence[Sequence[str]],
                            tokens: Sequence[str],
                            groups: Sequence[Tuple[str, int]],
                            token_to_sample: str,
                            sample_size: int,
                            ) -> Tuple[Sequence[Sequence[str]], Sequence[str], Sequence[Tuple[str, int]]]:
    random.seed(0)
    TOKEN_INDEX = tokens.index(token_to_sample)
    utterance_combo_list = list(utterance_combo)
    sampled_combos = tuple(random.sample(utterance_combo_list.pop(TOKEN_INDEX), sample_size))
    utterance_combo_list.insert(TOKEN_INDEX, sampled_combos)
    utterance_combo = tuple(utterance_combo_list)
    return utterance_combo, tokens, groups

def _sample_play(utterance_combo: Sequence[Sequence[str]],
                 tokens: Sequence[str],
                 groups: Sequence[Tuple[str, int]]
                 ) -> Tuple[Sequence[Sequence[str]], Sequence[str], Sequence[Tuple[str, int]]]:
    return _sample_utterance_combo(utterance_combo, tokens, groups, 'PLAY', 1)

def _sample_artist(utterance_combo: Sequence[Sequence[str]],
                   tokens: Sequence[str],
                   groups: Sequence[Tuple[str, int]]
                   ) -> Tuple[Sequence[Sequence[str]], Sequence[str], Sequence[Tuple[str, int]]]:
    return _sample_utterance_combo(utterance_combo, tokens, groups, 'ARTIST', 1)

def _group_nonsense(utterance_combo: Sequence[Sequence[str]],
                    tokens: Sequence[str],
                    groups: Sequence[Tuple[str, int]]
                    ) -> Tuple[Sequence[Sequence[str]], Sequence[str], Sequence[Tuple[str, int]]]:
    nonsense_groups = list(groups)
    nonsense_groups[0] = ('nonsense', groups[0][1])
    return utterance_combo, tokens, nonsense_groups

def _add_random_words(utterance: str,
                      handled_tokens: Sequence[str],
                      handled_groups: Sequence[str],
                      ) -> Tuple[str, Sequence[str], Sequence[str]]:
    random.seed(0)
    utterances = utterance.split()
    random_words = ['hmmmm', 'uh', 'um', 'please']
    insert_index = random.randint(0, len(utterances))
    random_word = random.choice(random_words)
    utterances.insert(insert_index, random_word)
    utterance = ' '.join(utterances)
    return utterance, handled_tokens, handled_groups

def _lowercase_handled_tokens(utterance: str,
                              handled_tokens: Sequence[str],
                              handled_groups: Sequence[str]
                              ) -> Tuple[str, Sequence[str], Sequence[str]]:
    return utterance, tuple([handled_token.lower() for handled_token in handled_tokens]), handled_groups

def _lowercase_handled_groups(utterance: str,
                              handled_tokens: Sequence[str],
                              handled_groups: Sequence[str]
                              ) -> Tuple[str, Sequence[str], Sequence[str]]:
    return utterance, handled_tokens, tuple([handled_group.lower() for handled_group in handled_groups])

def _add_commas_to_groups(utterance: str,
                          handled_tokens: Sequence[str],
                          handled_groups: Sequence[str]
                          ) -> Tuple[str, Sequence[str], Sequence[str]]:
    return utterance, handled_tokens, tuple([handled_group + ',' for handled_group in handled_groups])

if __name__ == '__main__':
    unittest.main()
