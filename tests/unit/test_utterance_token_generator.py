import unittest
from typing import Callable, Mapping, Optional, Tuple

from putput.joiner import CombinationOptions
from putput.pattern_definition_processor import TokenPattern, UtterancePattern # pylint: disable=unused-import
from putput.utterance_token_generator import generate_utterances_and_tokens


class TestUtteranceTokenGenerator(unittest.TestCase):

    def _verify(self,
                utterance_pattern: UtterancePattern,
                tokens: Tuple[str, ...],
                expected_utterances: Tuple[str, ...],
                expected_tokens_iterable: Tuple[str, ...],
                token_handlers: Optional[Mapping[str, Callable[[str, str], str]]] = None,
                combination_options: Optional[CombinationOptions] = None
                ) -> None:
        # pylint: disable=too-many-arguments
        actual_utterances = []
        actual_tokens_iterable = []
        ut_gen = generate_utterances_and_tokens(utterance_pattern,
                                                tokens,
                                                token_handlers=token_handlers,
                                                combination_options=combination_options)
        for actual_utterance, actual_tokens in ut_gen:
            self.assertIn(actual_utterance, expected_utterances)
            self.assertIn(actual_tokens, expected_tokens_iterable)
            actual_utterances.append(actual_utterance)
            actual_tokens_iterable.append(actual_tokens)
        if combination_options:
            self.assertLessEqual(len(actual_utterances), combination_options.max_sample_size)
            self.assertLessEqual(len(actual_tokens_iterable), combination_options.max_sample_size)
        else:
            self.assertEqual(len(actual_utterances), len(expected_utterances))
            self.assertEqual(len(actual_tokens_iterable), len(expected_tokens_iterable))

    def test_one_token_pattern(self) -> None:
        # single tokens
        token_pattern = (('hey speaker',),) # type: TokenPattern
        utterance_pattern = ((token_pattern,),) # type: UtterancePattern
        tokens = ('WAKE',)

        expected_utterances = ('hey speaker',) # type: Tuple[str, ...]
        expected_tokens_iterable = ('[WAKE]',) # type: Tuple[str, ...]
        self._verify(utterance_pattern, tokens, expected_utterances, expected_tokens_iterable)

        # one or more tokens
        token_pattern = (('hey', 'ok'), ('speaker', 'sound system'))
        utterance_pattern = ((token_pattern,),)
        tokens = ('WAKE',)

        expected_utterances = ('hey speaker', 'hey sound system', 'ok speaker', 'ok sound system')
        expected_tokens_iterable = ('[WAKE]', '[WAKE]', '[WAKE]', '[WAKE]')
        self._verify(utterance_pattern, tokens, expected_utterances, expected_tokens_iterable)

    def test_multiple_token_patterns(self) -> None:
        # single tokens
        token_pattern_one = (('hey speaker',),) # type: TokenPattern
        token_pattern_two = (('ok speaker',),) # type: TokenPattern
        token_patterns = (token_pattern_one, token_pattern_two) # type: Tuple[TokenPattern, ...]
        utterance_pattern = (token_patterns,)
        tokens = ('WAKE',)

        expected_utterances = ('hey speaker', 'ok speaker') # type: Tuple[str, ...]
        expected_tokens_iterable = ('[WAKE]', '[WAKE]') # type: Tuple[str, ...]
        self._verify(utterance_pattern, tokens, expected_utterances, expected_tokens_iterable)

        # one or more tokens
        token_pattern_one = (('he', 'she'), ('wants', 'needs'), ('to play', 'to listen to'))
        token_pattern_two = (('play', 'turn on'),)
        token_patterns = (token_pattern_one, token_pattern_two)
        utterance_pattern = (token_patterns,)
        tokens = ('WAKE',)

        expected_utterances = ('he wants to play', 'he wants to listen to',
                               'he needs to play', 'he needs to listen to',
                               'she wants to play', 'she wants to listen to',
                               'she needs to play', 'she needs to listen to',
                               'play', 'turn on')

        expected_tokens_iterable = ('[WAKE]',) * 10
        self._verify(utterance_pattern, tokens, expected_utterances, expected_tokens_iterable)

    def test_utterance_pattern(self) -> None:
        wake_token_patterns = ((('hey speaker',),), (('ok speaker',),))
        play_token_patterns = ((('he', 'she'), ('wants', 'needs'), ('to play', 'to listen to')), (('play', 'turn on'),))
        utterance_pattern = (wake_token_patterns, play_token_patterns)
        tokens = ('WAKE', 'PLAY')
        expected_utterances = ('hey speaker he wants to play', 'hey speaker he wants to listen to',
                               'hey speaker he needs to play', 'hey speaker he needs to listen to',
                               'hey speaker she wants to play', 'hey speaker she wants to listen to',
                               'hey speaker she needs to play', 'hey speaker she needs to listen to',
                               'hey speaker play', 'hey speaker turn on',
                               'ok speaker he wants to play', 'ok speaker he wants to listen to',
                               'ok speaker he needs to play', 'ok speaker he needs to listen to',
                               'ok speaker she wants to play', 'ok speaker she wants to listen to',
                               'ok speaker she needs to play', 'ok speaker she needs to listen to',
                               'ok speaker play', 'ok speaker turn on')
        expected_tokens_iterable = ('[WAKE] [PLAY]',) * 20
        self._verify(utterance_pattern, tokens, expected_utterances, expected_tokens_iterable)

    def test_combination_options(self) -> None:
        # single tokens
        token_pattern_one = (('hey speaker',),) # type: TokenPattern
        token_pattern_two = (('ok speaker',),) # type: TokenPattern
        token_patterns = (token_pattern_one, token_pattern_two) # type: Tuple[TokenPattern, ...]
        utterance_pattern = (token_patterns,)
        tokens = ('WAKE',)

        expected_utterances = ('hey speaker', 'ok speaker') # type: Tuple[str, ...]
        expected_tokens_iterable = ('[WAKE]', '[WAKE]') # type: Tuple[str, ...]
        combination_options = CombinationOptions(max_sample_size=1, seed=0)
        self._verify(utterance_pattern,
                     tokens,
                     expected_utterances,
                     expected_tokens_iterable,
                     combination_options=combination_options)

    def test_token_handler(self) -> None:
        wake_token_patterns = ((('hey speaker',),),)
        play_token_patterns = ((('play',),),)
        utterance_pattern = (wake_token_patterns, play_token_patterns)
        tokens = ('WAKE', 'PLAY')

        expected_utterances = ('hey speaker play',)
        expected_tokens_iterable = ('[WAKE(hey speaker)] [PLAY]',)

        _custom_token_handler = lambda token, tokenized_phrase: '[{}({})]'.format(token, tokenized_phrase)

        # specific token
        token_handlers = {'WAKE': _custom_token_handler}

        for actual_utterance, actual_tokens in generate_utterances_and_tokens(utterance_pattern,
                                                                              tokens,
                                                                              token_handlers=token_handlers):
            self.assertIn(actual_utterance, expected_utterances)
            self.assertIn(actual_tokens, expected_tokens_iterable)

        # default token
        token_handlers = {'DEFAULT': _custom_token_handler}
        expected_tokens_iterable = ('[WAKE(hey speaker)] [PLAY(play)]',)
        for actual_utterance, actual_tokens in generate_utterances_and_tokens(utterance_pattern,
                                                                              tokens,
                                                                              token_handlers=token_handlers):
            self.assertIn(actual_utterance, expected_utterances)
            self.assertIn(actual_tokens, expected_tokens_iterable)

        # default and specific token
        _play_token_handler = lambda token, tokenized_phrase: '[{}({})]'.format(token, tokenized_phrase).upper()
        token_handlers = {'DEFAULT': _custom_token_handler, 'PLAY': _play_token_handler}
        expected_tokens_iterable = ('[WAKE(hey speaker)] [PLAY(PLAY)]',)
        for actual_utterance, actual_tokens in generate_utterances_and_tokens(utterance_pattern,
                                                                              tokens,
                                                                              token_handlers=token_handlers):
            self.assertIn(actual_utterance, expected_utterances)
            self.assertIn(actual_tokens, expected_tokens_iterable)
