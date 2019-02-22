import logging
from functools import reduce
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

from putput.combiner import combine
from putput.expander import expand
from putput.joiner import ComboOptions
from putput.logger import get_logger
from putput.presets.factory import get_preset

try:
    get_ipython() # type: ignore
    from tqdm import tqdm_notebook as tqdm # pragma: no cover
except NameError:
    from tqdm import tqdm


_HOOK_ARGS = TypeVar('_HOOK_ARGS',
                     Tuple[Sequence[Sequence[str]], Sequence[str], Sequence[Tuple[str, int]]],
                     Tuple[str, Sequence[str], Sequence[str]])

_E_H_MAP = Mapping[Any, Sequence[Callable[[Sequence[Sequence[str]], Sequence[str], Sequence[Tuple[str, int]]],
                                          Tuple[Sequence[Sequence[str]], Sequence[str], Sequence[Tuple[str, int]]]]]]
_C_H_MAP = Mapping[Any, Sequence[Callable[[str, Sequence, Sequence], Tuple[str, Sequence, Sequence]]]]

class Pipeline:
    # pylint: disable=too-many-instance-attributes
    def __init__(self,
                 *,
                 dynamic_token_patterns_map: Optional[Mapping[str, Sequence[Sequence[Sequence[str]]]]] = None,
                 token_handler_map: Optional[Mapping[str, Callable[[str, str], str]]] = None,
                 group_handler_map: Optional[Mapping[str, Callable[[str, Sequence[str]], str]]] = None,
                 expansion_hooks_map: Optional[_E_H_MAP] = None,
                 combo_hooks_map: Optional[_C_H_MAP] = None,
                 combo_options_map: Optional[Mapping[Any, ComboOptions]] = None,
                 final_hook: Optional[Callable[[str, Sequence, Sequence], Any]] = None,
                 LOG_LEVEL: int = logging.WARNING
                 ) -> None:
        self.dynamic_token_patterns_map = dynamic_token_patterns_map
        self.token_handler_map = token_handler_map
        self.group_handler_map = group_handler_map
        self.expansion_hooks_map = expansion_hooks_map
        self.combo_hooks_map = combo_hooks_map
        self.combo_options_map = combo_options_map
        self.final_hook = final_hook
        self._logger = get_logger(__name__, LOG_LEVEL)

    @classmethod
    def from_preset(cls, preset: Union[str, Callable], **kwargs: Any) -> 'Pipeline':
        if isinstance(preset, str):
            preset = get_preset(preset)
        init_kwargs = preset()
        init_kwargs.update(kwargs)
        return cls(**init_kwargs)

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    def flow(self,
             pattern_def_path: Path,
             *,
             disable_progress_bar: bool = False
             ) -> Iterable:
        for utterance_combo, tokens, groups in self._expand(pattern_def_path,
                                                            disable_progress_bar=disable_progress_bar):
            for utterance, handled_tokens, handled_groups in self._combine(utterance_combo,
                                                                           tokens,
                                                                           groups,
                                                                           disable_progress_bar=disable_progress_bar):
                if self.final_hook:
                    yield self.final_hook(utterance, handled_tokens, handled_groups)
                else:
                    yield utterance, handled_tokens, handled_groups

    def _combine(self,
                 utterance_combo: Sequence[Sequence[str]],
                 tokens: Sequence[str],
                 groups: Sequence[Tuple[str, int]],
                 *,
                 disable_progress_bar: bool = False
                 ) -> Iterable[Tuple[str, Sequence[str], Sequence[str]]]:
        group_names = tuple([group[0] for group in groups])
        combo_options = self._get_combo_options(tokens, self.combo_options_map) if self.combo_options_map else None

        sample_size, combo_gen = combine(utterance_combo,
                                         tokens,
                                         token_handler_map=self.token_handler_map,
                                         combo_options=combo_options)
        with tqdm(combo_gen,
                  desc='Combination...',
                  total=sample_size,
                  disable=disable_progress_bar,
                  leave=False,
                  miniters=1) as combination_tqdm:
            for utterance, handled_tokens in combination_tqdm:
                handled_groups = self._compute_handled_groups(groups, handled_tokens)
                if self.combo_hooks_map:
                    utterance, handled_tokens, handled_groups = self._execute_joining_hooks(tokens,
                                                                                            group_names,
                                                                                            (utterance,
                                                                                             handled_tokens,
                                                                                             handled_groups),
                                                                                            self.combo_hooks_map)
                yield utterance, handled_tokens, handled_groups

    def _expand(self,
                pattern_def_path: Path,
                *,
                disable_progress_bar: bool = False
                ) -> Iterable[Tuple[Sequence[Sequence[str]], Sequence[str], Sequence[Tuple[str, int]]]]:
        ilen, exp_gen = expand(pattern_def_path, dynamic_token_patterns_map=self.dynamic_token_patterns_map)
        with tqdm(exp_gen, desc='Expansion...', total=ilen, disable=disable_progress_bar, miniters=1) as expansion_tqdm:
            for utterance_combo, tokens, groups in expansion_tqdm:
                log_msg = '{}'.format(', '.join(tokens))
                self._logger.info(log_msg)
                group_names = tuple([group[0] for group in groups])
                if self.expansion_hooks_map:
                    utterance_combo, tokens, groups = self._execute_joining_hooks(tokens,
                                                                                  group_names,
                                                                                  (utterance_combo, tokens, groups),
                                                                                  self.expansion_hooks_map)
                yield utterance_combo, tokens, groups

    @staticmethod
    def _get_combo_options(tokens: Sequence[str],
                           combo_options_map: Mapping[Any, ComboOptions]
                           ) -> Optional[ComboOptions]:
        options_map = {} # type: Dict[Union[str, Tuple[str, ...]], ComboOptions]
        options_map.update(combo_options_map)
        key = tuple(tokens)
        return options_map.get(key) or options_map.get('DEFAULT')

    @no_type_check
    @staticmethod
    def _execute_joining_hooks(tokens: Sequence[str],
                               group_names: Sequence[str],
                               args: _HOOK_ARGS,
                               hooks_map: Union[_C_H_MAP, _E_H_MAP]
                               ) -> _HOOK_ARGS:
        token_key = tuple(tokens) if tuple(tokens) in hooks_map else 'DEFAULT'
        group_key = tuple(group_names) if tuple(group_names) in hooks_map else 'GROUP_DEFAULT'
        for key in (token_key, group_key):
            if key in hooks_map:
                args = reduce(lambda args, hook: hook(*args), hooks_map[key], args)
        return args

    def _compute_handled_groups(self,
                                groups: Sequence[Tuple[str, int]],
                                handled_tokens: Sequence[str],
                                ) -> Sequence[str]:
        start_index = 0
        handled_groups = []
        for group in groups:
            group_name, end_index = group
            group_handler = self._get_group_handler(group_name)
            handled_group = group_handler(group_name, handled_tokens[start_index: start_index + end_index])
            handled_groups.append(handled_group)
            start_index += end_index
        return tuple(handled_groups)

    def _get_group_handler(self, group_name: str) -> Callable[[str, Sequence[str]], str]:
        default_group_handler = lambda group_name, handled_tokens: '{{{}({})}}'.format(group_name,
                                                                                       ' '.join(handled_tokens))
        if self.group_handler_map:
            return (self.group_handler_map.get(group_name) or
                    self.group_handler_map.get('DEFAULT') or
                    default_group_handler)
        return default_group_handler
