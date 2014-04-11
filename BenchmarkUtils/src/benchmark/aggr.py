'''
Created on Mar 31, 2014

@author: los
'''
from math import sqrt
from __builtin__ import min


def count(data):
    return len(list(data))


def avg(data):
    vals = list(data)
    return sum(vals) / float(len(vals))


def var(data):
    a = avg(data)
    return avg((x - a) ** 2 for x in data)


def dev(data):
    return sqrt(var(data))


def median(data):
    s = sorted(data)
    n = len(s)
    if n % 2 == 1:
        return s[n / 2]
    else:
        return 0.5 * (s[n / 2 - 1] + s[n / 2])


def aggr(f, *args):
    def wrapper(row):
        vals = [row[arg] for arg in args]
        return f(*vals)
    return wrapper


def Count(col):
    return aggr(count, col)


def Avg(col):
    return aggr(avg, col)


def Var(col):
    return aggr(var, col)


def Dev(col):
    return aggr(dev, col)


def Median(col):
    return aggr(median, col)


def Min(col):
    return aggr(min, col)


def Max(col):
    return aggr(max, col)


def Sum(col):
    return aggr(sum, col)
