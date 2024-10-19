import unittest
from unittest import TestCase

from ecocounterfetcher.commands import fetchdata


class FetchDataTest(TestCase):
    def test_two_same_length_arrays_with_matching_values_should_merge(self):
        data1 = [
            {"date": "2024-01-01 01:00:00", "comptage": 1},
            {"date": "2024-01-01 02:00:00", "comptage": 10},
            {"date": "2024-01-01 03:00:00", "comptage": 100},
            {"date": "2024-01-01 04:00:00", "comptage": 1000}
        ]
        data2 = [
            {"date": "2024-01-01 01:00:00", "comptage": 2},
            {"date": "2024-01-01 02:00:00", "comptage": 20},
            {"date": "2024-01-01 03:00:00", "comptage": 200},
            {"date": "2024-01-01 04:00:00", "comptage": 2000}
        ]
        merged = fetchdata._merge_timeseries(data1, data2)
        self.assertEqual(merged, [
            {"date": "2024-01-01 01:00:00", "comptage": 3},
            {"date": "2024-01-01 02:00:00", "comptage": 30},
            {"date": "2024-01-01 03:00:00", "comptage": 300},
            {"date": "2024-01-01 04:00:00", "comptage": 3000}
        ])

    def test_second_array_after_first(self):
        data1 = [
            {"date": "2024-01-01 01:00:00", "comptage": 1},
            {"date": "2024-01-01 02:00:00", "comptage": 10},
            {"date": "2024-01-01 03:00:00", "comptage": 100},
            {"date": "2024-01-01 04:00:00", "comptage": 1000}
        ]
        data2 = [
            {"date": "2024-01-01 08:00:00", "comptage": 2},
            {"date": "2024-01-01 09:00:00", "comptage": 20},
            {"date": "2024-01-01 10:00:00", "comptage": 200},
            {"date": "2024-01-01 11:00:00", "comptage": 2000}
        ]
        merged = fetchdata._merge_timeseries(data1, data2)
        self.assertEqual(merged, [
            {"date": "2024-01-01 01:00:00", "comptage": 1},
            {"date": "2024-01-01 02:00:00", "comptage": 10},
            {"date": "2024-01-01 03:00:00", "comptage": 100},
            {"date": "2024-01-01 04:00:00", "comptage": 1000},
            {"date": "2024-01-01 08:00:00", "comptage": 2},
            {"date": "2024-01-01 09:00:00", "comptage": 20},
            {"date": "2024-01-01 10:00:00", "comptage": 200},
            {"date": "2024-01-01 11:00:00", "comptage": 2000}])

    def test_second_array_before_first(self):
        data1 = [
            {"date": "2024-01-01 08:00:00", "comptage": 1},
            {"date": "2024-01-01 09:00:00", "comptage": 10},
            {"date": "2024-01-01 10:00:00", "comptage": 100},
            {"date": "2024-01-01 11:00:00", "comptage": 1000}
        ]
        data2 = [
            {"date": "2024-01-01 01:00:00", "comptage": 2},
            {"date": "2024-01-01 02:00:00", "comptage": 20},
            {"date": "2024-01-01 03:00:00", "comptage": 200},
            {"date": "2024-01-01 04:00:00", "comptage": 2000}
        ]
        merged = fetchdata._merge_timeseries(data1, data2)
        self.assertEqual(merged, [
            {"date": "2024-01-01 01:00:00", "comptage": 2},
            {"date": "2024-01-01 02:00:00", "comptage": 20},
            {"date": "2024-01-01 03:00:00", "comptage": 200},
            {"date": "2024-01-01 04:00:00", "comptage": 2000},
            {"date": "2024-01-01 08:00:00", "comptage": 1},
            {"date": "2024-01-01 09:00:00", "comptage": 10},
            {"date": "2024-01-01 10:00:00", "comptage": 100},
            {"date": "2024-01-01 11:00:00", "comptage": 1000}])

    def test_arrays_are_interleaved(self):
        data1 = [
            {"date": "2024-01-01 01:00:00", "comptage": 1},
            {"date": "2024-01-01 03:00:00", "comptage": 10},
            {"date": "2024-01-01 05:00:00", "comptage": 100},
            {"date": "2024-01-01 07:00:00", "comptage": 1000}
        ]
        data2 = [
            {"date": "2024-01-01 02:00:00", "comptage": 2},
            {"date": "2024-01-01 04:00:00", "comptage": 20},
            {"date": "2024-01-01 06:00:00", "comptage": 200},
            {"date": "2024-01-01 08:00:00", "comptage": 2000}
        ]
        merged = fetchdata._merge_timeseries(data1, data2)
        self.assertEqual(merged, [
            {"date": "2024-01-01 01:00:00", "comptage": 1},
            {"date": "2024-01-01 02:00:00", "comptage": 2},
            {"date": "2024-01-01 03:00:00", "comptage": 10},
            {"date": "2024-01-01 04:00:00", "comptage": 20},
            {"date": "2024-01-01 05:00:00", "comptage": 100},
            {"date": "2024-01-01 06:00:00", "comptage": 200},
            {"date": "2024-01-01 07:00:00", "comptage": 1000},
            {"date": "2024-01-01 08:00:00", "comptage": 2000}])

    def test_second_array_within_range_of_first(self):
        data1 = [
            {"date": "2024-01-01 01:00:00", "comptage": 1},
            {"date": "2024-01-01 02:00:00", "comptage": 10},
            {"date": "2024-01-01 03:00:00", "comptage": 100},
            {"date": "2024-01-01 04:00:00", "comptage": 1000}
        ]
        data2 = [
            {"date": "2024-01-01 02:00:00", "comptage": 20},
            {"date": "2024-01-01 03:00:00", "comptage": 200}
        ]
        merged = fetchdata._merge_timeseries(data1, data2)
        self.assertEqual(merged, [
            {"date": "2024-01-01 01:00:00", "comptage": 1},
            {"date": "2024-01-01 02:00:00", "comptage": 30},
            {"date": "2024-01-01 03:00:00", "comptage": 300},
            {"date": "2024-01-01 04:00:00", "comptage": 1000}
        ])

    def test_first_array_within_range_of_second(self):
        data1 = [
            {"date": "2024-01-01 02:00:00", "comptage": 20},
            {"date": "2024-01-01 03:00:00", "comptage": 200}
        ]
        data2 = [{"date": "2024-01-01 01:00:00", "comptage": 1},
            {"date": "2024-01-01 02:00:00", "comptage": 10},
            {"date": "2024-01-01 03:00:00", "comptage": 100},
            {"date": "2024-01-01 04:00:00", "comptage": 1000}
        ]
        merged = fetchdata._merge_timeseries(data1, data2)
        self.assertEqual(merged, [
            {"date": "2024-01-01 01:00:00", "comptage": 1},
            {"date": "2024-01-01 02:00:00", "comptage": 30},
            {"date": "2024-01-01 03:00:00", "comptage": 300},
            {"date": "2024-01-01 04:00:00", "comptage": 1000}
        ])

    def test_first_array_partly_overlap_with_second(self):
        data1 = [
            {"date": "2024-01-01 01:00:00", "comptage": 1},
            {"date": "2024-01-01 02:00:00", "comptage": 10},
            {"date": "2024-01-01 03:00:00", "comptage": 100},
            {"date": "2024-01-01 04:00:00", "comptage": 1000}
        ]
        data2 = [
            {"date": "2024-01-01 03:00:00", "comptage": 2},
            {"date": "2024-01-01 04:00:00", "comptage": 20},
            {"date": "2024-01-01 05:00:00", "comptage": 200},
            {"date": "2024-01-01 06:00:00", "comptage": 2000}
        ]
        merged = fetchdata._merge_timeseries(data1, data2)
        self.assertEqual(merged, [
            {"date": "2024-01-01 01:00:00", "comptage": 1},
            {"date": "2024-01-01 02:00:00", "comptage": 10},
            {"date": "2024-01-01 03:00:00", "comptage": 102},
            {"date": "2024-01-01 04:00:00", "comptage": 1020},
            {"date": "2024-01-01 05:00:00", "comptage": 200},
            {"date": "2024-01-01 06:00:00", "comptage": 2000}])

    def test_return_first_array_if_second_is_empty(self):
        data1 = [
            {"date": "2024-01-01 01:00:00", "comptage": 1},
            {"date": "2024-01-01 02:00:00", "comptage": 10},
            {"date": "2024-01-01 03:00:00", "comptage": 100},
            {"date": "2024-01-01 04:00:00", "comptage": 1000}
        ]
        data2 = []
        merged = fetchdata._merge_timeseries(data1, data2)
        self.assertEqual(merged, [
            {"date": "2024-01-01 01:00:00", "comptage": 1},
            {"date": "2024-01-01 02:00:00", "comptage": 10},
            {"date": "2024-01-01 03:00:00", "comptage": 100},
            {"date": "2024-01-01 04:00:00", "comptage": 1000}
        ])

    def test_return_second_array_if_first_is_empty(self):
        data1 = []
        data2 = [
            {"date": "2024-01-01 01:00:00", "comptage": 1},
            {"date": "2024-01-01 02:00:00", "comptage": 10},
            {"date": "2024-01-01 03:00:00", "comptage": 100},
            {"date": "2024-01-01 04:00:00", "comptage": 1000}
        ]
        merged = fetchdata._merge_timeseries(data1, data2)
        self.assertEqual(merged, [
            {"date": "2024-01-01 01:00:00", "comptage": 1},
            {"date": "2024-01-01 02:00:00", "comptage": 10},
            {"date": "2024-01-01 03:00:00", "comptage": 100},
            {"date": "2024-01-01 04:00:00", "comptage": 1000}
        ])

    def test_return_empty_array_if_both_are_empty(self):
        data1 = []
        date2 = []
        merged = fetchdata._merge_timeseries(data1, date2)
        self.assertEqual(merged, [])


if __name__ == '__main__':
    unittest.main()