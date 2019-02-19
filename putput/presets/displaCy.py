import re
from typing import Callable
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Mapping

MYPY = False
if MYPY: # pragma: no cover
    # pylint: disable=cyclic-import
    from putput.pipeline import _AFTER_JOINING_HOOKS_MAP # pylint: disable=unused-import
    from putput.pipeline import _BEFORE_JOINING_HOOKS_MAP # pylint: disable=unused-import
    from putput.pipeline import _FINAL_HOOK # pylint: disable=unused-import
    from putput.pipeline import _GROUP_HANDLER_MAP # pylint: disable=unused-import
    from putput.types import TOKEN_HANDLER_MAP # pylint: disable=unused-import


def preset() -> Callable:
    return _preset

def _preset() -> Tuple[Optional['TOKEN_HANDLER_MAP'],
                       Optional['_GROUP_HANDLER_MAP'],
                       Optional['_BEFORE_JOINING_HOOKS_MAP'],
                       Optional['_AFTER_JOINING_HOOKS_MAP'],
                       Optional['_FINAL_HOOK']]:
    after_joining_hooks_map = {}
    after_joining_hooks_map['DEFAULT'] = (_handled_tokens_to_ent,)
    after_joining_hooks_map['GROUP_DEFAULT'] = (_handled_groups_to_ent,)
    return (None, None, None, after_joining_hooks_map, _convert_to_displaCy_visualizer)

def _convert_to_ents(utterance: str,
                     handled_items: Sequence[str],
                     label_extractor: Callable[[str], str]
                     ) -> Sequence[Mapping]:
    ents = []
    offset = 0
    for handled_item in handled_items:
        label = label_extractor(handled_item)
        phrase = ' '.join(re.findall(r'\(([^()]+)\)', handled_item))
        start = offset + utterance[offset:].index(phrase)
        end = start + len(phrase)
        ent = {
            'start': start,
            'end': end,
            'label': label
        }
        ents.append(ent)
        offset = end
    return ents

def _handled_groups_to_ent(utterance: str,
                           handled_tokens: Sequence,
                           handled_groups: Sequence[str]
                           ) -> Tuple[str, Sequence, Sequence[Mapping]]:
    label_extractor = lambda s: s[s.index('{') + 1: s.index('(')]
    ents = _convert_to_ents(utterance, handled_groups, label_extractor)
    return utterance, handled_tokens, ents

def _handled_tokens_to_ent(utterance: str,
                           handled_tokens: Sequence[str],
                           handled_groups: Sequence
                           ) -> Tuple[str, Sequence[Mapping], Sequence]:
    label_extractor = lambda s: s[s.index('[') + 1: s.index('(')]
    ents = _convert_to_ents(utterance, handled_tokens, label_extractor)
    return utterance, ents, handled_groups

def _convert_to_displaCy_visualizer(utterance: str,
                                    handled_tokens: Sequence[Mapping],
                                    handled_groups: Sequence[Mapping]):
    # https://spacy.io/usage/visualizers#manual-usage
    # ent usage
    token_visualizer = {
        'text': utterance,
        'ents': handled_tokens,
        'title': 'Tokens'
    }
    group_visualizer = {
        'text': utterance,
        'ents': handled_groups,
        'title': 'Groups'
    }
    return (token_visualizer, group_visualizer)
