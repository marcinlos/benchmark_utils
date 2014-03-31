'''
Created on Mar 31, 2014

@author: los
'''
from subprocess import Popen, PIPE
from .data import Results
from .util import cartesianProduct


class Runner(object):
    def __init__(self, f, names, valname='val'):
        self.f = f
        self.names = names
        self.results = Results(tuple(names) + (valname,))
        self.valname = valname

    @staticmethod
    def argSets(args):
        return cartesianProduct(*args)

    def formatArgs(self, args):
        pairs = zip(self.names, map(str, args))
        return ', '.join(name + ' = ' + val for name, val in pairs)

    def printArgs(self, args):
        print self.formatArgs(args)

    def add(self, argset, val):
        self.results.add(*argset, **{self.valname: val})

    def run(self, *args):
        if len(args) != len(self.names):
            raise TypeError('Wrong number of arguments')
        for argset in Runner.argSets(args):
            self.printArgs(argset)
            val = self.f(*argset)
            self.add(argset, val)
            print val
        return self.results

    def repeat(self, times, args):
        for i in xrange(times):
            print 'Iteration {0}:'.format(i)
            self.run(*args)
        return self.results


def runCmd(cmd, args, converter=lambda x: x):
    parts = [cmd] + args
    command = ' '.join(map(str, parts))
    p = Popen(command, shell=True, stdout=PIPE)
    output = p.stdout.read()
    return converter(output)


def retry(n=5):
    def decorator(func):
        def decorated(*args, **kwargs):
            for i in xrange(n):
                try:
                    return func(*args, **kwargs)
                except ValueError as e:
                    print('failed, retrying ({0})...'.format(i))
                    print e
            else:
                raise Exception('Too many failures')
        return decorated
    return decorator
