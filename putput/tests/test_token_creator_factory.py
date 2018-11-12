import unittest

from putput.token_creators.custom_token_creator import CustomTokenCreator
from putput.token_creators.default_token_creator import DefaultTokenCreator
from putput.token_creators.token_creator_factory import TokenCreatorFactory


class TestTokenCreatorFactory(unittest.TestCase):
    def setUp(self) -> None:
        token_handlers = {'SPEAKER': lambda token_val: f"{token_val}(id=1)"}
        self._factory = TokenCreatorFactory(token_handlers)

    def test_static_created_when_no_handler_for_token(self) -> None:
        token_creator = self._factory.token_creator('PLAY')
        self.assertIsInstance(token_creator, DefaultTokenCreator)

    def test_dynamic_created_when_handler_for_token_exists(self) -> None:
        token_creator = self._factory.token_creator('SPEAKER')
        self.assertIsInstance(token_creator, CustomTokenCreator)


if __name__ == '__main__':
    unittest.main()
