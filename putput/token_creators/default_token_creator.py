from typing import Optional

from putput.token_creators.token_creator import TokenCreator


class DefaultTokenCreator(TokenCreator):
    def __init__(self, token: str) -> None:
        self._token = token

    def __call__(self, token_val: Optional[str] = None) -> str:
        return f"[{self._token}]"
