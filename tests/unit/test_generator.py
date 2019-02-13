import unittest
from pathlib import Path

from putput.generator import generate_utterance_combo_tokens_and_groups
from putput.generator import generate_utterances_and_handled_tokens
from putput.joiner import ComboOptions
from tests.unit.helper_functions import compare_all_pairs


class TestGenerateUtteranceComboTokensAndGroups(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    def setUp(self) -> None:
        self.maxDiff = None
        self._base_dir = Path(__file__).parent / 'pattern_definitions' / 'valid'

    def test_dynamic_token_patterns_only(self) -> None:
        dynamic_token_patterns_map = {'ARTIST': ((('the beatles', 'kanye'),),)}
        pattern_def = self._base_dir / 'dynamic_token_patterns_only.yml'
        expected_utterance_combo = ((('the beatles', 'kanye'),),)
        expected_tokens = (('ARTIST',),)
        expected_groups = (((('None', 1)),),)
        generator = generate_utterance_combo_tokens_and_groups(pattern_def,
                                                               dynamic_token_patterns_map=dynamic_token_patterns_map)
        actual_utterance_combo, actual_tokens, actual_groups = zip(*generator)
        pairs = [(actual_utterance_combo, expected_utterance_combo),
                 (actual_tokens, expected_tokens),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_static_token_patterns_only(self) -> None:
        pattern_def = self._base_dir / 'static_token_patterns_only.yml'
        generator = generate_utterance_combo_tokens_and_groups(pattern_def)
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
        generator = generate_utterance_combo_tokens_and_groups(pattern_def,
                                                               dynamic_token_patterns_map=dynamic_token_patterns_map)
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
        generator = generate_utterance_combo_tokens_and_groups(pattern_def)
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
        generator = generate_utterance_combo_tokens_and_groups(pattern_def)
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
        generator = generate_utterance_combo_tokens_and_groups(pattern_def,
                                                               dynamic_token_patterns_map=dynamic_token_patterns_map)
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
        generator = generate_utterance_combo_tokens_and_groups(pattern_def,
                                                               dynamic_token_patterns_map=dynamic_token_patterns_map)
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
        generator = generate_utterance_combo_tokens_and_groups(pattern_def,
                                                               dynamic_token_patterns_map=dynamic_token_patterns_map)
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
        generator = generate_utterance_combo_tokens_and_groups(pattern_def,
                                                               dynamic_token_patterns_map=dynamic_token_patterns_map)
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
        generator = generate_utterance_combo_tokens_and_groups(pattern_def,
                                                               dynamic_token_patterns_map=dynamic_token_patterns_map)
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
        generator = generate_utterance_combo_tokens_and_groups(pattern_def,
                                                               dynamic_token_patterns_map=dynamic_token_patterns_map)
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

class TestGenerateUtterancesHandledTokens(unittest.TestCase):
    def test_one_token(self) -> None:
        utterance_combo = (('the beatles', 'kanye'),)
        tokens = ('ARTIST',)
        generator = generate_utterances_and_handled_tokens(utterance_combo, tokens)
        actual_utterances, actual_handled_tokens = zip(*generator)
        expected_utterances = ('the beatles', 'kanye')
        expected_handled_tokens = (('[ARTIST(the beatles)]',), ('[ARTIST(kanye)]',))
        pairs = [(actual_utterances, expected_utterances), (actual_handled_tokens, expected_handled_tokens)]
        compare_all_pairs(self, pairs)

    def test_multiple_tokens(self) -> None:
        utterance_combo = (('he will want', 'she will want'), ('to play', 'to listen'))
        tokens = ('START', 'PLAY')
        generator = generate_utterances_and_handled_tokens(utterance_combo, tokens)
        actual_utterances, actual_handled_tokens = zip(*generator)
        expected_utterances = ('he will want to play', 'he will want to listen',
                               'she will want to play', 'she will want to listen')
        expected_handled_tokens = (('[START(he will want)]', '[PLAY(to play)]',),
                                   ('[START(he will want)]', '[PLAY(to listen)]',),
                                   ('[START(she will want)]', '[PLAY(to play)]',),
                                   ('[START(she will want)]', '[PLAY(to listen)]',))
        pairs = [(actual_utterances, expected_utterances), (actual_handled_tokens, expected_handled_tokens)]
        compare_all_pairs(self, pairs)

    def test_default_token_handler(self) -> None:
        _custom_token_handler = lambda token, tokenized_phrase: '[{}({})]'.format(token, tokenized_phrase)
        utterance_combo = (('he will want', 'she will want'), ('to play', 'to listen'))
        tokens = ('START', 'PLAY')
        token_handler_map = {'DEFAULT': _custom_token_handler}
        generator = generate_utterances_and_handled_tokens(utterance_combo,
                                                           tokens,
                                                           token_handler_map=token_handler_map)
        actual_utterances, actual_handled_tokens = zip(*generator)
        expected_utterances = ('he will want to play', 'he will want to listen',
                               'she will want to play', 'she will want to listen')
        expected_handled_tokens = (('[START(he will want)]', '[PLAY(to play)]',),
                                   ('[START(he will want)]', '[PLAY(to listen)]',),
                                   ('[START(she will want)]', '[PLAY(to play)]',),
                                   ('[START(she will want)]', '[PLAY(to listen)]',))
        pairs = [(actual_utterances, expected_utterances), (actual_handled_tokens, expected_handled_tokens)]
        compare_all_pairs(self, pairs)

    def test_token_token_handler(self) -> None:
        _custom_token_handler = lambda token, tokenized_phrase: '[{}]'.format(token)
        utterance_combo = (('he will want', 'she will want'), ('to play', 'to listen'))
        tokens = ('START', 'PLAY')
        token_handler_map = {'START': _custom_token_handler}
        generator = generate_utterances_and_handled_tokens(utterance_combo,
                                                           tokens,
                                                           token_handler_map=token_handler_map)
        actual_utterances, actual_handled_tokens = zip(*generator)
        expected_utterances = ('he will want to play', 'he will want to listen',
                               'she will want to play', 'she will want to listen')
        expected_handled_tokens = (('[START]', '[PLAY(to play)]',), ('[START]', '[PLAY(to listen)]',),
                                   ('[START]', '[PLAY(to play)]',), ('[START]', '[PLAY(to listen)]',))
        pairs = [(actual_utterances, expected_utterances), (actual_handled_tokens, expected_handled_tokens)]
        compare_all_pairs(self, pairs)

    def test_token_and_default_token_handler(self) -> None:
        _start_token_handler = lambda token, tokenized_phrase: '[{}]'.format(token)
        _default_token_handler = lambda token, tokenized_phrase: '[{}(default)]'.format(token)
        utterance_combo = (('he will want', 'she will want'), ('to play', 'to listen'))
        tokens = ('START', 'PLAY')
        token_handler_map = {'START': _start_token_handler, 'DEFAULT': _default_token_handler}
        generator = generate_utterances_and_handled_tokens(utterance_combo,
                                                           tokens,
                                                           token_handler_map=token_handler_map)
        actual_utterances, actual_handled_tokens = zip(*generator)
        expected_utterances = ('he will want to play', 'he will want to listen',
                               'she will want to play', 'she will want to listen')
        expected_handled_tokens = (('[START]', '[PLAY(default)]',), ('[START]', '[PLAY(default)]',),
                                   ('[START]', '[PLAY(default)]',), ('[START]', '[PLAY(default)]',))
        pairs = [(actual_utterances, expected_utterances), (actual_handled_tokens, expected_handled_tokens)]
        compare_all_pairs(self, pairs)

    def test_combo_options_without_replacement(self) -> None:
        utterance_combo = (('he will want', 'she will want'), ('to play', 'to listen'))
        tokens = ('START', 'PLAY')
        combo_options = ComboOptions(max_sample_size=6, with_replacement=False, seed=0)
        generator = generate_utterances_and_handled_tokens(utterance_combo,
                                                           tokens,
                                                           combo_options=combo_options)
        actual_utterances, actual_handled_tokens = zip(*generator)
        expected_utterances = ('he will want to play', 'he will want to listen',
                               'she will want to play', 'she will want to listen')
        expected_handled_tokens = (('[START(he will want)]', '[PLAY(to play)]',),
                                   ('[START(he will want)]', '[PLAY(to listen)]',),
                                   ('[START(she will want)]', '[PLAY(to play)]',),
                                   ('[START(she will want)]', '[PLAY(to listen)]',))
        pairs = [(actual_utterances, expected_utterances), (actual_handled_tokens, expected_handled_tokens)]
        compare_all_pairs(self, pairs)

    def test_combo_options_with_replacement(self) -> None:
        utterance_combo = (('he will want', 'she will want'), ('to play', 'to listen'))
        tokens = ('START', 'PLAY')
        combo_options = ComboOptions(max_sample_size=6, with_replacement=True, seed=0)
        generator = generate_utterances_and_handled_tokens(utterance_combo,
                                                           tokens,
                                                           combo_options=combo_options)
        actual_utterances, actual_handled_tokens = zip(*generator)
        expected_utterances = ('she will want to listen', 'she will want to listen',
                               'he will want to play', 'she will want to play',
                               'she will want to listen', 'she will want to listen')
        expected_handled_tokens = (('[START(she will want)]', '[PLAY(to listen)]'),
                                   ('[START(she will want)]', '[PLAY(to listen)]'),
                                   ('[START(he will want)]', '[PLAY(to play)]'),
                                   ('[START(she will want)]', '[PLAY(to play)]'),
                                   ('[START(she will want)]', '[PLAY(to listen)]'),
                                   ('[START(she will want)]', '[PLAY(to listen)]'))
        pairs = [(actual_utterances, expected_utterances), (actual_handled_tokens, expected_handled_tokens)]
        compare_all_pairs(self, pairs)

if __name__ == '__main__':
    unittest.main()
