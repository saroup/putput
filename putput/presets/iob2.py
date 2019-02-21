# https://en.wikipedia.org/wiki/Inside%E2%80%93outside%E2%80%93beginning_(tagging)
from functools import partial
from typing import Callable
from typing import List
from typing import Mapping
from typing import Optional
from typing import Sequence
from typing import Tuple


def preset(*,
           tokens_to_include: Optional[Sequence[str]] = None,
           tokens_to_exclude: Optional[Sequence[str]] = None,
           groups_to_include: Optional[Sequence[str]] = None,
           groups_to_exclude: Optional[Sequence[str]] = None
           ) -> Callable:
    return partial(_preset,
                   tokens_to_include=tokens_to_include,
                   tokens_to_exclude=tokens_to_exclude,
                   groups_to_include=groups_to_include,
                   groups_to_exclude=groups_to_exclude)

def _preset(*,
            tokens_to_include: Optional[Sequence[str]] = None,
            tokens_to_exclude: Optional[Sequence[str]] = None,
            groups_to_include: Optional[Sequence[str]] = None,
            groups_to_exclude: Optional[Sequence[str]] = None
            ) -> Mapping:
    if tokens_to_include and tokens_to_exclude:
        raise ValueError("Cannot specify tokens_to_include AND tokens_to_exclude.")
    if groups_to_include and groups_to_exclude:
        raise ValueError("Cannot specify groups_to_include AND groups_to_exclude")

    token_handler_map = {'DEFAULT': _iob_token_handler}
    group_handler_map = {'DEFAULT': _iob_group_handler}

    combo_hooks_map = {}

    tokens_hook = None
    if tokens_to_include:
        tokens_hook = partial(_include_tokens, tokens_to_include=tokens_to_include)
    if tokens_to_exclude:
        tokens_hook = partial(_exclude_tokens, tokens_to_exclude=tokens_to_exclude)
    if tokens_hook:
        combo_hooks_map.update({'DEFAULT': (tokens_hook,)})

    groups_hook = None
    if groups_to_include:
        groups_hook = partial(_include_groups, groups_to_include=groups_to_include)
    if groups_to_exclude:
        groups_hook = partial(_exclude_groups, groups_to_exclude=groups_to_exclude)
    if groups_hook:
        combo_hooks_map.update({'GROUP_DEFAULT': (groups_hook,)})
    return {
        'token_handler_map': token_handler_map,
        'group_handler_map': group_handler_map,
        'combo_hooks_map': combo_hooks_map
    }

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
