import logging
from sys import stderr
from sys import stdout
from typing import IO


def get_logger(module_name: str, *, level: int = logging.INFO, stream: str = 'stderr') -> logging.Logger:
    """Returns a configured logger for the module.

    Args:
        module_name: __name__ for the calling module.

        level: Minimum logging level. Messages with this level or
            higher will be shown.

        stream: Input to logging.StreamHandler, either 'stderr' or 'stdout'.

    Raises:
        ValueError: If stream is not 'stderr' or 'stdout'.
    """
    out_stream = _get_out_stream(stream)
    logger = logging.getLogger(module_name)
    if not logger.handlers:
        logger.propagate = False
        logger.setLevel(level)

        stream_handler = logging.StreamHandler(out_stream)
        stream_handler.setLevel(level)

        handler_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(handler_format)
        stream_handler.setFormatter(formatter)

        logger.addHandler(stream_handler)
    return logger

def _get_out_stream(stream: str) -> IO[str]:
    possible_streams = {'stderr', 'stdout'}
    if stream not in possible_streams:
        raise ValueError('Invalid value for stream. Valid values include: {}.'.format(possible_streams))
    if stream == 'stdout':
        return stdout
    return stderr
