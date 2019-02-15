import random
import unittest
from pathlib import Path
from typing import Sequence
from typing import Tuple

from putput import ComboOptions
from putput import Pipeline
from putput.presets import iob2
from putput.types import COMBO
from putput.types import GROUP
from tests.unit.helper_functions import compare_all_pairs


class TestPipeline(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    def setUp(self) -> None:
        self.maxDiff = None
        self._base_dir = Path(__file__).parent / 'pattern_definitions' / 'valid'

    def test_before_joining_hooks_tokens(self) -> None:
        pattern_def_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('kanye west', 'the beatles'),),)
        }

        before_joining_hooks_map = {
            ('START', 'PLAY', 'ARTIST'): (_sample_artist, _sample_play)
        }

        p = Pipeline(before_joining_hooks_map=before_joining_hooks_map)
        generator = p.flow(pattern_def_path, dynamic_token_patterns_map=dynamic_token_patterns_map)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)

        expected_utterances = ('he will want to listen the beatles', 'she will want to listen the beatles')
        expected_tokens_list = ('[START(he will want)] [PLAY(to listen)] [ARTIST(the beatles)]',
                                '[START(she will want)] [PLAY(to listen)] [ARTIST(the beatles)]')
        expected_groups = _generate_no_groups(expected_tokens_list)

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_before_joining_hooks_default(self) -> None:
        pattern_def_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('kanye west', 'the beatles'),),)
        }

        before_joining_hooks_map = {
            'DEFAULT': (_sample_artist, _sample_play)
        }

        p = Pipeline(before_joining_hooks_map=before_joining_hooks_map)
        generator = p.flow(pattern_def_path, dynamic_token_patterns_map=dynamic_token_patterns_map)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('he will want to listen the beatles', 'she will want to listen the beatles')
        expected_tokens_list = ('[START(he will want)] [PLAY(to listen)] [ARTIST(the beatles)]',
                                '[START(she will want)] [PLAY(to listen)] [ARTIST(the beatles)]')
        expected_groups = _generate_no_groups(expected_tokens_list)

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_before_joining_hooks_tokens_and_default(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_utterance_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('kanye west', 'the beatles'),),)
        }

        before_joining_hooks_map = {
            ('START', 'PLAY', 'ARTIST'): (_sample_play,),
            'DEFAULT': (_sample_artist,)
        }

        p = Pipeline(before_joining_hooks_map=before_joining_hooks_map)
        generator = p.flow(pattern_def_path, dynamic_token_patterns_map=dynamic_token_patterns_map)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('he will want to listen kanye west', 'he will want to listen the beatles',
                               'she will want to listen kanye west', 'she will want to listen the beatles',
                               'the beatles')
        expected_tokens_list = ('[START(he will want)] [PLAY(to listen)] [ARTIST(the beatles)]',
                                '[START(she will want)] [PLAY(to listen)] [ARTIST(the beatles)]',
                                '[START(he will want)] [PLAY(to listen)] [ARTIST(kanye west)]',
                                '[START(she will want)] [PLAY(to listen)] [ARTIST(kanye west)]',
                                '[ARTIST(the beatles)]')
        expected_groups = _generate_no_groups(expected_tokens_list)

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_after_joining_hooks_tokens(self) -> None:
        pattern_def_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles',),),)
        }

        after_joining_hooks_map = {
            ('START', 'PLAY', 'ARTIST') : (_add_random_words,)
        }

        p = Pipeline(after_joining_hooks_map=after_joining_hooks_map)
        generator = p.flow(pattern_def_path, dynamic_token_patterns_map=dynamic_token_patterns_map)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('he will want to play the please beatles', 'he will want to listen the please beatles',
                               'she will want to play the please beatles', 'she will want to listen the please beatles')
        expected_tokens_list = ('[START(he will want)] [PLAY(to play)] [ARTIST(the beatles)]',
                                '[START(she will want)] [PLAY(to play)] [ARTIST(the beatles)]',
                                '[START(he will want)] [PLAY(to listen)] [ARTIST(the beatles)]',
                                '[START(she will want)] [PLAY(to listen)] [ARTIST(the beatles)]')
        expected_groups = _generate_no_groups(expected_tokens_list)

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_after_joining_hooks_default(self) -> None:
        pattern_def_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles',),),)
        }

        after_joining_hooks_map = {
            'DEFAULT' : (_add_random_words,)
        }

        p = Pipeline(after_joining_hooks_map=after_joining_hooks_map)
        generator = p.flow(pattern_def_path, dynamic_token_patterns_map=dynamic_token_patterns_map)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('he will want to play the please beatles', 'he will want to listen the please beatles',
                               'she will want to play the please beatles', 'she will want to listen the please beatles')
        expected_tokens_list = ('[START(he will want)] [PLAY(to play)] [ARTIST(the beatles)]',
                                '[START(she will want)] [PLAY(to play)] [ARTIST(the beatles)]',
                                '[START(he will want)] [PLAY(to listen)] [ARTIST(the beatles)]',
                                '[START(she will want)] [PLAY(to listen)] [ARTIST(the beatles)]')
        expected_groups = _generate_no_groups(expected_tokens_list)

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_after_joining_hooks_tokens_and_default(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_utterance_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles',),),)
        }

        after_joining_hooks_map = {
            ('START', 'PLAY', 'ARTIST') : (_add_random_words,),
            'DEFAULT' : (_lowercase_handled_tokens,)
        }

        p = Pipeline(after_joining_hooks_map=after_joining_hooks_map)
        generator = p.flow(pattern_def_path, dynamic_token_patterns_map=dynamic_token_patterns_map)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('he will want to play the please beatles', 'he will want to listen the please beatles',
                               'she will want to play the please beatles', 'she will want to listen the please beatles',
                               'the beatles')
        expected_tokens_list = ('[START(he will want)] [PLAY(to play)] [ARTIST(the beatles)]',
                                '[START(she will want)] [PLAY(to play)] [ARTIST(the beatles)]',
                                '[START(he will want)] [PLAY(to listen)] [ARTIST(the beatles)]',
                                '[START(she will want)] [PLAY(to listen)] [ARTIST(the beatles)]',
                                '[artist(the beatles)]')
        groups = ('{None([START(he will want)])} {None([PLAY(to play)])} {None([ARTIST(the beatles)])}',
                  '{None([START(she will want)])} {None([PLAY(to play)])} {None([ARTIST(the beatles)])}',
                  '{None([START(he will want)])} {None([PLAY(to listen)])} {None([ARTIST(the beatles)])}',
                  '{None([START(she will want)])} {None([PLAY(to listen)])} {None([ARTIST(the beatles)])}',
                  '{None([ARTIST(the beatles)])}')

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, groups)]
        compare_all_pairs(self, pairs)

    def test_token_handlers_token(self) -> None:
        pattern_def_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles',),),)
        }
        token_handler_map = {
            'START': _just_tokens,
        }
        p = Pipeline(token_handler_map=token_handler_map)
        generator = p.flow(pattern_def_path,
                           dynamic_token_patterns_map=dynamic_token_patterns_map)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('he will want to play the beatles', 'he will want to listen the beatles',
                               'she will want to play the beatles', 'she will want to listen the beatles')
        expected_tokens_list = ('[START] [PLAY(to play)] [ARTIST(the beatles)]',
                                '[START] [PLAY(to play)] [ARTIST(the beatles)]',
                                '[START] [PLAY(to listen)] [ARTIST(the beatles)]',
                                '[START] [PLAY(to listen)] [ARTIST(the beatles)]')
        expected_groups = _generate_no_groups(expected_tokens_list)

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
        p = Pipeline(token_handler_map=token_handler_map)
        generator = p.flow(pattern_def_path,
                           dynamic_token_patterns_map=dynamic_token_patterns_map)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('he will want to play the beatles', 'he will want to listen the beatles',
                               'she will want to play the beatles', 'she will want to listen the beatles')
        expected_tokens_list = ('[START] [PLAY] [ARTIST]', '[START] [PLAY] [ARTIST]',
                                '[START] [PLAY] [ARTIST]', '[START] [PLAY] [ARTIST]')
        expected_groups = _generate_no_groups(expected_tokens_list)

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
        p = Pipeline(token_handler_map=token_handler_map)
        generator = p.flow(pattern_def_path,
                           dynamic_token_patterns_map=dynamic_token_patterns_map)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('he will want to play the beatles', 'he will want to listen the beatles',
                               'she will want to play the beatles', 'she will want to listen the beatles')
        expected_tokens_list = ('[START] [(to play)] [(the beatles)]',
                                '[START] [(to play)] [(the beatles)]',
                                '[START] [(to listen)] [(the beatles)]',
                                '[START] [(to listen)] [(the beatles)]')
        expected_groups = _generate_no_groups(expected_tokens_list)

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_after_joining_hooks_group(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles',),),)
        }

        after_joining_hooks_map = {
            ('None', 'PLAY_PHRASE') : (_add_commas_to_groups,),
        }

        p = Pipeline(after_joining_hooks_map=after_joining_hooks_map)
        generator = p.flow(pattern_def_path, dynamic_token_patterns_map=dynamic_token_patterns_map)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play', 'hi he will want to listen',
                               'hi she will want to play', 'hi she will want to listen', 'hi')
        expected_tokens_list = ('[WAKE(hi)] [START(he will want)] [PLAY(to play)]',
                                '[WAKE(hi)] [START(he will want)] [PLAY(to listen)]',
                                '[WAKE(hi)] [START(she will want)] [PLAY(to play)]',
                                '[WAKE(hi)] [START(she will want)] [PLAY(to listen)]',
                                '[WAKE(hi)]')
        groups = ('{None([WAKE(hi)])}, {PLAY_PHRASE([START(he will want)] [PLAY(to play)])},',
                  '{None([WAKE(hi)])}, {PLAY_PHRASE([START(he will want)] [PLAY(to listen)])},',
                  '{None([WAKE(hi)])}, {PLAY_PHRASE([START(she will want)] [PLAY(to play)])},',
                  '{None([WAKE(hi)])}, {PLAY_PHRASE([START(she will want)] [PLAY(to listen)])},',
                  '{None([WAKE(hi)])}')

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, groups)]
        compare_all_pairs(self, pairs)

    def test_after_joining_hooks_group_default(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles',),),)
        }

        after_joining_hooks_map = {
            'GROUP_DEFAULT' : (_lowercase_handled_groups,)
        }

        p = Pipeline(after_joining_hooks_map=after_joining_hooks_map)
        generator = p.flow(pattern_def_path, dynamic_token_patterns_map=dynamic_token_patterns_map)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play', 'hi he will want to listen',
                               'hi she will want to play', 'hi she will want to listen', 'hi')
        expected_tokens_list = ('[WAKE(hi)] [START(he will want)] [PLAY(to play)]',
                                '[WAKE(hi)] [START(he will want)] [PLAY(to listen)]',
                                '[WAKE(hi)] [START(she will want)] [PLAY(to play)]',
                                '[WAKE(hi)] [START(she will want)] [PLAY(to listen)]',
                                '[WAKE(hi)]')
        groups = ('{none([wake(hi)])} {play_phrase([start(he will want)] [play(to play)])}',
                  '{none([wake(hi)])} {play_phrase([start(he will want)] [play(to listen)])}',
                  '{none([wake(hi)])} {play_phrase([start(she will want)] [play(to play)])}',
                  '{none([wake(hi)])} {play_phrase([start(she will want)] [play(to listen)])}',
                  '{none([wake(hi)])}')

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, groups)]
        compare_all_pairs(self, pairs)

    def test_after_joining_hooks_group_and_group_default(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles',),),)
        }

        after_joining_hooks_map = {
            ('None', 'PLAY_PHRASE') : (_add_commas_to_groups,),
            'GROUP_DEFAULT' : (_lowercase_handled_groups,)
        }

        p = Pipeline(after_joining_hooks_map=after_joining_hooks_map)
        generator = p.flow(pattern_def_path, dynamic_token_patterns_map=dynamic_token_patterns_map)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play', 'hi he will want to listen',
                               'hi she will want to play', 'hi she will want to listen', 'hi')
        expected_tokens_list = ('[WAKE(hi)] [START(he will want)] [PLAY(to play)]',
                                '[WAKE(hi)] [START(he will want)] [PLAY(to listen)]',
                                '[WAKE(hi)] [START(she will want)] [PLAY(to play)]',
                                '[WAKE(hi)] [START(she will want)] [PLAY(to listen)]',
                                '[WAKE(hi)]')
        groups = ('{None([WAKE(hi)])}, {PLAY_PHRASE([START(he will want)] [PLAY(to play)])},',
                  '{None([WAKE(hi)])}, {PLAY_PHRASE([START(he will want)] [PLAY(to listen)])},',
                  '{None([WAKE(hi)])}, {PLAY_PHRASE([START(she will want)] [PLAY(to play)])},',
                  '{None([WAKE(hi)])}, {PLAY_PHRASE([START(she will want)] [PLAY(to listen)])},',
                  '{none([wake(hi)])}')

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, groups)]
        compare_all_pairs(self, pairs)

    def test_group_handlers_group(self) -> None:
        pattern_def_path = self._base_dir / 'static_and_base_tokens_and_group_tokens.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ((('the beatles',),),)
        }
        group_handler_map = {
            'PLAY_PHRASE': _remove_group,
        }
        p = Pipeline(group_handler_map=group_handler_map)
        generator = p.flow(pattern_def_path,
                           dynamic_token_patterns_map=dynamic_token_patterns_map)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play', 'hi he will want to listen',
                               'hi she will want to play', 'hi she will want to listen')
        expected_tokens_list = ('[WAKE(hi)] [START(he will want)] [PLAY(to play)]',
                                '[WAKE(hi)] [START(he will want)] [PLAY(to listen)]',
                                '[WAKE(hi)] [START(she will want)] [PLAY(to play)]',
                                '[WAKE(hi)] [START(she will want)] [PLAY(to listen)]')
        expected_groups = ('{None([WAKE(hi)])} {([START(he will want)] [PLAY(to play)])}',
                           '{None([WAKE(hi)])} {([START(he will want)] [PLAY(to listen)])}',
                           '{None([WAKE(hi)])} {([START(she will want)] [PLAY(to play)])}',
                           '{None([WAKE(hi)])} {([START(she will want)] [PLAY(to listen)])}')

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
        p = Pipeline(group_handler_map=group_handler_map)
        generator = p.flow(pattern_def_path,
                           dynamic_token_patterns_map=dynamic_token_patterns_map)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play', 'hi he will want to listen',
                               'hi she will want to play', 'hi she will want to listen')
        expected_tokens_list = ('[WAKE(hi)] [START(he will want)] [PLAY(to play)]',
                                '[WAKE(hi)] [START(he will want)] [PLAY(to listen)]',
                                '[WAKE(hi)] [START(she will want)] [PLAY(to play)]',
                                '[WAKE(hi)] [START(she will want)] [PLAY(to listen)]')
        expected_groups = ('[None] [PLAY_PHRASE]', '[None] [PLAY_PHRASE]',
                           '[None] [PLAY_PHRASE]', '[None] [PLAY_PHRASE]')

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
        p = Pipeline(group_handler_map=group_handler_map)
        generator = p.flow(pattern_def_path,
                           dynamic_token_patterns_map=dynamic_token_patterns_map)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play', 'hi he will want to listen',
                               'hi she will want to play', 'hi she will want to listen')
        expected_tokens_list = ('[WAKE(hi)] [START(he will want)] [PLAY(to play)]',
                                '[WAKE(hi)] [START(he will want)] [PLAY(to listen)]',
                                '[WAKE(hi)] [START(she will want)] [PLAY(to play)]',
                                '[WAKE(hi)] [START(she will want)] [PLAY(to listen)]')
        expected_groups = ('{([WAKE(hi)])} [PLAY_PHRASE]', '{([WAKE(hi)])} [PLAY_PHRASE]',
                           '{([WAKE(hi)])} [PLAY_PHRASE]', '{([WAKE(hi)])} [PLAY_PHRASE]')

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

        p = Pipeline()
        generator = p.flow(pattern_def_path,
                           dynamic_token_patterns_map=dynamic_token_patterns_map,
                           combo_options_map=combo_options_map)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('he will want to play the beatles', 'he will want to listen the beatles',
                               'she will want to play the beatles', 'she will want to listen the beatles')
        expected_tokens_list = ('[START(he will want)] [PLAY(to play)] [ARTIST(the beatles)]',
                                '[START(she will want)] [PLAY(to play)] [ARTIST(the beatles)]',
                                '[START(he will want)] [PLAY(to listen)] [ARTIST(the beatles)]',
                                '[START(she will want)] [PLAY(to listen)] [ARTIST(the beatles)]')
        expected_groups = _generate_no_groups(expected_tokens_list)

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

        p = Pipeline()
        generator = p.flow(pattern_def_path,
                           dynamic_token_patterns_map=dynamic_token_patterns_map,
                           combo_options_map=combo_options_map)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('she will want to listen the beatles', 'she will want to listen the beatles',
                               'he will want to play the beatles', 'she will want to play the beatles',
                               'she will want to listen the beatles')
        expected_tokens_list = ('[START(she will want)] [PLAY(to listen)] [ARTIST(the beatles)]',
                                '[START(she will want)] [PLAY(to listen)] [ARTIST(the beatles)]',
                                '[START(he will want)] [PLAY(to play)] [ARTIST(the beatles)]',
                                '[START(she will want)] [PLAY(to play)] [ARTIST(the beatles)]',
                                '[START(she will want)] [PLAY(to listen)] [ARTIST(the beatles)]')
        expected_groups = _generate_no_groups(expected_tokens_list)

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

        p = Pipeline()
        generator = p.flow(pattern_def_path,
                           dynamic_token_patterns_map=dynamic_token_patterns_map,
                           combo_options_map=combo_options_map)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('she will want to listen the beatles',
                               'she will want to listen the beatles',
                               'he will want to play the beatles',
                               'she will want to play the beatles',
                               'she will want to listen the beatles')
        expected_tokens_list = ('[START(she will want)] [PLAY(to listen)] [ARTIST(the beatles)]',
                                '[START(she will want)] [PLAY(to listen)] [ARTIST(the beatles)]',
                                '[START(he will want)] [PLAY(to play)] [ARTIST(the beatles)]',
                                '[START(she will want)] [PLAY(to play)] [ARTIST(the beatles)]',
                                '[START(she will want)] [PLAY(to listen)] [ARTIST(the beatles)]')
        expected_groups = _generate_no_groups(expected_tokens_list)

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

        p = Pipeline()
        generator = p.flow(pattern_def_path,
                           dynamic_token_patterns_map=dynamic_token_patterns_map,
                           combo_options_map=combo_options_map)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('she will want to listen the beatles', 'she will want to listen the beatles',
                               'he will want to play the beatles', 'kanye')
        expected_tokens_list = ('[START(she will want)] [PLAY(to listen)] [ARTIST(the beatles)]',
                                '[START(she will want)] [PLAY(to listen)] [ARTIST(the beatles)]',
                                '[START(he will want)] [PLAY(to play)] [ARTIST(the beatles)]',
                                '[ARTIST(kanye)]')
        expected_groups = _generate_no_groups(expected_tokens_list)

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_iob2_preset_tokens_to_include(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        p = Pipeline(preset=iob2.preset(tokens_to_include=('WAKE',)))
        generator = p.flow(pattern_def_path)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play',
                               'hi he will want to listen',
                               'hi she will want to play',
                               'hi she will want to listen',
                               'hi')
        expected_tokens_list = ('B-WAKE O O O O O',
                                'B-WAKE O O O O O',
                                'B-WAKE O O O O O',
                                'B-WAKE O O O O O',
                                'B-WAKE')
        expected_groups = ('B-None B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE',
                           'B-None B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE',
                           'B-None B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE',
                           'B-None B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE',
                           'B-None')
        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_iob2_preset_tokens_to_include_with_after_joining_hook(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        after_joining_hooks_map = {
            'DEFAULT' : (_add_random_words,),
            'GROUP_DEFAULT': (_lowercase_handled_groups,),
            ('WAKE',): (_lowercase_handled_tokens,)
        }
        p = Pipeline(preset=iob2.preset(tokens_to_include=('WAKE',)),
                     after_joining_hooks_map=after_joining_hooks_map)
        generator = p.flow(pattern_def_path)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play please',
                               'hi he will want to listen please',
                               'hi she will want to play please',
                               'hi she will want to listen please',
                               'hi')
        expected_tokens_list = ('B-WAKE O O O O O',
                                'B-WAKE O O O O O',
                                'B-WAKE O O O O O',
                                'B-WAKE O O O O O',
                                'b-wake')
        expected_groups = ('b-none b-play_phrase i-play_phrase i-play_phrase i-play_phrase i-play_phrase',
                           'b-none b-play_phrase i-play_phrase i-play_phrase i-play_phrase i-play_phrase',
                           'b-none b-play_phrase i-play_phrase i-play_phrase i-play_phrase i-play_phrase',
                           'b-none b-play_phrase i-play_phrase i-play_phrase i-play_phrase i-play_phrase',
                           'b-none')
        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_iob2_preset_tokens_to_exclude(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        p = Pipeline(preset=iob2.preset(tokens_to_exclude=('WAKE',)))
        generator = p.flow(pattern_def_path)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play',
                               'hi he will want to listen',
                               'hi she will want to play',
                               'hi she will want to listen',
                               'hi')
        expected_tokens_list = ('O B-START I-START I-START B-PLAY I-PLAY',
                                'O B-START I-START I-START B-PLAY I-PLAY',
                                'O B-START I-START I-START B-PLAY I-PLAY',
                                'O B-START I-START I-START B-PLAY I-PLAY',
                                'O')
        expected_groups = ('B-None B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE',
                           'B-None B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE',
                           'B-None B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE',
                           'B-None B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE',
                           'B-None')
        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_iob2_preset_tokens_to_exclude_with_after_joining_hook(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        after_joining_hooks_map = {
            'DEFAULT' : (_add_random_words,),
            'GROUP_DEFAULT': (_lowercase_handled_groups,),
            ('WAKE',): (_lowercase_handled_tokens,)
        }
        p = Pipeline(preset=iob2.preset(tokens_to_exclude=('WAKE',)),
                     after_joining_hooks_map=after_joining_hooks_map)
        generator = p.flow(pattern_def_path)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play please',
                               'hi he will want to listen please',
                               'hi she will want to play please',
                               'hi she will want to listen please',
                               'hi')
        expected_tokens_list = ('O B-START I-START I-START B-PLAY I-PLAY',
                                'O B-START I-START I-START B-PLAY I-PLAY',
                                'O B-START I-START I-START B-PLAY I-PLAY',
                                'O B-START I-START I-START B-PLAY I-PLAY',
                                'b-wake')
        expected_groups = ('b-none b-play_phrase i-play_phrase i-play_phrase i-play_phrase i-play_phrase',
                           'b-none b-play_phrase i-play_phrase i-play_phrase i-play_phrase i-play_phrase',
                           'b-none b-play_phrase i-play_phrase i-play_phrase i-play_phrase i-play_phrase',
                           'b-none b-play_phrase i-play_phrase i-play_phrase i-play_phrase i-play_phrase',
                           'b-none')
        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_iob2_preset_tokens_to_include_and_tokens_to_exclude(self) -> None:
        with self.assertRaises(ValueError):
            Pipeline(preset=iob2.preset(tokens_to_include=('WAKE',), tokens_to_exclude=('PLAY',)))

    def test_iob2_preset_groups_to_include_and_groups_to_exclude(self) -> None:
        with self.assertRaises(ValueError):
            Pipeline(preset=iob2.preset(groups_to_include=('PLAY_SONG',), groups_to_exclude=('PLAY_ARTIST',)))

    def test_preset_str_invalid(self) -> None:
        with self.assertRaises(ValueError):
            Pipeline(preset='INVALID')

    def test_iob2_preset_groups_to_include(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        p = Pipeline(preset=iob2.preset(groups_to_include=('PLAY_PHRASE',)))
        generator = p.flow(pattern_def_path)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play',
                               'hi he will want to listen',
                               'hi she will want to play',
                               'hi she will want to listen',
                               'hi')
        expected_tokens_list = ('B-WAKE B-START I-START I-START B-PLAY I-PLAY',
                                'B-WAKE B-START I-START I-START B-PLAY I-PLAY',
                                'B-WAKE B-START I-START I-START B-PLAY I-PLAY',
                                'B-WAKE B-START I-START I-START B-PLAY I-PLAY',
                                'B-WAKE')
        expected_groups = ('O B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE',
                           'O B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE',
                           'O B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE',
                           'O B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE',
                           'O')
        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_iob2_preset_groups_to_include_with_after_joining_map(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        after_joining_hooks_map = {
            'DEFAULT' : (_add_random_words,),
            'GROUP_DEFAULT': (_lowercase_handled_groups,),
            ('WAKE',): (_lowercase_handled_tokens,)
        }
        p = Pipeline(preset=iob2.preset(groups_to_include=('PLAY_PHRASE',)),
                     after_joining_hooks_map=after_joining_hooks_map)
        generator = p.flow(pattern_def_path)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play please',
                               'hi he will want to listen please',
                               'hi she will want to play please',
                               'hi she will want to listen please',
                               'hi')
        expected_tokens_list = ('B-WAKE B-START I-START I-START B-PLAY I-PLAY',
                                'B-WAKE B-START I-START I-START B-PLAY I-PLAY',
                                'B-WAKE B-START I-START I-START B-PLAY I-PLAY',
                                'B-WAKE B-START I-START I-START B-PLAY I-PLAY',
                                'b-wake')
        expected_groups = ('o b-play_phrase i-play_phrase i-play_phrase i-play_phrase i-play_phrase',
                           'o b-play_phrase i-play_phrase i-play_phrase i-play_phrase i-play_phrase',
                           'o b-play_phrase i-play_phrase i-play_phrase i-play_phrase i-play_phrase',
                           'o b-play_phrase i-play_phrase i-play_phrase i-play_phrase i-play_phrase',
                           'o')
        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_iob2_preset_groups_to_exclude(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        p = Pipeline(preset=iob2.preset(groups_to_exclude=('PLAY_PHRASE',)))
        generator = p.flow(pattern_def_path)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play',
                               'hi he will want to listen',
                               'hi she will want to play',
                               'hi she will want to listen',
                               'hi')
        expected_tokens_list = ('B-WAKE B-START I-START I-START B-PLAY I-PLAY',
                                'B-WAKE B-START I-START I-START B-PLAY I-PLAY',
                                'B-WAKE B-START I-START I-START B-PLAY I-PLAY',
                                'B-WAKE B-START I-START I-START B-PLAY I-PLAY',
                                'B-WAKE')
        expected_groups = ('B-None O O O O O',
                           'B-None O O O O O',
                           'B-None O O O O O',
                           'B-None O O O O O',
                           'B-None')
        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_iob2_preset_groups_to_exclude_with_after_joining_hooks_map(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        after_joining_hooks_map = {
            'DEFAULT' : (_add_random_words,),
            'GROUP_DEFAULT': (_lowercase_handled_groups,),
            ('WAKE',): (_lowercase_handled_tokens,)
        }
        p = Pipeline(preset=iob2.preset(groups_to_exclude=('PLAY_PHRASE',)),
                     after_joining_hooks_map=after_joining_hooks_map)
        generator = p.flow(pattern_def_path)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play please',
                               'hi he will want to listen please',
                               'hi she will want to play please',
                               'hi she will want to listen please',
                               'hi')
        expected_tokens_list = ('B-WAKE B-START I-START I-START B-PLAY I-PLAY',
                                'B-WAKE B-START I-START I-START B-PLAY I-PLAY',
                                'B-WAKE B-START I-START I-START B-PLAY I-PLAY',
                                'B-WAKE B-START I-START I-START B-PLAY I-PLAY',
                                'b-wake')
        expected_groups = ('b-none o o o o o',
                           'b-none o o o o o',
                           'b-none o o o o o',
                           'b-none o o o o o',
                           'b-none')
        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_iob2_str_preset(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        p = Pipeline(preset='IOB2')
        generator = p.flow(pattern_def_path)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play',
                               'hi he will want to listen',
                               'hi she will want to play',
                               'hi she will want to listen',
                               'hi')
        expected_tokens_list = ('B-WAKE B-START I-START I-START B-PLAY I-PLAY',
                                'B-WAKE B-START I-START I-START B-PLAY I-PLAY',
                                'B-WAKE B-START I-START I-START B-PLAY I-PLAY',
                                'B-WAKE B-START I-START I-START B-PLAY I-PLAY',
                                'B-WAKE')
        expected_groups = ('B-None B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE',
                           'B-None B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE',
                           'B-None B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE',
                           'B-None B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE',
                           'B-None')
        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_iob2_override_token_group_handler_default(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        token_handler_map = {
            'DEFAULT': _just_tokens,
        }
        group_handler_map = {
            'DEFAULT': _remove_group,
        }
        p = Pipeline(preset='IOB2',
                     group_handler_map=group_handler_map,
                     token_handler_map=token_handler_map)
        generator = p.flow(pattern_def_path)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play',
                               'hi he will want to listen',
                               'hi she will want to play',
                               'hi she will want to listen',
                               'hi')
        expected_tokens_list = ('B-WAKE B-START I-START I-START B-PLAY I-PLAY',
                                'B-WAKE B-START I-START I-START B-PLAY I-PLAY',
                                'B-WAKE B-START I-START I-START B-PLAY I-PLAY',
                                'B-WAKE B-START I-START I-START B-PLAY I-PLAY',
                                'B-WAKE')
        expected_groups = ('B-None B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE',
                           'B-None B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE',
                           'B-None B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE',
                           'B-None B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE',
                           'B-None')
        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_iob2_token_group_handler_non_default(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        token_handler_map = {
            'WAKE': _remove_token,
        }
        group_handler_map = {
            'PLAY_PHRASE': _remove_group,
        }
        p = Pipeline(preset='IOB2',
                     group_handler_map=group_handler_map,
                     token_handler_map=token_handler_map)
        generator = p.flow(pattern_def_path)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play',
                               'hi he will want to listen',
                               'hi she will want to play',
                               'hi she will want to listen',
                               'hi')
        expected_tokens_list = ('[(hi)] B-START I-START I-START B-PLAY I-PLAY',
                                '[(hi)] B-START I-START I-START B-PLAY I-PLAY',
                                '[(hi)] B-START I-START I-START B-PLAY I-PLAY',
                                '[(hi)] B-START I-START I-START B-PLAY I-PLAY',
                                '[(hi)]')
        expected_groups = ('B-None {(B-START I-START I-START B-PLAY I-PLAY)}',
                           'B-None {(B-START I-START I-START B-PLAY I-PLAY)}',
                           'B-None {(B-START I-START I-START B-PLAY I-PLAY)}',
                           'B-None {(B-START I-START I-START B-PLAY I-PLAY)}',
                           'B-None')
        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

def _generate_no_groups(expected_tokens_list: Sequence[str]) -> Sequence[str]:
    default_group_handler = lambda group_name, expected_tokens: '{{{}({})}}'.format(group_name, expected_tokens)
    expected_groups = []
    for expected_tokens in expected_tokens_list:
        expected_group = []
        for index, handled_token in enumerate(expected_tokens.split(' [')):
            if index != 0:
                handled_token = '[' + handled_token
            expected_group.append(default_group_handler('None', handled_token))
        expected_groups.append(' '.join(expected_group))
    return tuple(expected_groups)

def _just_groups(group_name: str, _: Sequence[str]) -> str:
    return '[{group_name}]'.format(group_name=group_name)

def _remove_group(_: str, handled_tokens: Sequence[str]) -> str:
    return '{{({handled_tokens})}}'.format(handled_tokens=' '.join(handled_tokens))

def _just_tokens(token: str, _: str) -> str:
    return '[{token}]'.format(token=token)

def _remove_token(_: str, phrase: str) -> str:
    return '[({phrase})]'.format(phrase=phrase)

def _sample_utterance_combo(utterance_combo: COMBO,
                            tokens: Sequence[str],
                            groups: Sequence[GROUP],
                            token_to_sample: str,
                            sample_size: int,
                            ) -> Tuple[COMBO, Sequence[str], Sequence[GROUP]]:
    random.seed(0)
    TOKEN_INDEX = tokens.index(token_to_sample)
    utterance_combo_list = list(utterance_combo)
    sampled_combos = tuple(random.sample(utterance_combo_list.pop(TOKEN_INDEX), sample_size))
    utterance_combo_list.insert(TOKEN_INDEX, sampled_combos)
    utterance_combo = tuple(utterance_combo_list)
    return utterance_combo, tokens, groups

def _sample_play(utterance_combo: COMBO,
                 tokens: Sequence[str],
                 groups: Sequence[GROUP]
                 ) -> Tuple[COMBO, Sequence[str], Sequence[GROUP]]:
    return _sample_utterance_combo(utterance_combo, tokens, groups, 'PLAY', 1)

def _sample_artist(utterance_combo: COMBO,
                   tokens: Sequence[str],
                   groups: Sequence[GROUP]
                   ) -> Tuple[COMBO, Sequence[str], Sequence[GROUP]]:
    return _sample_utterance_combo(utterance_combo, tokens, groups, 'ARTIST', 1)

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
