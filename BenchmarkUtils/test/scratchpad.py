'''
Created on Mar 31, 2014

@author: los
'''
from random import random
from benchmark.util import *
from benchmark.run import *
from benchmark.data import saveResults, FileSink, DataFormat
from benchmark.aggr import avg, Dev

s = 0.2


def f(n, p):
    x = 1 + 0.3 * (random() - 0.5)
    return {'dupa': x * n * (s + (1 - s) / p), 'fak': random()}

fmt = DataFormat(['n', 'p'], ['dupa', 'fak'])
# r = Runner(f, fmt, sink=FileSink.make('dupa'))


r = Runner(f, fmt)
args = [seq(10, 100, 1000), seq(xrange(1, 9))]
r.repeat(100, args)


res = r.sink
print res.select('n', 'p', dupa=avg, fak=avg, dev=Dev('dupa'))
 
pat = 'data_{n}'
cols = [('dupa', avg), ('fak', avg), ('dev', Dev('dupa'))]
saveResults(res, pat, ['n'], 'p', *cols)
