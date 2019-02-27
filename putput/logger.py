import logging
from sys import stdout


def get_logger(module_name: str, level: int = logging.INFO) -> logging.Logger:
    """Returns a configured logger for the module.

    Args:
        module_name: __name__ for the calling module.
        level: Minimum logging level. Messages with this level or
            higher will be shown.
    """
    logger = logging.getLogger(module_name)
    if not logger.handlers:
        logger.propagate = False
        logger.setLevel(level)

        # TODO: make this standard error? Allow user to specify?
        stream_handler = logging.StreamHandler(stdout)
        stream_handler.setLevel(level)

        handler_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(handler_format)
        stream_handler.setFormatter(formatter)

        logger.addHandler(stream_handler)
    return logger
