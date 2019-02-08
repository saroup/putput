from typing import Callable
from typing import Mapping
from typing import Sequence
from typing import Tuple

COMBO = Sequence[Sequence[str]]
GROUP = Tuple[str, int]
TOKEN_PATTERN = Sequence[Sequence[str]]
TOKEN_HANDLER = Callable[[str, str], str]
TOKEN_PATTERNS_MAP = Mapping[str, Sequence[TOKEN_PATTERN]]
TOKEN_HANDLER_MAP = Mapping[str, TOKEN_HANDLER]
