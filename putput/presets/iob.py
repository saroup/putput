from typing import Optional
from typing import Sequence
from typing import Tuple


MYPY = False
if MYPY:
    from putput.pipeline import _GROUP_HANDLER_MAP # pylint: disable=unused-import
    from putput.pipeline import TOKEN_HANDLER_MAP # pylint: disable=unused-import

def _iob_token_handler(token: str, phrase: str) -> str:
    tokens = ['{}-{}'.format('B' if i == 0 else 'I', token)
              for i, _ in enumerate(phrase.replace(" '", "'").split())]
    return ' '.join(tokens)

def _iob_group_handler(group_name: str, handled_tokens: Sequence[str]) -> str:
    num_tokens = 0
    for tokenized_phrase in handled_tokens:
        num_tokens += len(tokenized_phrase.split())
    groups = ['{}-{}'.format('B' if i == 0 else 'I', group_name)
              for i in range(num_tokens)]
    return ' '.join(groups)

def init_preset(token_handler_map: Optional['TOKEN_HANDLER_MAP'] = None,
                group_handler_map: Optional['_GROUP_HANDLER_MAP'] = None
                ) -> Tuple['TOKEN_HANDLER_MAP', '_GROUP_HANDLER_MAP']:
    iob_token_handler_map = dict(token_handler_map) if token_handler_map else {}
    iob_group_handler_map = dict(group_handler_map) if group_handler_map else {}

    iob_token_handler_map.update({'DEFAULT': _iob_token_handler})
    iob_group_handler_map.update({'DEFAULT': _iob_group_handler})

    return iob_token_handler_map, iob_group_handler_map
