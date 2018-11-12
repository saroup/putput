from typing import Dict, List, Optional, Tuple

import yaml

from putput.input_validator import InputValidator
from putput.types import TokenPattern, UtterancePattern, UtterancePatternTokens


class InputProcessor:
    def __init__(self,
                 input_fname: str,
                 dynamic_token_patterns_dict: Optional[Dict[str, List[TokenPattern]]] = None) -> None:
        self._dynamic_token_patterns_dict = dynamic_token_patterns_dict or {}
        with open(input_fname, encoding='utf-8') as f:
            self._input_dict = yaml.load(f)
        input_validator = InputValidator(self._input_dict)
        input_validator.validate_yml()

    def _get_static_token_patterns_dict(self) -> dict:
        return {
            token: token_patterns
            for token_type_dict in self._input_dict['tokens'] for token_type in token_type_dict
            if token_type == 'static' for token_patterns_dict in token_type_dict['static']
            for token, token_patterns in token_patterns_dict.items()
        }

    def generate_utterance_pattern_and_tokens(self) -> List[Tuple[UtterancePattern, UtterancePatternTokens]]:
        static_token_patterns_dict = self._get_static_token_patterns_dict()
        token_patterns_dict = {**static_token_patterns_dict, **self._dynamic_token_patterns_dict}
        return [
            ([token_patterns_dict[token] for token in tokens], tokens)
            for tokens in self._input_dict['utterances']
        ]
