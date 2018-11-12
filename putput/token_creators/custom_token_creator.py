from typing import Callable, Optional

from putput.token_creators.token_creator import TokenCreator


class CustomTokenCreator(TokenCreator):
    def __init__(self, token_handler: Callable[..., str]) -> None:
        self._token_handler = token_handler

    def __call__(self, token_val: Optional[str] = None) -> str:
        return self._token_handler(token_val)
