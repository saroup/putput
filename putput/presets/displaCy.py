import re
from typing import Callable
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Mapping
import json

MYPY = False
if MYPY: # pragma: no cover
    # pylint: disable=cyclic-import
    from putput.pipeline import _AFTER_JOINING_HOOKS_MAP # pylint: disable=unused-import
    from putput.pipeline import _BEFORE_JOINING_HOOKS_MAP # pylint: disable=unused-import
    from putput.pipeline import _GROUP_HANDLER_MAP # pylint: disable=unused-import
    from putput.types import TOKEN_HANDLER_MAP # pylint: disable=unused-import

def preset() -> Callable:
    return _preset

def _preset(token_handler_map: Optional['TOKEN_HANDLER_MAP'] = None,
            group_handler_map: Optional['_GROUP_HANDLER_MAP'] = None,
            before_joining_hooks_map: Optional['_BEFORE_JOINING_HOOKS_MAP'] = None,
            after_joining_hooks_map: Optional['_AFTER_JOINING_HOOKS_MAP'] = None
            ) -> Tuple[Optional['TOKEN_HANDLER_MAP'],
                       Optional['_GROUP_HANDLER_MAP'],
                       Optional['_BEFORE_JOINING_HOOKS_MAP'],
                       Optional['_AFTER_JOINING_HOOKS_MAP']]:
    # visualize groups AND tokens
    iob_after_joining_hooks_map = dict(after_joining_hooks_map) if after_joining_hooks_map else {}
    existing_tokens_hooks = iob_after_joining_hooks_map.get('DEFAULT')
    if existing_tokens_hooks:
        updated_tokens_hooks = (_handled_tokens_to_ent,) + tuple(_ for _ in existing_tokens_hooks)
    else:
        updated_tokens_hooks = (_handled_tokens_to_ent,)
    iob_after_joining_hooks_map.update({'DEFAULT': updated_tokens_hooks})

    existing_groups_hooks = iob_after_joining_hooks_map.get('GROUP_DEFAULT')
    if existing_groups_hooks:
        updated_groups_hooks = (_handled_groups_to_ent,) + tuple(_ for _ in existing_groups_hooks)
    else:
        updated_groups_hooks = (_handled_groups_to_ent,)
    iob_after_joining_hooks_map.update({'GROUP_DEFAULT': updated_groups_hooks})

    return token_handler_map, group_handler_map, before_joining_hooks_map, iob_after_joining_hooks_map

def _convert_to_ents(utterance: str,
                     handled_items: Sequence[str],
                     label_extractor: Callable[[str], str]
                     ) -> Tuple[Mapping]:
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
    return tuple(ents)

def _handled_groups_to_ent(utterance: str,
                           handled_tokens: Sequence[str],
                           handled_groups: Sequence[str]
                           ) -> Tuple[str, Sequence[str], Sequence[str]]:
    label_extractor = lambda s: s[s.index('{') + 1: s.index('(')]
    ents = _convert_to_ents(utterance, handled_groups, label_extractor)
    return utterance, handled_tokens, json.dumps(ents)

def _handled_tokens_to_ent(utterance: str,
                           handled_tokens: Sequence[str],
                           handled_groups: Sequence[str]
                           ) -> Tuple[str, Sequence[str], Sequence[str]]:
    label_extractor = lambda s: s[s.index('[') + 1: s.index('(')]
    ents = _convert_to_ents(utterance, handled_tokens, label_extractor)
    return utterance, json.dumps(ents), handled_groups
