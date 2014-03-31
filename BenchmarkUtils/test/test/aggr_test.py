'''
Created on Mar 31, 2014

@author: los
'''
import unittest
import benchmark.aggr as aggr


class Test(unittest.TestCase):

    def test_count_empty_zero(self):
        self.assertEquals(aggr.count([]), 0, 'Empty list has size > 0')

    def test_nonempty_list_nonzero(self):
        self.assertEquals(aggr.count([1, 2]), 2)

    def test_nonempty_generator_nonzero(self):
        n = aggr.count(x ** 2 for x in [2, 3, 4, 5])
        self.assertEquals(n, 4)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testCount_empty_zero']
    unittest.main()
