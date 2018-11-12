import unittest

from putput.token_creators.default_token_creator import DefaultTokenCreator


class TestDefaultTokenCreator(unittest.TestCase):
    def test_default_token_creator(self) -> None:
        token = 'SPEAKER'
        token_creator = DefaultTokenCreator(token)
        self.assertEqual(token_creator('Bose'), f"[{token}]")


if __name__ == '__main__':
    unittest.main()
