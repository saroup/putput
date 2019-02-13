from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import cast
from putput.presets.preset import Preset


MYPY = False
if MYPY:
    # pylint: disable=cyclic-import
    from putput.pipeline import _AFTER_JOINING_HOOKS_MAP # pylint: disable=unused-import
    from putput.pipeline import _BEFORE_JOINING_HOOKS_MAP # pylint: disable=unused-import
    from putput.pipeline import _GROUP_HANDLER_MAP # pylint: disable=unused-import
    from putput.types import TOKEN_HANDLER_MAP # pylint: disable=unused-import

class IOB(Preset):
    # pylint: disable=too-few-public-methods
    def __init__(self,
                 *,
                 tokens_to_include: Optional[Sequence[str]] = None,
                 tokens_to_exclude: Optional[Sequence[str]] = None,
                 groups_to_include: Optional[Sequence[str]] = None,
                 groups_to_exclude: Optional[Sequence[str]] = None
                 ) -> None:
        if tokens_to_include and tokens_to_exclude:
            raise ValueError("Cannot specify tokens_to_include AND tokens_to_exclude.")
        if groups_to_include and groups_to_exclude:
            raise ValueError("Cannot specify groups_to_include AND groups_to_exclude")
        self._tokens_to_include = tokens_to_include
        self._tokens_to_exclude = tokens_to_exclude
        self._groups_to_include = groups_to_include
        self._groups_to_exclude = groups_to_exclude

    @staticmethod
    def _iob_token_handler(token: str, phrase: str) -> str:
        tokens = ['{}-{}'.format('B' if i == 0 else 'I', token)
                  for i, _ in enumerate(phrase.replace(" '", "'").split())]
        return ' '.join(tokens)

    @staticmethod
    def _iob_group_handler(group_name: str, handled_tokens: Sequence[str]) -> str:
        num_tokens = 0
        for tokenized_phrase in handled_tokens:
            num_tokens += len(tokenized_phrase.split())
        groups = ['{}-{}'.format('B' if i == 0 else 'I', group_name)
                  for i in range(num_tokens)]
        return ' '.join(groups)

    @staticmethod
    def _exclude_items(items_to_exclude: Sequence[str], iob_handled_items: List[str]) -> Sequence[str]:
        iob_items_to_exclude = []
        for token_to_exclude in items_to_exclude:
            iob_items_to_exclude.append('B-{}'.format(token_to_exclude))
            iob_items_to_exclude.append('I-{}'.format(token_to_exclude))

        for i in range(len(iob_handled_items)): # pylint: disable=consider-using-enumerate
            for token_to_exclude in iob_items_to_exclude:
                iob_handled_items[i] = iob_handled_items[i].replace(token_to_exclude, 'O')
        return tuple(iob_handled_items)

    def _exclude_tokens(self,
                        utterance: str,
                        handled_tokens: Sequence[str],
                        handled_groups: Sequence[str]
                        ) -> Tuple[str, Sequence[str], Sequence[str]]:
        iob_handled_tokens = self._exclude_items(cast(Sequence[str], self._tokens_to_exclude), list(handled_tokens))
        return utterance, iob_handled_tokens, handled_groups

    def _exclude_groups(self,
                        utterance: str,
                        handled_tokens: Sequence[str],
                        handled_groups: Sequence[str]
                        ) -> Tuple[str, Sequence[str], Sequence[str]]:
        iob_handled_groups = self._exclude_items(cast(Sequence[str], self._groups_to_exclude), list(handled_groups))
        return utterance, handled_tokens, iob_handled_groups

    @staticmethod
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

    def _include_tokens(self,
                        utterance: str,
                        handled_tokens: Sequence[str],
                        handled_groups: Sequence[str]
                        ) -> Tuple[str, Sequence[str], Sequence[str]]:
        iob_handled_tokens = self._include_items(cast(Sequence[str], self._tokens_to_include), list(handled_tokens))
        return utterance, iob_handled_tokens, handled_groups

    def _include_groups(self,
                        utterance: str,
                        handled_tokens: Sequence[str],
                        handled_groups: Sequence[str]
                        ) -> Tuple[str, Sequence[str], Sequence[str]]:
        iob_handled_groups = self._include_items(cast(Sequence[str], self._groups_to_include), list(handled_groups))
        return utterance, handled_tokens, iob_handled_groups

    def init_preset(self,
                    *,
                    token_handler_map: Optional['TOKEN_HANDLER_MAP'] = None,
                    group_handler_map: Optional['_GROUP_HANDLER_MAP'] = None,
                    before_joining_hooks_map: Optional['_BEFORE_JOINING_HOOKS_MAP'] = None,
                    after_joining_hooks_map: Optional['_AFTER_JOINING_HOOKS_MAP'] = None
                    ) -> Tuple[Optional['TOKEN_HANDLER_MAP'],
                               Optional['_GROUP_HANDLER_MAP'],
                               Optional['_BEFORE_JOINING_HOOKS_MAP'],
                               Optional['_AFTER_JOINING_HOOKS_MAP']]:
        iob_token_handler_map = dict(token_handler_map) if token_handler_map else {}
        iob_group_handler_map = dict(group_handler_map) if group_handler_map else {}

        iob_token_handler_map.update({'DEFAULT': self._iob_token_handler})
        iob_group_handler_map.update({'DEFAULT': self._iob_group_handler})

        iob_after_joining_hooks_map = dict(after_joining_hooks_map) if after_joining_hooks_map else {}
        iob_before_joining_hooks_map = dict(before_joining_hooks_map) if before_joining_hooks_map else {}

        if self._tokens_to_exclude:
            iob_after_joining_hooks_map.update({'DEFAULT': (self._exclude_tokens,)})
        if self._tokens_to_include:
            iob_after_joining_hooks_map.update({'DEFAULT': (self._include_tokens,)})
        if self._groups_to_include:
            iob_after_joining_hooks_map.update({'GROUP_DEFAULT': (self._include_groups,)})
        if self._groups_to_exclude:
            iob_after_joining_hooks_map.update({'GROUP_DEFAULT': (self._exclude_groups,)})

        return iob_token_handler_map, iob_group_handler_map, iob_before_joining_hooks_map, iob_after_joining_hooks_map
