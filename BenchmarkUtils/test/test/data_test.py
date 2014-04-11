
import unittest
from benchmark.data import DataFormat, ResultConverter, Record, Results
from benchmark.util import equal_as_multisets
from benchmark.aggr import Min


class DataFormatTest(unittest.TestCase):

    def setUp(self):
        self.fmt = DataFormat(['arg1', 'arg2'], ['res1', 'res2'])

    def test_args_are_immutable(self):
        with self.assertRaises(AttributeError):
            self.fmt.args = ('bla', 'foo')

    def test_results_are_immutable(self):
        with self.assertRaises(AttributeError):
            self.fmt.results = ('bla', 'foo')

    def test_fields_are_immutable(self):
        with self.assertRaises(AttributeError):
            self.fmt.fields = ('bla', 'foo')

    def test_fields(self):
        fields = ['arg1', 'arg2', 'res1', 'res2']
        self.assertSequenceEqual(self.fmt.fields, fields)


class RecordTest(unittest.TestCase):

    def setUp(self):
        self.record = Record(['arg1', 'arg2'], 3, 'string')

    def test_creates_good_dictionary(self):
        vals = {'arg1': 3, 'arg2': 'string'}
        self.assertEqual(self.record.data, vals)

    def test_fails_if_not_enough_values(self):
        with self.assertRaises(LookupError):
            Record(['arg1', 'arg2'], 2)

    def test_fails_if_too_many_values(self):
        with self.assertRaises(LookupError):
            Record(['arg1', 'arg2'], 1, 'value', 3.432)

    def test_equal_records_are_equal(self):
        record2 = Record(['arg2', 'arg1'], 'string', 3)
        self.assertEqual(self.record, record2)

    def test_different_records_are_not_equal(self):
        record2 = Record(['arg1', 'arg2'], 666, 'string')
        self.assertNotEqual(self.record, record2)

    def test_record_is_not_equal_to_sth_else(self):
        self.assertNotEqual(self.record, 2343)

    def test_can_get_value_by_indexing(self):
        self.assertEqual(self.record['arg2'], 'string')

    def test_fails_indexing_with_wrong_key(self):
        with self.assertRaises(KeyError):
            self.record['foo']

    def test_keys(self):
        keys = set(['arg1', 'arg2'])
        self.assertSetEqual(self.record.keys, keys)

    def test_values_zero(self):
        self.assertEquals(self.record.values(), ())

    def test_values_one(self):
        self.assertEquals(self.record.values('arg1'), (3,))

    def test_values_two(self):
        vals = self.record.values('arg2', 'arg1')
        self.assertEqual(vals, ('string', 3))

    def test_select_zero(self):
        self.assertEqual(self.record.select(), Record([]))

    def test_select_one(self):
        result = self.record.select('arg2')
        self.assertEqual(result, Record(['arg2'], 'string'))

    def test_select_two(self):
        result = self.record.select('arg2', 'arg1')
        self.assertEqual(result, Record(['arg2', 'arg1'], 'string', 3))


class ConverterTest(unittest.TestCase):

    def setUp(self):
        self.fmt = DataFormat(['arg1', 'arg2'], ['res1', 'res2'])
        self.conv = ResultConverter(self.fmt)
        self.record = Record(['arg1', 'arg2', 'res1', 'res2'], 1, 2, 3, 4)

    def test_converts_dict(self):
        row = self.conv([1, 2], dict(res1=3, res2=4, other=33))
        self.assertEqual(row, self.record)

    def test_converts_seq(self):
        row = self.conv([1, 2], (3, 4))
        self.assertEqual(row, self.record)

    def test_fails_with_single_object(self):
        with self.assertRaises(ValueError):
            self.conv([1, 2], 666)

    def test_fails_with_missing_dict_item(self):
        with self.assertRaises(KeyError):
            self.conv([1, 2], dict(res1=3))

    def test_single_object(self):
        fmt = DataFormat(['arg1'], ['res1'])
        conv = ResultConverter(fmt)
        row = conv([1], 666)
        self.assertEqual(Record(fmt.fields, 1, 666), row)


class ResultsTest(unittest.TestCase):

    def setUp(self):
        self.fmt = DataFormat(['a', 'b'], ['t', 'value'])
        fields = self.fmt

        self.rows = [
            Record(fields, 1, 1, 5, 100),
            Record(fields, 1, 2, 7, 120),
            Record(fields, 1, 3, 2, 114),
            Record(fields, 2, 1, 3, 180),
            Record(fields, 2, 2, 6, 119),
            Record(fields, 2, 3, 8, 107),
            Record(fields, 3, 1, 4, 134),
            Record(fields, 3, 2, 2, 162),
            Record(fields, 3, 3, 5, 111),
            Record(fields, 4, 1, 3, 143),
            Record(fields, 4, 2, 6, 121),
            Record(fields, 4, 3, 7, 115),
        ]
        self.value_ordered = [
            Record(fields, 1, 1, 5, 100),
            Record(fields, 2, 3, 8, 107),
            Record(fields, 3, 3, 5, 111),
            Record(fields, 1, 3, 2, 114),
            Record(fields, 4, 3, 7, 115),
            Record(fields, 2, 2, 6, 119),
            Record(fields, 1, 2, 7, 120),
            Record(fields, 4, 2, 6, 121),
            Record(fields, 3, 1, 4, 134),
            Record(fields, 4, 1, 3, 143),
            Record(fields, 3, 2, 2, 162),
            Record(fields, 2, 1, 3, 180),
        ]
        self.res = Results(fields, self.rows)

    def test_equal_results_are_equal(self):
        other = Results(self.fmt.fields, self.rows)
        self.assertEqual(self.res, other)

    def test_column_order_does_not_matter(self):
        other = Results(reversed(self.fmt.fields), self.rows)
        self.assertEqual(self.res, other)

    def test_orderBy(self):
        ordered = self.res.orderBy('value')
        other = Results(self.fmt.fields, self.value_ordered)
        self.assertEqual(ordered, other)

    def test_orderByDesc(self):
        ordered = self.res.orderBy('value', desc=True)
        other = Results(self.fmt.fields, self.value_ordered[::-1])
        self.assertEqual(ordered, other)

    def test_gatherBy(self):
        byB = {
            (1,): {
                'a': [1, 2, 3, 4],
                't': [5, 3, 4, 3],
                'value': [100, 180, 134, 143]
            },
            (2,): {
                'a': [1, 2, 3, 4],
                't': [7, 6, 2, 6],
                'value': [120, 119, 162, 121]
            },
            (3,): {
                'a': [1, 2, 3, 4],
                't': [2, 8, 5, 7],
                'value': [114, 107, 111, 115]
            }
        }
        gathered = self.res.gatherBy('b')
        self.assertEqual(gathered, byB)

    def test_groupBy(self):
        byB = {
            (1,): Results(self.fmt, [
                Record(self.fmt, 1, 1, 5, 100),
                Record(self.fmt, 2, 1, 3, 180),
                Record(self.fmt, 3, 1, 4, 134),
                Record(self.fmt, 4, 1, 3, 143),
            ]),
            (2,): Results(self.fmt, [
                Record(self.fmt, 1, 2, 7, 120),
                Record(self.fmt, 2, 2, 6, 119),
                Record(self.fmt, 3, 2, 2, 162),
                Record(self.fmt, 4, 2, 6, 121),
            ]),
            (3,): Results(self.fmt, [
                Record(self.fmt, 1, 3, 2, 114),
                Record(self.fmt, 2, 3, 8, 107),
                Record(self.fmt, 3, 3, 5, 111),
                Record(self.fmt, 4, 3, 7, 115),
            ])
        }
        gathered = self.res.groupBy('b')
        self.assertEqual(gathered, byB)

    def assertEqualAsMultisets(self, first, second):
        if not equal_as_multisets(first, second):
            raise AssertionError('{0} and {1} not equal as multisets'
                .format(first, second))

    def test_simple_select(self):
        fields = ('a', 'value')
        selected = self.res.select(*fields)
        expected = Results(fields, [
            Record(fields, 1, 100),
            Record(fields, 1, 120),
            Record(fields, 1, 114),
            Record(fields, 2, 180),
            Record(fields, 2, 119),
            Record(fields, 2, 107),
            Record(fields, 3, 134),
            Record(fields, 3, 162),
            Record(fields, 3, 111),
            Record(fields, 4, 143),
            Record(fields, 4, 121),
            Record(fields, 4, 115),
        ])
        self.assertEqualAsMultisets(selected, expected)

    def test_select_sum(self):
        selected = self.res.select('a', value=sum)
        fields = ('a', 'value')
        expected = Results(fields, [
            Record(fields, 1, 100 + 120 + 114),
            Record(fields, 2, 180 + 119 + 107),
            Record(fields, 3, 134 + 162 + 111),
            Record(fields, 4, 143 + 121 + 115),
        ])
        self.assertEqualAsMultisets(selected, expected)

    def test_select_complex(self):
        selected = self.res.select('a', value=sum, t_min=Min('t'))
        fields = ('a', 'value', 't_min')
        expected = Results(fields, [
            Record(fields, 1, 100 + 120 + 114, 2),
            Record(fields, 2, 180 + 119 + 107, 3),
            Record(fields, 3, 134 + 162 + 111, 2),
            Record(fields, 4, 143 + 121 + 115, 3),
        ])
        self.assertEqualAsMultisets(selected, expected)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
