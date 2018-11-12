from typing import Callable, Dict, Optional, cast

from putput.token_creators.custom_token_creator import CustomTokenCreator
from putput.token_creators.default_token_creator import DefaultTokenCreator
from putput.token_creators.token_creator import TokenCreator


class TokenCreatorFactory:
    def __init__(self, token_handlers: Optional[Dict[str, Callable[..., str]]] = None) -> None:
        self._token_handlers = token_handlers

    def token_creator(self, token: str) -> TokenCreator:
        try:
            handlers = cast(Dict[str, Callable[..., str]], self._token_handlers)
            return CustomTokenCreator(handlers[token])
        except (KeyError, TypeError):
            return DefaultTokenCreator(token)
