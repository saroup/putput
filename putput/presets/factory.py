from typing import Callable
from typing import Optional
from typing import Tuple

from putput.presets import iob

MYPY = False
if MYPY:
    from putput.pipeline import _GROUP_HANDLER_MAP # pylint: disable=unused-import
    from putput.pipeline import TOKEN_HANDLER_MAP # pylint: disable=unused-import

def get_init_preset(preset: str) -> Callable[[Optional['TOKEN_HANDLER_MAP'], Optional['_GROUP_HANDLER_MAP']],
                                             Tuple['TOKEN_HANDLER_MAP', '_GROUP_HANDLER_MAP']]:
    if preset == 'IOB':
        return iob.init_preset
    raise ValueError('{} is not a recognized preset.'.format(preset))
