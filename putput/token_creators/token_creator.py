from abc import ABC, abstractmethod
from typing import Optional


class TokenCreator(ABC):
    @abstractmethod
    def __call__(self, token_val: Optional[str] = None) -> str:
        raise NotImplementedError()
