import unittest

from putput.token_creators.custom_token_creator import CustomTokenCreator


class TestCustomTokenCreator(unittest.TestCase):
    def test_custom_token_creator(self) -> None:
        token_creator = CustomTokenCreator(lambda token_val: f"{token_val}(id=1)")
        self.assertEqual(token_creator('Bose'), f"Bose(id=1)")


if __name__ == '__main__':
    unittest.main()
