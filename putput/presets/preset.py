from abc import ABC, abstractmethod
from typing import Tuple, Optional

MYPY = False
if MYPY:
    # pylint: disable=cyclic-import
    from putput.pipeline import _AFTER_JOINING_HOOKS_MAP # pylint: disable=unused-import
    from putput.pipeline import _BEFORE_JOINING_HOOKS_MAP # pylint: disable=unused-import
    from putput.pipeline import _GROUP_HANDLER_MAP # pylint: disable=unused-import
    from putput.types import TOKEN_HANDLER_MAP # pylint: disable=unused-import

class Preset(ABC):
    # pylint: disable=too-few-public-methods
    @abstractmethod
    def init_preset(self,
                    *,
                    token_handler_map: Optional['TOKEN_HANDLER_MAP'] = None,
                    group_handler_map: Optional['_GROUP_HANDLER_MAP'] = None,
                    before_joining_hooks_map: Optional['_BEFORE_JOINING_HOOKS_MAP'] = None,
                    after_joining_hooks_map: Optional['_AFTER_JOINING_HOOKS_MAP'] = None
                    ) -> Tuple[Optional['TOKEN_HANDLER_MAP'],
                               Optional['_GROUP_HANDLER_MAP'],
                               Optional['_BEFORE_JOINING_HOOKS_MAP'],
                               Optional['_AFTER_JOINING_HOOKS_MAP']]:
        raise NotImplementedError()
