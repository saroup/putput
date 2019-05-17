import random
import unittest
from typing import Iterable
from typing import List
from typing import Optional
from typing import Sequence

from putput.joiner import ComboOptions
from putput.joiner import join_combo


class TestJoiner(unittest.TestCase):
    def setUp(self):
        random.seed(0)

    def _test_join_combo(self,
                         pattern: Sequence[Sequence],
                         expected_output: Iterable[Sequence],
                         *,
                         all_options: Optional[List[ComboOptions]] = None
                         ) -> None:
        expected_output = tuple(expected_output)
        if not all_options:
            all_options = [ComboOptions(max_sample_size=len(expected_output),
                                        with_replacement=False),
                           ComboOptions(max_sample_size=len(expected_output),
                                        with_replacement=True)]
        for combo_options in all_options:
            actual_output = list(join_combo(pattern, combo_options=combo_options))
            if combo_options.with_replacement:
                self.assertEqual(len(actual_output), combo_options.max_sample_size)
            else:
                self.assertEqual(len(actual_output), len(set(actual_output)))
                self.assertEqual(len(actual_output), min(len(expected_output), combo_options.max_sample_size))
            for actual in actual_output:
                self.assertIn(actual, expected_output)

    def test_join_same_shape_lists(self) -> None:
        pattern = (('she', 'he'), ('wants', 'needs'))
        expected_output = (('she', 'needs'), ('he', 'wants'), ('she', 'wants'), ('he', 'needs'))
        self._test_join_combo(pattern, expected_output)

    def test_first_list_shorter_than_second_list(self) -> None:
        pattern = (('he',), ('wants', 'needs'))
        expected_output = (('he', 'wants'), ('he', 'needs'))
        self._test_join_combo(pattern, expected_output)

    def test_first_list_longer_than_second_list(self) -> None:
        pattern = (('he', 'she'), ('wants',))
        expected_output = (('he', 'wants'), ('she', 'wants'))
        self._test_join_combo(pattern, expected_output)

    def test_one_list(self) -> None:
        pattern = (('he wants', 'she needs'),)
        expected_output = (('he wants',), ('she needs',))
        self._test_join_combo(pattern, expected_output)

    def test_one_list_one_item(self) -> None:
        pattern = (('he wants',),)
        expected_output = (('he wants',),)
        self._test_join_combo(pattern, expected_output)

    def test_multiple_lists_same_size(self) -> None:
        pattern = (('he', 'she'), ('would', 'will'), ('want', 'need'))
        expected_output = (('he', 'would', 'want'), ('he', 'would', 'need'),
                           ('he', 'will', 'want'), ('he', 'will', 'need'),
                           ('she', 'would', 'want'), ('she', 'would', 'need'),
                           ('she', 'will', 'want'), ('she', 'will', 'need'))
        self._test_join_combo(pattern, expected_output)

    def test_multiple_lists_first_list_shorter(self) -> None:
        pattern = (('he',), ('would', 'will'), ('want', 'need'))
        expected_output = (('he', 'would', 'want'), ('he', 'would', 'need'),
                           ('he', 'will', 'want'), ('he', 'will', 'need'))
        self._test_join_combo(pattern, expected_output)

    def test_multiple_lists_middle_list_shorter(self) -> None:
        pattern = (('he', 'she'), ('will',), ('want', 'need'))
        expected_output = (('he', 'will', 'want'), ('he', 'will', 'need'),
                           ('she', 'will', 'want'), ('she', 'will', 'need'))
        self._test_join_combo(pattern, expected_output)

    def test_multiple_lists_last_list_shorter(self) -> None:
        pattern = (('he', 'she'), ('would', 'will'), ('want',))
        expected_output = (('he', 'would', 'want'), ('he', 'will', 'want'),
                           ('she', 'would', 'want'), ('she', 'will', 'want'))
        self._test_join_combo(pattern, expected_output)

    def test_multiple_lists_all_different_size(self) -> None:
        pattern = (('he',), ('would', 'will'), ('want', 'have', 'order'))
        expected_output = (('he', 'would', 'want'), ('he', 'would', 'have'),
                           ('he', 'would', 'order'), ('he', 'will', 'want'),
                           ('he', 'will', 'have'), ('he', 'will', 'order'))
        self._test_join_combo(pattern, expected_output)

    def test_zero_dimension(self) -> None:
        with self.assertRaises(ValueError):
            pattern = (tuple(), ('would', 'will'), ('want', 'have', 'order')) # type: Sequence[Sequence]
            expected_output = (('would', 'want'), ('would', 'have'),
                               ('would', 'order'), ('will', 'want'),
                               ('will', 'have'), ('will', 'order'))
            self._test_join_combo(pattern, expected_output)

    def test_num_unique_combinations_greater_than_max_size(self) -> None:
        pattern = tuple([tuple(range(50))] * 50)
        max_sample_size = 2
        all_options = [ComboOptions(max_sample_size=max_sample_size, with_replacement=True),
                       ComboOptions(max_sample_size=max_sample_size, with_replacement=False)]
        for combo_options in all_options:
            actual_output = list(join_combo(pattern, combo_options=combo_options))
            self.assertEqual(len(actual_output), max_sample_size)

    def test_unique_one_d_to_mult_d(self) -> None:
        pattern = ((0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
                   (10, 11, 12, 13, 14, 15, 16, 17, 18, 19),
                   (20, 21, 22, 23, 24, 25, 26, 27, 28, 29))
        num_unique_combinations = 1000
        # Subtract 1 from num_unique_combinations because if max_sample_size == num_unique_combinations,
        # the sampling will fall back to joining without sampling. This leads to a 0.1% chance that
        # there is an error, given that num_unique_combinations is 1000.
        combo_options = ComboOptions(max_sample_size=num_unique_combinations - 1, with_replacement=False)
        actual_output = list(join_combo(pattern, combo_options=combo_options))
        self.assertEqual(len(set(actual_output)), len(actual_output))

    def test_invalid_combo_options(self) -> None:
        with self.assertRaises(ValueError):
            ComboOptions(max_sample_size=0, with_replacement=False)

    def test_max_sample_size_less_than_max_combo_options(self) -> None:
        pattern = (('he', 'she'), ('would', 'will'), ('want',))
        expected_output = (('he', 'would', 'want'), ('he', 'will', 'want'),
                           ('she', 'would', 'want'), ('she', 'will', 'want'))
        max_sample_size = 2
        all_options = [ComboOptions(max_sample_size=max_sample_size, with_replacement=False),
                       ComboOptions(max_sample_size=max_sample_size, with_replacement=True)]
        self._test_join_combo(pattern, expected_output, all_options=all_options)

    def test_max_sample_size_greater_than_max_unique_options(self) -> None:
        pattern = (('he', 'she'), ('would', 'will'), ('want',))
        expected_output = (('he', 'would', 'want'), ('he', 'will', 'want'),
                           ('she', 'would', 'want'), ('she', 'will', 'want'))
        max_sample_size = 10
        all_options = [ComboOptions(max_sample_size=max_sample_size, with_replacement=False),
                       ComboOptions(max_sample_size=max_sample_size, with_replacement=True)]
        self._test_join_combo(pattern, expected_output, all_options=all_options)

if __name__ == '__main__':
    unittest.main()
