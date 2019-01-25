import unittest
from typing import List, Optional

from putput.joiner import CombinationOptions, join_combination
from putput.pattern_definition_processor import TokenPattern


class TestJoiner(unittest.TestCase):
    def _test_join_combination(self,
                               pattern: TokenPattern,
                               expected_output: List[str],
                               all_options: Optional[List[CombinationOptions]] = None,
                               ) -> None:
        if not all_options:
            all_options = [CombinationOptions(max_sample_size=len(expected_output), with_replacement=False, seed=0),
                           CombinationOptions(max_sample_size=len(expected_output), with_replacement=True, seed=0)]
        for opts in all_options:
            actual_output = list(join_combination(pattern, opts))
            if opts.with_replacement:
                self.assertEqual(len(actual_output), opts.max_sample_size)
            else:
                self.assertEqual(len(actual_output), len(set(actual_output)))
                self.assertEqual(len(actual_output), min(len(expected_output), opts.max_sample_size))
            for actual in actual_output:
                self.assertIn(actual, expected_output)

    def test_join_same_shape_lists(self) -> None:
        pattern = (('she', 'he'), ('wants', 'needs'))
        expected_output = ['she needs', 'he wants', 'she wants', 'he needs']
        self._test_join_combination(pattern, expected_output)

    def test_first_list_shorter_than_second_list(self) -> None:
        pattern = (('he',), ('wants', 'needs'))
        expected_output = ['he wants', 'he needs']
        self._test_join_combination(pattern, expected_output)

    def test_first_list_longer_than_second_list(self) -> None:
        pattern = (('he', 'she'), ('wants',))
        expected_output = ['he wants', 'she wants']
        self._test_join_combination(pattern, expected_output)

    def test_one_list(self) -> None:
        pattern = (('he wants', 'she needs'),)
        expected_output = ['he wants', 'she needs']
        self._test_join_combination(pattern, expected_output)

    def test_one_list_one_item(self) -> None:
        pattern = (('he wants',),)
        expected_output = ['he wants']
        self._test_join_combination(pattern, expected_output)

    def test_multiple_lists_same_size(self) -> None:
        pattern = (('he', 'she'), ('would', 'will'), ('want', 'need'))
        expected_output = [
            'he would want', 'he would need', 'he will want', 'he will need', 'she would want', 'she would need',
            'she will want', 'she will need'
        ]
        self._test_join_combination(pattern, expected_output)

    def test_multiple_lists_first_list_shorter(self) -> None:
        pattern = (('he',), ('would', 'will'), ('want', 'need'))
        expected_output = ['he would want', 'he would need', 'he will want', 'he will need']
        self._test_join_combination(pattern, expected_output)

    def test_multiple_lists_middle_list_shorter(self) -> None:
        pattern = (('he', 'she'), ('will',), ('want', 'need'))
        expected_output = ['he will want', 'he will need', 'she will want', 'she will need']
        self._test_join_combination(pattern, expected_output)

    def test_multiple_lists_last_list_shorter(self) -> None:
        pattern = (('he', 'she'), ('would', 'will'), ('want',))
        expected_output = ['he would want', 'he will want', 'she would want', 'she will want']
        self._test_join_combination(pattern, expected_output)

    def test_multiple_lists_all_different_size(self) -> None:
        pattern = (('he',), ('would', 'will'), ('want', 'have', 'order'))
        expected_output = [
            'he would want', 'he would have', 'he would order', 'he will want', 'he will have', 'he will order'
        ]
        self._test_join_combination(pattern, expected_output)

    def test_invalid_combination_options(self) -> None:
        with self.assertRaises(ValueError):
            CombinationOptions(max_sample_size=0, with_replacement=False, seed=0)

    def test_max_sample_size_less_than_max_combination_options(self) -> None:
        pattern = (('he', 'she'), ('would', 'will'), ('want',))
        expected_output = ['he would want', 'he will want', 'she would want', 'she will want']
        max_sample_size = 2
        all_options = [CombinationOptions(max_sample_size=max_sample_size, with_replacement=False, seed=0),
                       CombinationOptions(max_sample_size=max_sample_size, with_replacement=True, seed=0)]
        self._test_join_combination(pattern, expected_output, all_options)

    def test_max_sample_size_greater_than_max_unique_options(self) -> None:
        pattern = (('he', 'she'), ('would', 'will'), ('want',))
        expected_output = ['he would want', 'he will want', 'she would want', 'she will want']
        max_sample_size = 10
        all_options = [CombinationOptions(max_sample_size=max_sample_size, with_replacement=False, seed=0),
                       CombinationOptions(max_sample_size=max_sample_size, with_replacement=True, seed=0)]
        self._test_join_combination(pattern, expected_output, all_options)

    def test_same_seed_same_result(self) -> None:
        pattern = (('1', '2', '3'), ('4',), ('5', '6', '7', '8', '9', '10'), ('11',), ('12',))
        all_options = [CombinationOptions(max_sample_size=3, with_replacement=False, seed=0),
                       CombinationOptions(max_sample_size=3, with_replacement=True, seed=0)]
        for opts in all_options:
            joined1 = list(join_combination(pattern, opts))
            joined2 = list(join_combination(pattern, opts))
            self.assertEqual(joined1, joined2)

    def test_different_seed_different_result(self) -> None:
        pattern = (('1', '2', '3'), ('4',), ('5', '6', '7', '8', '9', '10'), ('11',), ('12',))
        all_options = [
            (
                CombinationOptions(max_sample_size=3, with_replacement=False, seed=10),
                CombinationOptions(max_sample_size=3, with_replacement=False, seed=11)
            ), (
                CombinationOptions(max_sample_size=3, with_replacement=True, seed=10),
                CombinationOptions(max_sample_size=3, with_replacement=True, seed=11)
            )
        ]
        for opts in all_options:
            joined1 = list(join_combination(pattern, opts[0]))
            joined2 = list(join_combination(pattern, opts[1]))
            self.assertNotEqual(joined1, joined2)
