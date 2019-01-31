from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Tuple, Union # pylint: disable=unused-import

from putput.joiner import CombinationOptions
from putput.generator import generate_utterances_and_handled_tokens, process_pattern_definition


class Pipeline:
    def __init__(self) -> None:
        self._before_flow_hooks = {} # type: Dict[Union[str, Tuple[str, ...]], Tuple[Callable[[Tuple[Tuple[str, ...], ...], Tuple[str, ...]], Tuple[Tuple[Tuple[str, ...], ...], Tuple[str, ...]]], ...]]
        self._after_flow_hooks = {} # type: Dict[Union[str, Tuple[str, ...]], Tuple[Callable[[str, str], Tuple[str, str]], ...]]

    def register_hooks(self, tokens_to_hooks: Mapping[Union[str, Tuple[str, ...]], Tuple[Callable, ...]], stage: str) -> None:
        if stage == 'BEFORE_FLOW':
            self._before_flow_hooks.update(tokens_to_hooks)
        elif stage == 'AFTER_FLOW':
            self._after_flow_hooks.update(tokens_to_hooks)
        else:
            err_msg = '{} is invalid. Please choose "BEFORE_FLOW" or "AFTER_FLOW"'.format(stage)
            raise ValueError(err_msg)

    def flow(self,
             pattern_definition_path: Path,
             dynamic_token_to_token_patterns: Optional[Mapping[str, Tuple[Tuple[Tuple[str, ...], ...], ...]]] = None,
             token_to_token_handlers: Optional[Mapping[str, Callable[[str, str], str]]] = None,
             tokens_to_combination_options: Optional[Mapping[Union[str, Tuple[str, ...]], CombinationOptions]] = None
             ) -> Iterable[Tuple[str, str]]:
        for utterance_combination, tokens in process_pattern_definition(pattern_definition_path,
                                                                        dynamic_token_to_token_patterns):
            if self._before_flow_hooks:
                utterance_combination, tokens = self._execute_hooks(tokens,
                                                                    self._before_flow_hooks,
                                                                    (utterance_combination, tokens))

            if tokens_to_combination_options:
                combination_options = self._get_combination_options(tokens, tokens_to_combination_options)
            else:
                combination_options = None

            for utterance, handled_tokens in generate_utterances_and_handled_tokens(utterance_combination,
                                                                                    tokens,
                                                                                    token_to_token_handlers,
                                                                                    combination_options):
                if self._after_flow_hooks:
                    utterance, handled_tokens = self._execute_hooks(tokens,
                                                                    self._after_flow_hooks,
                                                                    (utterance, handled_tokens))
                yield utterance, handled_tokens

    @staticmethod
    def _get_combination_options(tokens: Tuple[str, ...],
                                 tokens_to_combination_options: Mapping[Union[str, Tuple[str, ...]], CombinationOptions]
                                 ) -> Optional[CombinationOptions]:
        return tokens_to_combination_options.get(tokens) or tokens_to_combination_options.get('DEFAULT')

    @staticmethod
    def _execute_hooks(tokens: Tuple[str, ...],
                       tokens_to_hooks: Mapping[Union[str, Tuple[str, ...]], Tuple[Callable, ...]],
                       args: Tuple[Any, ...]) -> Tuple[Any, ...]:
        if tokens in tokens_to_hooks:
            key = tokens # type: Union[str, Tuple[str, ...]]
        else:
            key = 'DEFAULT'
        if key in tokens_to_hooks:
            for hook in tokens_to_hooks[key]:
                args = hook(*args)
        return args
