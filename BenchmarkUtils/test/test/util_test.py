'''
Created on Mar 31, 2014

@author: los
'''
import unittest
from benchmark.util import is_iterable


class Test(unittest.TestCase):

    def test_tuple_is_iterable(self):
        self.assertTrue(is_iterable((1, 2, 3)))

    def test_list_is_iterable(self):
        self.assertTrue(is_iterable([1, 2, 3]))

    def test_string_is_not_iterable(self):
        self.assertFalse(is_iterable('dupa'))


if __name__ == "__main__":
    unittest.main()
