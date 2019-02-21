import unittest
from pathlib import Path

from putput.expander import expand
from tests.unit.helper_functions import compare_all_pairs


class TestExpander(unittest.TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self._base_dir = Path(__file__).parent / 'pattern_definitions' / 'valid'

    def test_dynamic_token_patterns_only(self) -> None:
        dynamic_token_patterns_map = {'ARTIST': ((('the beatles', 'kanye'),),)}
        pattern_def = self._base_dir / 'dynamic_token_patterns_only.yml'
        expected_utterance_combo = ((('the beatles', 'kanye'),),)
        expected_tokens = (('ARTIST',),)
        expected_groups = (((('None', 1)),),)
        _, generator = expand(pattern_def, dynamic_token_patterns_map=dynamic_token_patterns_map)
        actual_utterance_combo, actual_tokens, actual_groups = zip(*generator)
        pairs = [(actual_utterance_combo, expected_utterance_combo),
                 (actual_tokens, expected_tokens),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_static_token_patterns_only(self) -> None:
        pattern_def = self._base_dir / 'static_token_patterns_only.yml'
        _, generator = expand(pattern_def)
        actual_utterance_combo, actual_tokens, actual_groups = zip(*generator)
        expected_utterance_combo = ((('he will want', 'she will want'), ('to play', 'to listen')),)
        expected_tokens = (('START', 'PLAY'),)
        expected_groups = (((('None', 1)), ('None', 1)),)
        pairs = [(actual_utterance_combo, expected_utterance_combo),
                 (actual_tokens, expected_tokens),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_dynamic_and_static_token_patterns(self) -> None:
        dynamic_token_patterns_map = {'ARTIST': ((('the beatles', 'kanye'),),)}
        pattern_def = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        _, generator = expand(pattern_def, dynamic_token_patterns_map=dynamic_token_patterns_map)
        actual_utterance_combo, actual_tokens, actual_groups = zip(*generator)
        expected_utterance_combo = ((('he will want', 'she will want'),
                                     ('to play', 'to listen'),
                                     ('the beatles', 'kanye')),)
        expected_tokens = (('START', 'PLAY', 'ARTIST'),)
        expected_groups = ((('None', 1), ('None', 1), ('None', 1)),)
        pairs = [(actual_utterance_combo, expected_utterance_combo),
                 (actual_tokens, expected_tokens),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_static_and_base_tokens(self) -> None:
        pattern_def = self._base_dir / 'static_and_base_tokens.yml'
        _, generator = expand(pattern_def)
        actual_utterance_combo, actual_tokens, actual_groups = zip(*generator)
        expected_utterance_combo = ((('he will want', 'she will want'), ('to play', 'to listen')),)
        expected_tokens = (('START', 'PLAY'),)
        expected_groups = ((('None', 1), ('None', 1)),)
        pairs = [(actual_utterance_combo, expected_utterance_combo),
                 (actual_tokens, expected_tokens),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_static_and_base_tokens_and_group_tokens(self) -> None:
        pattern_def = self._base_dir / 'static_and_base_tokens_and_group_tokens.yml'
        _, generator = expand(pattern_def)
        actual_utterance_combo, actual_tokens, actual_groups = zip(*generator)
        expected_utterance_combo = ((('hi',), ('he will want', 'she will want'), ('to play', 'to listen')),)
        expected_tokens = (('WAKE', 'START', 'PLAY'),)
        expected_groups = ((('None', 1), ('PLAY_PHRASE', 2),),)
        pairs = [(actual_utterance_combo, expected_utterance_combo),
                 (actual_tokens, expected_tokens),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_keys_in_addition_to_utterance_patterns_token_patterns(self) -> None:
        dynamic_token_patterns_map = {'ARTIST': ((('the beatles', 'kanye'),),)}
        pattern_def = self._base_dir / 'keys_in_addition_to_utterance_patterns_tokens_patterns.yml'
        _, generator = expand(pattern_def, dynamic_token_patterns_map=dynamic_token_patterns_map)
        actual_utterance_combo, actual_tokens, actual_groups = zip(*generator)
        expected_utterance_combo = ((('he will want', 'she will want'),
                                     ('to play', 'to listen'),
                                     ('the beatles', 'kanye')),)
        expected_tokens = (('START', 'PLAY', 'ARTIST'),)
        expected_groups = ((('None', 1), ('None', 1), ('None', 1)),)
        pairs = [(actual_utterance_combo, expected_utterance_combo),
                 (actual_tokens, expected_tokens),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_groups_with_range(self) -> None:
        artists = ('the beatles', 'kanye', 'nico', 'tom waits')
        dynamic_token_patterns_map = {'ARTIST': ((artists,),)}
        pattern_def = self._base_dir / 'groups_with_range.yml'
        _, generator = expand(pattern_def, dynamic_token_patterns_map=dynamic_token_patterns_map)
        actual_utterance_combo, actual_tokens, actual_groups = zip(*generator)
        expected_utterance_combo = ((('she wants',), ('to play',), artists),
                                    (('she wants',), ('to play',), artists, artists),
                                    (('she wants',), ('to play',), artists, artists, artists),)
        expected_tokens = (('START', 'PLAY', 'ARTIST'),
                           ('START', 'PLAY', 'ARTIST', 'ARTIST'),
                           ('START', 'PLAY', 'ARTIST', 'ARTIST', 'ARTIST'),)
        expected_groups = ((('None', 1), ('PLAY_ARTISTS', 2)),
                           (('None', 1), ('PLAY_ARTISTS', 3)),
                           (('None', 1), ('PLAY_ARTISTS', 4)),)
        pairs = [(actual_utterance_combo, expected_utterance_combo),
                 (actual_tokens, expected_tokens),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_groups_with_single_range(self) -> None:
        artists = ('the beatles', 'kanye', 'nico', 'tom waits')
        dynamic_token_patterns_map = {'ARTIST': ((artists,),)}
        pattern_def = self._base_dir / 'groups_with_single_range.yml'
        _, generator = expand(pattern_def, dynamic_token_patterns_map=dynamic_token_patterns_map)
        actual_utterance_combo, actual_tokens, actual_groups = zip(*generator)
        expected_utterance_combo = ((('she wants',), ('to play',), artists, artists, artists),)
        expected_tokens = (('START', 'PLAY', 'ARTIST', 'ARTIST', 'ARTIST'),)
        expected_groups = ((('None', 1), ('PLAY_ARTISTS', 4)),)
        pairs = [(actual_utterance_combo, expected_utterance_combo),
                 (actual_tokens, expected_tokens),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_utterance_patterns_with_range(self) -> None:
        artists = ('the beatles', 'kanye', 'nico', 'tom waits')
        dynamic_token_patterns_map = {'ARTIST': ((artists,),)}
        pattern_def = self._base_dir / 'utterance_patterns_with_range.yml'
        _, generator = expand(pattern_def, dynamic_token_patterns_map=dynamic_token_patterns_map)
        actual_utterance_combo, actual_tokens, actual_groups = zip(*generator)
        expected_utterance_combo = ((('she wants',), ('to play',), artists),
                                    (('she wants',), ('to play',), artists, ('to play',), artists),
                                    (('she wants',), ('to play',), artists,
                                     ('to play',), artists, ('to play',), artists),)
        expected_tokens = (('START', 'PLAY', 'ARTIST'),
                           ('START', 'PLAY', 'ARTIST', 'PLAY', 'ARTIST'),
                           ('START', 'PLAY', 'ARTIST', 'PLAY', 'ARTIST', 'PLAY', 'ARTIST'),)
        expected_groups = ((('None', 1), ('PLAY_ARTIST', 2)),
                           (('None', 1), ('PLAY_ARTIST', 2), ('PLAY_ARTIST', 2)),
                           (('None', 1), ('PLAY_ARTIST', 2), ('PLAY_ARTIST', 2), ('PLAY_ARTIST', 2)),)
        pairs = [(actual_utterance_combo, expected_utterance_combo),
                 (actual_tokens, expected_tokens),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_utterance_patterns_with_range_and_non_range(self) -> None:
        artists = ('the beatles', 'kanye', 'nico', 'tom waits')
        dynamic_token_patterns_map = {'ARTIST': ((artists,),)}
        pattern_def = self._base_dir / 'utterance_patterns_with_range_and_non_range.yml'
        _, generator = expand(pattern_def, dynamic_token_patterns_map=dynamic_token_patterns_map)
        actual_utterance_combo, actual_tokens, actual_groups = zip(*generator)
        expected_utterance_combo = ((('she wants',),),
                                    (('she wants',), ('to play',), artists),
                                    (('she wants',), ('to play',), artists, ('to play',), artists),
                                    (('she wants',), ('to play',), artists,
                                     ('to play',), artists, ('to play',), artists),)
        expected_tokens = (('START',),
                           ('START', 'PLAY', 'ARTIST'),
                           ('START', 'PLAY', 'ARTIST', 'PLAY', 'ARTIST'),
                           ('START', 'PLAY', 'ARTIST', 'PLAY', 'ARTIST', 'PLAY', 'ARTIST'),)
        expected_groups = ((('None', 1),),
                           (('None', 1), ('PLAY_ARTIST', 2)),
                           (('None', 1), ('PLAY_ARTIST', 2), ('PLAY_ARTIST', 2)),
                           (('None', 1), ('PLAY_ARTIST', 2), ('PLAY_ARTIST', 2), ('PLAY_ARTIST', 2)),)
        pairs = [(actual_utterance_combo, expected_utterance_combo),
                 (actual_tokens, expected_tokens),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_groups_with_range_and_non_range(self) -> None:
        artists = ('the beatles', 'kanye', 'nico', 'tom waits')
        dynamic_token_patterns_map = {'ARTIST': ((artists,),)}
        pattern_def = self._base_dir / 'groups_with_range_and_non_range.yml'
        _, generator = expand(pattern_def, dynamic_token_patterns_map=dynamic_token_patterns_map)
        actual_utterance_combo, actual_tokens, actual_groups = zip(*generator)
        expected_utterance_combo = ((('she wants',), ('to play',), artists, artists, artists),
                                    (('she wants',), ('to play',), artists),)
        expected_tokens = (('START', 'PLAY', 'ARTIST', 'ARTIST', 'ARTIST'),
                           ('START', 'PLAY', 'ARTIST'),)
        expected_groups = ((('None', 1), ('PLAY_ARTISTS', 4)),
                           (('START_SONG', 3),),)
        pairs = [(actual_utterance_combo, expected_utterance_combo),
                 (actual_tokens, expected_tokens),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

if __name__ == '__main__':
    unittest.main()
