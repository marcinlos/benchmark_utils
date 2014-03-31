'''
Created on Mar 31, 2014

@author: los
'''
from random import random
from benchmark.util import *
from benchmark.run import *
from benchmark.data import saveResults
from benchmark.aggr import avg, Dev


def dupa(a, b, c):
    return a + b * random() + c


r = Runner(dupa, ['a', 'b', 'z'], valname='value')
args = [seq(1, 2, 3), seq(10, 100, 1000), seq(4, 5)]
r.repeat(5, args)


res = r.results
print res.select('a', 'b', 'z', value=avg, dev=Dev('value'))

pat = 'data_a{a}_b{b}'
saveResults(res, pat, ['a', 'b'], main='z', value=avg)
