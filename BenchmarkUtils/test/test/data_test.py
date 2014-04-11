
import unittest
from benchmark.data import DataFormat, ResultConverter, Record


class DataFormatTest(unittest.TestCase):

    def test_all(self):
        fmt = DataFormat(['arg1', 'arg2'], ['res1', 'res2'])
        self.assertSequenceEqual(fmt.all, ['arg1', 'arg2', 'res1', 'res2'])


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

    @unittest.expectedFailure
    def test_fails_with_single_object(self):
        self.conv([1, 2], 666)

    @unittest.expectedFailure
    def test_fails_with_missing_dict_item(self):
        self.conv([1, 2], dict(res1=3))

    def test_single_object(self):
        fmt = DataFormat(['arg1'], ['res1'])
        conv = ResultConverter(fmt)
        row = conv([1], 666)
        self.assertEqual(Record(fmt.all, 1, 666), row)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
