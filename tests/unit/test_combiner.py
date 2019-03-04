import unittest

from putput.combiner import combine
from putput.joiner import ComboOptions
from tests.unit.helper_functions import compare_all_pairs


class TestCombiner(unittest.TestCase):
    def test_one_token(self) -> None:
        utterance_combo = (('the beatles', 'kanye'),)
        tokens = ('ARTIST',)
        groups = (('None', 1),)
        _, generator = combine(utterance_combo, tokens, groups)
        actual_utterances, actual_handled_tokens, actual_handled_groups = zip(*generator)
        expected_utterances = ('the beatles', 'kanye')
        expected_handled_tokens = (('[ARTIST(the beatles)]',), ('[ARTIST(kanye)]',))
        expected_handled_groups = (('{None([ARTIST(the beatles)])}',), ('{None([ARTIST(kanye)])}',))
        pairs = [(actual_utterances, expected_utterances),
                 (actual_handled_tokens, expected_handled_tokens),
                 (actual_handled_groups, expected_handled_groups)]
        compare_all_pairs(self, pairs)

    def test_multiple_tokens(self) -> None:
        utterance_combo = (('he will want', 'she will want'), ('to play', 'to listen'))
        tokens = ('START', 'PLAY')
        groups = (('None', 1), ('None', 1))
        _, generator = combine(utterance_combo, tokens, groups)
        actual_utterances, actual_handled_tokens, actual_handled_groups = zip(*generator)
        expected_utterances = ('he will want to play', 'he will want to listen',
                               'she will want to play', 'she will want to listen')
        expected_handled_tokens = (('[START(he will want)]', '[PLAY(to play)]',),
                                   ('[START(he will want)]', '[PLAY(to listen)]',),
                                   ('[START(she will want)]', '[PLAY(to play)]',),
                                   ('[START(she will want)]', '[PLAY(to listen)]',))
        expected_handled_groups = (('{None([START(he will want)])}', '{None([PLAY(to play)])}'),
                                   ('{None([START(he will want)])}', '{None([PLAY(to listen)])}'),
                                   ('{None([START(she will want)])}', '{None([PLAY(to play)])}'),
                                   ('{None([START(she will want)])}', '{None([PLAY(to listen)])}'))
        pairs = [(actual_utterances, expected_utterances),
                 (actual_handled_tokens, expected_handled_tokens),
                 (actual_handled_groups, expected_handled_groups)]
        compare_all_pairs(self, pairs)

    def test_default_token_handler(self) -> None:
        # pylint: disable=too-many-locals
        _custom_token_handler = lambda token, tokenized_phrase: '[{}({})]'.format(token, tokenized_phrase)
        utterance_combo = (('he will want', 'she will want'), ('to play', 'to listen'))
        tokens = ('START', 'PLAY')
        groups = (('None', 1), ('None', 1))
        token_handler_map = {'DEFAULT': _custom_token_handler}
        _, generator = combine(utterance_combo, tokens, groups, token_handler_map=token_handler_map)
        actual_utterances, actual_handled_tokens, actual_handled_groups = zip(*generator)
        expected_utterances = ('he will want to play', 'he will want to listen',
                               'she will want to play', 'she will want to listen')
        expected_handled_tokens = (('[START(he will want)]', '[PLAY(to play)]',),
                                   ('[START(he will want)]', '[PLAY(to listen)]',),
                                   ('[START(she will want)]', '[PLAY(to play)]',),
                                   ('[START(she will want)]', '[PLAY(to listen)]',))
        expected_handled_groups = (('{None([START(he will want)])}', '{None([PLAY(to play)])}'),
                                   ('{None([START(he will want)])}', '{None([PLAY(to listen)])}'),
                                   ('{None([START(she will want)])}', '{None([PLAY(to play)])}'),
                                   ('{None([START(she will want)])}', '{None([PLAY(to listen)])}'))
        pairs = [(actual_utterances, expected_utterances),
                 (actual_handled_tokens, expected_handled_tokens),
                 (actual_handled_groups, expected_handled_groups)]
        compare_all_pairs(self, pairs)

    def test_token_token_handler(self) -> None:
        # pylint: disable=too-many-locals
        _custom_token_handler = lambda token, tokenized_phrase: '[{}]'.format(token)
        utterance_combo = (('he will want', 'she will want'), ('to play', 'to listen'))
        tokens = ('START', 'PLAY')
        groups = (('None', 1), ('None', 1))
        token_handler_map = {'START': _custom_token_handler}
        _, generator = combine(utterance_combo, tokens, groups, token_handler_map=token_handler_map)
        actual_utterances, actual_handled_tokens, actual_handled_groups = zip(*generator)
        expected_utterances = ('he will want to play', 'he will want to listen',
                               'she will want to play', 'she will want to listen')
        expected_handled_tokens = (('[START]', '[PLAY(to play)]',), ('[START]', '[PLAY(to listen)]',),
                                   ('[START]', '[PLAY(to play)]',), ('[START]', '[PLAY(to listen)]',))
        expected_handled_groups = (('{None([START])}', '{None([PLAY(to play)])}'),
                                   ('{None([START])}', '{None([PLAY(to listen)])}'),
                                   ('{None([START])}', '{None([PLAY(to play)])}'),
                                   ('{None([START])}', '{None([PLAY(to listen)])}'))
        pairs = [(actual_utterances, expected_utterances),
                 (actual_handled_tokens, expected_handled_tokens),
                 (actual_handled_groups, expected_handled_groups)]
        compare_all_pairs(self, pairs)

    def test_token_and_default_token_handler(self) -> None:
        # pylint: disable=too-many-locals
        _start_token_handler = lambda token, tokenized_phrase: '[{}]'.format(token)
        _default_token_handler = lambda token, tokenized_phrase: '[{}(default)]'.format(token)
        utterance_combo = (('he will want', 'she will want'), ('to play', 'to listen'))
        tokens = ('START', 'PLAY')
        groups = (('None', 1), ('None', 1))
        token_handler_map = {'START': _start_token_handler, 'DEFAULT': _default_token_handler}
        _, generator = combine(utterance_combo, tokens, groups, token_handler_map=token_handler_map)
        actual_utterances, actual_handled_tokens, actual_handled_groups = zip(*generator)
        expected_utterances = ('he will want to play', 'he will want to listen',
                               'she will want to play', 'she will want to listen')
        expected_handled_tokens = (('[START]', '[PLAY(default)]',), ('[START]', '[PLAY(default)]',),
                                   ('[START]', '[PLAY(default)]',), ('[START]', '[PLAY(default)]',))
        expected_handled_groups = (('{None([START])}', '{None([PLAY(default)])}'),
                                   ('{None([START])}', '{None([PLAY(default)])}'),
                                   ('{None([START])}', '{None([PLAY(default)])}'),
                                   ('{None([START])}', '{None([PLAY(default)])}'))
        pairs = [(actual_utterances, expected_utterances),
                 (actual_handled_tokens, expected_handled_tokens),
                 (actual_handled_groups, expected_handled_groups)]
        compare_all_pairs(self, pairs)

    def test_combo_options_without_replacement(self) -> None:
        utterance_combo = (('he will want', 'she will want'), ('to play', 'to listen'))
        tokens = ('START', 'PLAY')
        groups = (('None', 1), ('None', 1))
        combo_options = ComboOptions(max_sample_size=6, with_replacement=False, seed=0)
        _, generator = combine(utterance_combo, tokens, groups, combo_options=combo_options)
        actual_utterances, actual_handled_tokens, actual_handled_groups = zip(*generator)
        expected_utterances = ('he will want to play', 'he will want to listen',
                               'she will want to play', 'she will want to listen')
        expected_handled_tokens = (('[START(he will want)]', '[PLAY(to play)]',),
                                   ('[START(he will want)]', '[PLAY(to listen)]',),
                                   ('[START(she will want)]', '[PLAY(to play)]',),
                                   ('[START(she will want)]', '[PLAY(to listen)]',))
        expected_handled_groups = (('{None([START(she will want)])}', '{None([PLAY(to listen)])}'),
                                   ('{None([START(he will want)])}', '{None([PLAY(to listen)])}'),
                                   ('{None([START(he will want)])}', '{None([PLAY(to play)])}'),
                                   ('{None([START(she will want)])}', '{None([PLAY(to play)])}'))
        pairs = [(actual_utterances, expected_utterances),
                 (actual_handled_tokens, expected_handled_tokens),
                 (actual_handled_groups, expected_handled_groups)]
        compare_all_pairs(self, pairs)

    def test_combo_options_with_replacement(self) -> None:
        utterance_combo = (('he will want', 'she will want'), ('to play', 'to listen'))
        tokens = ('START', 'PLAY')
        groups = (('None', 1), ('None', 1))
        combo_options = ComboOptions(max_sample_size=6, with_replacement=True, seed=0)
        _, generator = combine(utterance_combo, tokens, groups, combo_options=combo_options)
        actual_utterances, actual_handled_tokens, actual_handled_groups = zip(*generator)
        expected_utterances = ('she will want to listen', 'she will want to listen',
                               'he will want to play', 'she will want to play',
                               'she will want to listen', 'she will want to listen')
        expected_handled_tokens = (('[START(she will want)]', '[PLAY(to listen)]'),
                                   ('[START(she will want)]', '[PLAY(to listen)]'),
                                   ('[START(he will want)]', '[PLAY(to play)]'),
                                   ('[START(she will want)]', '[PLAY(to play)]'),
                                   ('[START(she will want)]', '[PLAY(to listen)]'),
                                   ('[START(she will want)]', '[PLAY(to listen)]'))
        expected_handled_groups = (('{None([START(she will want)])}', '{None([PLAY(to listen)])}'),
                                   ('{None([START(she will want)])}', '{None([PLAY(to listen)])}'),
                                   ('{None([START(he will want)])}', '{None([PLAY(to play)])}'),
                                   ('{None([START(she will want)])}', '{None([PLAY(to play)])}'),
                                   ('{None([START(she will want)])}', '{None([PLAY(to listen)])}'),
                                   ('{None([START(she will want)])}', '{None([PLAY(to listen)])}'))
        pairs = [(actual_utterances, expected_utterances),
                 (actual_handled_tokens, expected_handled_tokens),
                 (actual_handled_groups, expected_handled_groups)]
        compare_all_pairs(self, pairs)

if __name__ == '__main__':
    unittest.main()
