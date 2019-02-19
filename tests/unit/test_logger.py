import logging
import unittest

from putput.logger import get_logger


class TestLogger(unittest.TestCase):

    def test_name(self) -> None:
        logger = get_logger(__name__)
        self.assertEqual(logger.name, 'tests.unit.test_logger')

    def test_default_level(self) -> None:
        logger = get_logger(__name__)
        self.assertEqual(logger.level, logging.INFO)

    def test_singleton(self) -> None:
        for _ in range(2):
            logger = get_logger(__name__)
            self.assertEqual(len(logger.handlers), 1)

    def test_formatter_uses_time(self) -> None:
        logger = get_logger(__name__)
        self.assertTrue(logger.handlers[0].formatter.usesTime()) # type: ignore
