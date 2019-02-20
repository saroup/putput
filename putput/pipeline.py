import logging
import textwrap
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
from typing import Union
from typing import no_type_check

from tqdm import tqdm

from putput.expander import expand
from putput.combiner import combine
from putput.joiner import ComboOptions
from putput.logger import get_logger
from putput.presets.factory import get_preset
from putput.types import COMBO
from putput.types import GROUP
from putput.types import TOKEN_HANDLER_MAP
from putput.types import TOKEN_PATTERNS_MAP

_GROUP_HANDLER = Callable[[str, Sequence[str]], str]
_BEFORE_JOINING_HOOK = Callable[[COMBO, Sequence[str], Sequence[GROUP]], Tuple[COMBO, Sequence[str], Sequence[GROUP]]]
_AFTER_JOINING_HOOK = Callable[[str, Sequence, Sequence], Tuple[str, Sequence, Sequence]]
_FINAL_HOOK = Callable[[str, Sequence, Sequence], Any]
_HOOK_ARGS = TypeVar('_HOOK_ARGS',
                     Tuple[COMBO, Sequence[str], Sequence[GROUP]],
                     Tuple[str, Sequence[str], Sequence[str]])
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
    # pylint: disable=too-few-public-methods
    def __init__(self,
                 *,
                 token_handler_map: Optional[TOKEN_HANDLER_MAP] = None,
                 group_handler_map: Optional[_GROUP_HANDLER_MAP] = None,
                 before_joining_hooks_map: Optional[_BEFORE_JOINING_HOOKS_MAP] = None,
                 after_joining_hooks_map: Optional[_AFTER_JOINING_HOOKS_MAP] = None,
                 preset: Optional[Union[str, Callable]] = None,
                 final_hook: Optional[_FINAL_HOOK] = None,
                 LOG_LEVEL: int = logging.WARNING
                 ) -> None:
        if preset and any((token_handler_map,
                           group_handler_map,
                           before_joining_hooks_map,
                           after_joining_hooks_map,
                           final_hook)):
            raise ValueError('If a preset is used, no other arguments may be specified.')
        self._logger = get_logger(__name__, LOG_LEVEL)
        if preset:
            if isinstance(preset, str):
                preset = get_preset(preset)
            presets = preset()
            self._token_handler_map, self._group_handler_map = presets[0], presets[1]
            self._before_joining_hooks_map, self._after_joining_hooks_map = presets[2], presets[3]
            self._final_hook = presets[4]
        else:
            self._token_handler_map = token_handler_map
            self._group_handler_map = group_handler_map
            self._before_joining_hooks_map = before_joining_hooks_map
            self._after_joining_hooks_map = after_joining_hooks_map
            self._final_hook = final_hook

    def flow(self,
             pattern_def_path: Path,
             *,
             dynamic_token_patterns_map: Optional[TOKEN_PATTERNS_MAP] = None,
             combo_options_map: Optional[_COMBO_OPTIONS_MAP] = None,
             disable_progress_bar: bool = False
             ) -> Iterable:
        # pylint: disable=too-many-locals
        ilen, exp_gen = expand(pattern_def_path, dynamic_token_patterns_map=dynamic_token_patterns_map)
        with tqdm(exp_gen, total=ilen, disable=disable_progress_bar, leave=False, miniters=1) as expansion_tqdm:
            for utterance_combo, tokens, groups in expansion_tqdm:
                desc = '{}'.format(', '.join(tokens))
                expansion_tqdm.set_description(textwrap.shorten(desc, width=30))
                self._logger.info(desc)
                group_names = tuple([group[0] for group in groups])
                if self._before_joining_hooks_map:
                    utterance_combo, tokens, groups = self._execute_joining_hooks(tokens,
                                                                                  group_names,
                                                                                  (utterance_combo, tokens, groups),
                                                                                  'EXPANSION')

                combo_options = self._get_combo_options(tokens, combo_options_map) if combo_options_map else None

                sample_size, combo_gen = combine(utterance_combo,
                                                 tokens,
                                                 token_handler_map=self._token_handler_map,
                                                 combo_options=combo_options)
                with tqdm(combo_gen, desc='COMBINING', total=sample_size,
                          disable=disable_progress_bar, leave=False, miniters=1) as combo_tqdm:
                    for utterance, handled_tokens in combo_tqdm:
                        handled_groups = _compute_handled_groups(groups, handled_tokens,
                                                                 group_handler_map=self._group_handler_map)
                        if self._after_joining_hooks_map:
                            utterance, handled_tokens, handled_groups = self._execute_joining_hooks(tokens,
                                                                                                    group_names,
                                                                                                    (utterance,
                                                                                                     handled_tokens,
                                                                                                     handled_groups),
                                                                                                    'COMBINATION')
                        if self._final_hook:
                            yield self._final_hook(utterance, handled_tokens, handled_groups)
                        else:
                            yield utterance, handled_tokens, handled_groups

    @staticmethod
    def _get_combo_options(tokens: Sequence[str], combo_options_map: _COMBO_OPTIONS_MAP) -> Optional[ComboOptions]:
        options_map = {} # type: Dict[Union[str, Tuple[str, ...]], ComboOptions]
        options_map.update(combo_options_map)
        key = tuple(tokens)
        return options_map.get(key) or options_map.get('DEFAULT')

    @no_type_check
    def _execute_joining_hooks(self,
                               tokens: Sequence[str],
                               group_names: Sequence[str],
                               args: _HOOK_ARGS,
                               stage: str
                               ) -> _HOOK_ARGS:
        hooks_map = self._before_joining_hooks_map if stage == 'EXPANSION' else self._after_joining_hooks_map
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
