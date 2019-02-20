"""This module provides functionality to generate utterances and tokens after processing the pattern definition."""
from functools import reduce
from typing import Iterable
from typing import Optional
from typing import Sequence
from typing import Tuple

from putput.joiner import ComboOptions
from putput.joiner import join_combo
from putput.types import COMBO
from putput.types import TOKEN_HANDLER
from putput.types import TOKEN_HANDLER_MAP


def combine(utterance_combo: COMBO,
            tokens: Sequence[str],
            *,
            token_handler_map: Optional[TOKEN_HANDLER_MAP] = None,
            combo_options: Optional[ComboOptions] = None
            ) -> Tuple[int, Iterable[Tuple[str, Sequence[str]]]]:
    # TODO: combo options should behave this way too in joiner
    sample_size = reduce(lambda x, y: x * y, (len(item) for item in utterance_combo))
    if combo_options:
        sample_size = combo_options.max_sample_size

    # TODO: consider if these should really be nested
    def _combine() -> Iterable[Tuple[str, Sequence[str]]]:
        handled_token_combo = _compute_handled_token_combo(utterance_combo, tokens, token_handler_map=token_handler_map)
        combo_indices = tuple(tuple(i for i in range(len(component))) for component in utterance_combo)
        for indices in join_combo(combo_indices, combo_options=combo_options):
            utterance = []
            handled_tokens = []
            for utterance_component, token_component, index in zip(utterance_combo,
                                                                   handled_token_combo,
                                                                   indices):
                utterance.append(utterance_component[index])
                handled_tokens.append(token_component[index])
            yield ' '.join(utterance), tuple(handled_tokens)
    return sample_size, _combine()

def _compute_handled_token_combo(utterance_combo: COMBO,
                                 tokens: Sequence[str],
                                 *,
                                 token_handler_map: Optional[TOKEN_HANDLER_MAP] = None
                                 ) -> COMBO:
    handled_token_combo = []
    for utterance_component, token in zip(utterance_combo, tokens):
        token_components = tuple(_get_token_handler(token, token_handler_map=token_handler_map)(token, phrase)
                                 for phrase in utterance_component)
        handled_token_combo.append(token_components)
    return tuple(handled_token_combo)

def _get_token_handler(token: str,
                       *,
                       token_handler_map: Optional[TOKEN_HANDLER_MAP] = None
                       ) -> TOKEN_HANDLER:
    default_token_handler = lambda token, phrase: '[{}({})]'.format(token, phrase)
    if token_handler_map:
        return token_handler_map.get(token) or token_handler_map.get('DEFAULT') or default_token_handler
    return default_token_handler
