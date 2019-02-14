# https://en.wikipedia.org/wiki/Inside%E2%80%93outside%E2%80%93beginning_(tagging)
from functools import partial
from typing import Callable
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple

MYPY = False
if MYPY: # pragma: no cover
    # pylint: disable=cyclic-import
    from putput.pipeline import _AFTER_JOINING_HOOKS_MAP # pylint: disable=unused-import
    from putput.pipeline import _BEFORE_JOINING_HOOKS_MAP # pylint: disable=unused-import
    from putput.pipeline import _GROUP_HANDLER_MAP # pylint: disable=unused-import
    from putput.types import TOKEN_HANDLER_MAP # pylint: disable=unused-import

def preset(*,
           tokens_to_include: Optional[Sequence[str]] = None,
           tokens_to_exclude: Optional[Sequence[str]] = None,
           groups_to_include: Optional[Sequence[str]] = None,
           groups_to_exclude: Optional[Sequence[str]] = None
           ) -> Callable:
    return partial(_preset,
                   _iob_token_handler,
                   _iob_group_handler,
                   tokens_to_include=tokens_to_include,
                   tokens_to_exclude=tokens_to_exclude,
                   groups_to_include=groups_to_include,
                   groups_to_exclude=groups_to_exclude)

def _preset(token_handler: Callable[[str, str], str],
            group_handler: Callable[[str, Sequence[str]], str],
            *,
            tokens_to_include: Optional[Sequence[str]] = None,
            tokens_to_exclude: Optional[Sequence[str]] = None,
            groups_to_include: Optional[Sequence[str]] = None,
            groups_to_exclude: Optional[Sequence[str]] = None,
            token_handler_map: Optional['TOKEN_HANDLER_MAP'] = None,
            group_handler_map: Optional['_GROUP_HANDLER_MAP'] = None,
            before_joining_hooks_map: Optional['_BEFORE_JOINING_HOOKS_MAP'] = None,
            after_joining_hooks_map: Optional['_AFTER_JOINING_HOOKS_MAP'] = None
            ) -> Tuple[Optional['TOKEN_HANDLER_MAP'],
                       Optional['_GROUP_HANDLER_MAP'],
                       Optional['_BEFORE_JOINING_HOOKS_MAP'],
                       Optional['_AFTER_JOINING_HOOKS_MAP']]:
    # pylint: disable=too-many-locals

    if tokens_to_include and tokens_to_exclude:
        raise ValueError("Cannot specify tokens_to_include AND tokens_to_exclude.")
    if groups_to_include and groups_to_exclude:
        raise ValueError("Cannot specify groups_to_include AND groups_to_exclude")

    iob_token_handler_map = dict(token_handler_map) if token_handler_map else {}
    iob_group_handler_map = dict(group_handler_map) if group_handler_map else {}

    iob_token_handler_map.update({'DEFAULT': token_handler})
    iob_group_handler_map.update({'DEFAULT': group_handler})

    iob_after_joining_hooks_map = dict(after_joining_hooks_map) if after_joining_hooks_map else {}
    iob_before_joining_hooks_map = dict(before_joining_hooks_map) if before_joining_hooks_map else {}

    if tokens_to_exclude:
        exclude_tokens_hook = partial(_exclude_tokens, tokens_to_exclude=tokens_to_exclude)
        existing_hooks = iob_after_joining_hooks_map.get('DEFAULT')
        if existing_hooks:
            updated_hooks = (exclude_tokens_hook,) + tuple(existing_hooks)
        else:
            updated_hooks = (exclude_tokens_hook,)
        iob_after_joining_hooks_map.update({'DEFAULT': updated_hooks})
    if tokens_to_include:
        include_tokens_hook = partial(_include_tokens, tokens_to_include=tokens_to_include)
        existing_hooks = iob_after_joining_hooks_map.get('DEFAULT')
        if existing_hooks:
            updated_hooks = (include_tokens_hook,) + tuple(existing_hooks)
        else:
            updated_hooks = (include_tokens_hook,)
        iob_after_joining_hooks_map.update({'DEFAULT': updated_hooks})
    if groups_to_include:
        include_groups_hook = partial(_include_groups, groups_to_include=groups_to_include)
        existing_hooks = iob_after_joining_hooks_map.get('GROUP_DEFAULT')
        if existing_hooks:
            updated_hooks = (include_groups_hook,) + tuple(existing_hooks)
        else:
            updated_hooks = (include_groups_hook,)
        iob_after_joining_hooks_map.update({'GROUP_DEFAULT': updated_hooks})
    if groups_to_exclude:
        exclude_groups_hook = partial(_exclude_groups, groups_to_exclude=groups_to_exclude)
        existing_hooks = iob_after_joining_hooks_map.get('GROUP_DEFAULT')
        if existing_hooks:
            updated_hooks = (exclude_groups_hook,) + tuple(existing_hooks)
        else:
            updated_hooks = (exclude_groups_hook,)
        iob_after_joining_hooks_map.update({'GROUP_DEFAULT': updated_hooks})
    return iob_token_handler_map, iob_group_handler_map, iob_before_joining_hooks_map, iob_after_joining_hooks_map

def _iob_token_handler(token: str, phrase: str) -> str:
    tokens = ['{}-{}'.format('B' if i == 0 else 'I', token)
              for i, _ in enumerate(phrase.replace(" '", "'").split())]
    return ' '.join(tokens)

def _iob_group_handler(group_name: str, handled_tokens: Sequence[str]) -> str:
    num_tokens = 0
    for tokenized_phrase in handled_tokens:
        num_tokens += len(tokenized_phrase.split())
    groups = ['{}-{}'.format('B' if i == 0 else 'I', group_name)
              for i in range(num_tokens)]
    return ' '.join(groups)

def _exclude_items(items_to_exclude: Sequence[str], iob_handled_items: List[str]) -> Sequence[str]:
    iob_items_to_exclude = []
    for token_to_exclude in items_to_exclude:
        iob_items_to_exclude.append('B-{}'.format(token_to_exclude))
        iob_items_to_exclude.append('I-{}'.format(token_to_exclude))

    for i in range(len(iob_handled_items)): # pylint: disable=consider-using-enumerate
        for token_to_exclude in iob_items_to_exclude:
            iob_handled_items[i] = iob_handled_items[i].replace(token_to_exclude, 'O')
    return tuple(iob_handled_items)

def _include_items(items_to_include: Sequence[str], iob_handled_items: List[str]) -> Sequence[str]:
    iob_items_to_include = set()
    for item_to_include in items_to_include:
        iob_items_to_include.add('B-{}'.format(item_to_include))
        iob_items_to_include.add('I-{}'.format(item_to_include))

    for i, handled_item in enumerate(iob_handled_items):
        split_handled_item = handled_item.split()
        for j, component in enumerate(split_handled_item):
            if component not in iob_items_to_include:
                split_handled_item[j] = 'O'
        iob_handled_items[i] = ' '.join(split_handled_item)
    return tuple(iob_handled_items)

def _exclude_tokens(utterance: str,
                    handled_tokens: Sequence[str],
                    handled_groups: Sequence[str],
                    tokens_to_exclude: Sequence[str]
                    ) -> Tuple[str, Sequence[str], Sequence[str]]:
    iob_handled_tokens = _exclude_items(tokens_to_exclude, list(handled_tokens))
    return utterance, iob_handled_tokens, handled_groups

def _exclude_groups(utterance: str,
                    handled_tokens: Sequence[str],
                    handled_groups: Sequence[str],
                    groups_to_exclude: Sequence[str]
                    ) -> Tuple[str, Sequence[str], Sequence[str]]:
    iob_handled_groups = _exclude_items(groups_to_exclude, list(handled_groups))
    return utterance, handled_tokens, iob_handled_groups

def _include_tokens(utterance: str,
                    handled_tokens: Sequence[str],
                    handled_groups: Sequence[str],
                    tokens_to_include: Sequence[str]
                    ) -> Tuple[str, Sequence[str], Sequence[str]]:
    iob_handled_tokens = _include_items(tokens_to_include, list(handled_tokens))
    return utterance, iob_handled_tokens, handled_groups

def _include_groups(utterance: str,
                    handled_tokens: Sequence[str],
                    handled_groups: Sequence[str],
                    groups_to_include: Sequence[str]
                    ) -> Tuple[str, Sequence[str], Sequence[str]]:
    iob_handled_groups = _include_items(groups_to_include, list(handled_groups))
    return utterance, handled_tokens, iob_handled_groups
