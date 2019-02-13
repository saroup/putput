from pathlib import Path
from typing import Any
from typing import Callable
from typing import Dict  # pylint: disable=unused-import
from typing import Iterable
from typing import Mapping
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import TypeVar
from typing import Union  # pylint: disable=unused-import
from typing import cast
from typing import no_type_check

from putput.generator import generate_utterance_combo_tokens_and_groups
from putput.generator import generate_utterances_and_handled_tokens
from putput.joiner import ComboOptions
from putput.types import COMBO
from putput.types import GROUP
from putput.types import TOKEN_HANDLER_MAP
from putput.types import TOKEN_PATTERNS_MAP

_GROUP_HANDLER = Callable[[str, Sequence[str]], str]
_BEFORE_JOINING_HOOK_ARGS = Tuple[COMBO, Sequence[str], Sequence[GROUP]]
_BEFORE_JOINING_HOOK = Callable[[_BEFORE_JOINING_HOOK_ARGS], _BEFORE_JOINING_HOOK_ARGS]
_AFTER_JOINING_HOOK_ARGS = Tuple[str, Sequence[str], Sequence[str]]
_AFTER_JOINING_HOOK = Callable[[_AFTER_JOINING_HOOK_ARGS], _AFTER_JOINING_HOOK_ARGS]
_HOOK_ARGS = TypeVar('_HOOK_ARGS', _BEFORE_JOINING_HOOK_ARGS, _AFTER_JOINING_HOOK_ARGS)
_GROUP_HANDLER_MAP = Mapping[str, _GROUP_HANDLER]

_HOOKS_MAP = Mapping[Any, Any]
_BEFORE_JOINING_HOOKS_MAP = Mapping[Any, Sequence[_BEFORE_JOINING_HOOK]]
_AFTER_JOINING_HOOKS_MAP = Mapping[Any, Sequence[_AFTER_JOINING_HOOK]]
_COMBO_OPTIONS_MAP = Mapping[Any, ComboOptions]
# TODO: check whether we need any instead of union
# _HOOKS_MAP=Mapping[Union[str, Tuple[str, ...]], Union[Sequence[_BEFORE_JOINING_HOOK], Sequence[_AFTER_JOINING_HOOK]]]
# _BEFORE_JOINING_HOOKS_MAP = Mapping[Union[str, Tuple[str, ...]], Sequence[_BEFORE_JOINING_HOOK]]
# _AFTER_JOINING_HOOKS_MAP = Mapping[Union[str, Tuple[str, ...]], Sequence[_AFTER_JOINING_HOOK]]
# _COMBO_OPTIONS_MAP = Mapping[Union[str, Tuple[str, ...]], ComboOptions]

class Pipeline:
    def __init__(self) -> None:
        self._before_joining_hooks_map = {} # type: Dict[Union[str, Tuple[str, ...]], Sequence[_BEFORE_JOINING_HOOK]]
        self._after_joining_hooks_map = {} # type: Dict[Union[str, Tuple[str, ...]], Sequence[_AFTER_JOINING_HOOK]]

    def register_hooks(self, hooks_map: _HOOKS_MAP, stage: str) -> None:
        if stage == 'BEFORE_JOINING':
            before_joining_hooks_map = cast(_BEFORE_JOINING_HOOKS_MAP, hooks_map)
            self._before_joining_hooks_map.update(before_joining_hooks_map)
        elif stage == 'AFTER_JOINING':
            after_joining_hooks_map = cast(_AFTER_JOINING_HOOKS_MAP, hooks_map)
            self._after_joining_hooks_map.update(after_joining_hooks_map)
        else:
            err_msg = '{} is invalid. Please choose "BEFORE_JOINING" or "AFTER_JOINING"'.format(stage)
            raise ValueError(err_msg)

    def flow(self,
             pattern_def_path: Path,
             *,
             dynamic_token_patterns_map: Optional[TOKEN_PATTERNS_MAP] = None,
             token_handler_map: Optional[TOKEN_HANDLER_MAP] = None,
             group_handler_map: Optional[_GROUP_HANDLER_MAP] = None,
             combo_options_map: Optional[_COMBO_OPTIONS_MAP] = None
             ) -> Iterable[Tuple[str, str, str]]:
        # pylint: disable=too-many-arguments, too-many-locals
        before_gen = generate_utterance_combo_tokens_and_groups(pattern_def_path,
                                                                dynamic_token_patterns_map=dynamic_token_patterns_map)
        for utterance_combo, tokens, groups in before_gen:
            if self._before_joining_hooks_map:
                utterance_combo, tokens = self._execute_joining_hooks(tokens,
                                                                      (utterance_combo, tokens),
                                                                      'BEFORE_JOINING')

            combo_options = None
            if combo_options_map:
                combo_options = self._get_combo_options(tokens, combo_options_map)

            after_joining_generator = generate_utterances_and_handled_tokens(utterance_combo,
                                                                             tokens,
                                                                             token_handler_map=token_handler_map,
                                                                             combo_options=combo_options)
            for utterance, handled_tokens in after_joining_generator:
                handled_groups = _compute_handled_groups(groups, handled_tokens, group_handler_map=group_handler_map)
                if self._after_joining_hooks_map:
                    group_names = tuple([group[0] for group in groups])
                    utterance, handled_tokens, handled_groups = self._execute_joining_hooks(tokens,
                                                                                            (utterance,
                                                                                             handled_tokens,
                                                                                             handled_groups),
                                                                                            'AFTER_JOINING',
                                                                                            group_names=group_names)
                yield utterance, ' '.join(handled_tokens), ' '.join(handled_groups)

    @staticmethod
    def _get_combo_options(tokens: Sequence[str],
                           combo_options_map: _COMBO_OPTIONS_MAP,
                           ) -> Optional[ComboOptions]:
        options_map = {} # type: Dict[Union[str, Tuple[str, ...]], ComboOptions]
        options_map.update(combo_options_map)
        key = tuple(tokens)
        return options_map.get(key) or options_map.get('DEFAULT')

    @no_type_check
    def _execute_joining_hooks(self,
                               tokens: Sequence[str],
                               args: _HOOK_ARGS,
                               stage: str,
                               *,
                               group_names: Optional[Sequence[str]] = None
                               ) -> _HOOK_ARGS:
        hooks_map = self._before_joining_hooks_map if stage == 'BEFORE_JOINING' else self._after_joining_hooks_map
        token_key = tuple(tokens) if tokens in hooks_map else 'DEFAULT'
        if token_key in hooks_map:
            for hook in hooks_map[token_key]:
                args = hook(*args)
        if group_names:
            group_name_key = tuple(group_names) if group_names in hooks_map else 'GROUP_DEFAULT'
            if group_name_key in hooks_map:
                for hook in hooks_map[group_name_key]:
                    args = hook(*args)
        return args

def _compute_handled_groups(groups: Sequence[GROUP],
                            handled_tokens: Sequence[str],
                            *,
                            group_handler_map: Optional[_GROUP_HANDLER_MAP] = None
                            ) -> Sequence[str]:
    start_index = 0
    handled_groups = []
    for group in groups:
        group_name = group[0]
        end_index = group[1]
        group_handler = _get_group_handler(group_name, group_handler_map=group_handler_map)
        handled_group = group_handler(group_name, handled_tokens[start_index: start_index + end_index])
        handled_groups.append(handled_group)
        start_index += end_index
    return tuple(handled_groups)

def _get_group_handler(group_name: str,
                       *,
                       group_handler_map: Optional[_GROUP_HANDLER_MAP] = None
                       ) -> _GROUP_HANDLER:
    default_group_handler = lambda group_name, handled_tokens: '{{{}({})}}'.format(group_name, ' '.join(handled_tokens))
    if group_handler_map:
        return group_handler_map.get(group_name) or group_handler_map.get('DEFAULT') or default_group_handler
    return default_group_handler
