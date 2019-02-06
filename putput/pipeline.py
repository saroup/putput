from pathlib import Path
from typing import Dict # pylint: disable=unused-import
from typing import Iterable
from typing import Mapping
from typing import Optional
from typing import Tuple
from typing import TypeVar
from typing import Union
from typing import cast
from typing import no_type_check

from putput.generator import generate_utterance_combinations_and_tokens
from putput.generator import generate_utterances_and_handled_tokens
from putput.joiner import CombinationOptions
from putput.types import AFTER_FLOW_HOOK_ARGS
from putput.types import AFTER_FLOW_HOOKS
from putput.types import BEFORE_FLOW_HOOK_ARGS
from putput.types import BEFORE_FLOW_HOOKS
from putput.types import HANDLED_TOKENS
from putput.types import HASHABLE_TOKENS
from putput.types import TOKEN
from putput.types import TOKEN_HANDLER
from putput.types import TOKEN_PATTERNS
from putput.types import TOKENS
from putput.types import UTTERANCE

HOOK_ARGS = TypeVar('HOOK_ARGS', BEFORE_FLOW_HOOK_ARGS, AFTER_FLOW_HOOK_ARGS)

class Pipeline:
    def __init__(self) -> None:
        self._before_flow_hooks_map = {} # type: Dict[Union[TOKEN, HASHABLE_TOKENS], BEFORE_FLOW_HOOKS]
        self._after_flow_hooks_map = {} # type: Dict[Union[TOKEN, HASHABLE_TOKENS], AFTER_FLOW_HOOKS]

    def register_hooks(self,
                       hooks_map: Mapping[Union[TOKEN, HASHABLE_TOKENS], Union[BEFORE_FLOW_HOOKS, AFTER_FLOW_HOOKS]],
                       stage: str) -> None:
        if stage == 'BEFORE_FLOW':
            before_flow_hooks_map = cast(Mapping[Union[TOKEN, HASHABLE_TOKENS], BEFORE_FLOW_HOOKS], hooks_map)
            self._before_flow_hooks_map.update(before_flow_hooks_map)
        elif stage == 'AFTER_FLOW':
            after_flow_hooks_map = cast(Mapping[Union[TOKEN, HASHABLE_TOKENS], AFTER_FLOW_HOOKS], hooks_map)
            self._after_flow_hooks_map.update(after_flow_hooks_map)
        else:
            err_msg = '{} is invalid. Please choose "BEFORE_FLOW" or "AFTER_FLOW"'.format(stage)
            raise ValueError(err_msg)

    def flow(self,
             pattern_definition_path: Path,
             dynamic_token_patterns_map: Optional[Mapping[TOKEN, TOKEN_PATTERNS]] = None,
             token_handler_map: Optional[Mapping[TOKEN, TOKEN_HANDLER]] = None,
             combination_options_map: Optional[Mapping[Union[TOKEN, HASHABLE_TOKENS], CombinationOptions]] = None
             ) -> Iterable[Tuple[UTTERANCE, HANDLED_TOKENS]]:
        for utterance_combination, tokens in generate_utterance_combinations_and_tokens(pattern_definition_path,
                                                                                        dynamic_token_patterns_map):
            if self._before_flow_hooks_map:
                utterance_combination, tokens = self._execute_flow_hooks(tokens,
                                                                         (utterance_combination, tokens),
                                                                         'BEFORE_FLOW')

            combination_options = None
            if combination_options_map:
                combination_options = self._get_combination_options(tokens, combination_options_map)

            for utterance, handled_tokens in generate_utterances_and_handled_tokens(utterance_combination,
                                                                                    tokens,
                                                                                    token_handler_map,
                                                                                    combination_options):
                if self._after_flow_hooks_map:
                    utterance, handled_tokens = self._execute_flow_hooks(tokens,
                                                                         (utterance, handled_tokens),
                                                                         'AFTER_FLOW')
                yield utterance, handled_tokens

    @staticmethod
    def _get_combination_options(tokens: TOKENS,
                                 combination_options_map: Mapping[Union[TOKEN, HASHABLE_TOKENS], CombinationOptions]
                                 ) -> Optional[CombinationOptions]:
        options_map = {} # type: Dict[Union[TOKEN, HASHABLE_TOKENS], CombinationOptions]
        options_map.update(combination_options_map)
        key = tuple(tokens)
        return options_map.get(key) or options_map.get('DEFAULT')

    @no_type_check
    def _execute_flow_hooks(self, tokens: TOKENS, args: HOOK_ARGS, stage: str) -> HOOK_ARGS:
        hooks_map = self._before_flow_hooks_map if stage == 'BEFORE_FLOW' else self._after_flow_hooks_map
        key = tuple(tokens) if tokens in hooks_map else 'DEFAULT'
        if key in hooks_map:
            for hook in hooks_map[key]:
                args = hook(*args)
        return args
