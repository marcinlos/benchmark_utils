'''
Created on Mar 31, 2014

@author: los
'''
from subprocess import Popen, PIPE
from .data import Results, ResultConverter
from .util import cartesianProduct


class Runner(object):
    def __init__(self, f, data_format, conv=ResultConverter, sink=Results):
        self.f = f
        self.data_format = data_format
        self.conv = conv(data_format)
        self.sink = sink(data_format)

    def formatArgs(self, args):
        pairs = zip(self.data_format.args, map(str, args))
        return ', '.join(name + ' = ' + val for name, val in pairs)

    def printArgs(self, args):
        print self.formatArgs(args)

    def add(self, argset, val):
        record = self.conv(argset, val)
        self.sink.add(record)

    def run(self, *args):
        for argset in cartesianProduct(*args):
            self.printArgs(argset)
            val = self.f(*argset)
            self.add(argset, val)
            print val
        return self.sink

    def repeat(self, times, args):
        for i in xrange(times):
            print 'Iteration {0}:'.format(i)
            self.run(*args)
        return self.sink


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
                except Exception as e:
                    print('failed, retrying ({0})...'.format(i))
                    print e
            else:
                raise Exception('Too many failures')
        return decorated
    return decorator
