'''
Created on Mar 31, 2014

@author: los
'''


def is_iterable(a):
    return hasattr(a, '__iter__')


class seq(object):
    def __init__(self, *args):
        if args:
            if len(args) == 1 and is_iterable(args[0]):
                self.items = args[0]
            else:
                self.items = args
        else:
            self.items = []


def cartesianProduct(*args):
    if args:
        first, rest = args[0], args[1:]
        if isinstance(first, seq):
            items = first.items
        else:
            items = (first,)
        for val in items:
            for tail in cartesianProduct(*rest):
                yield (val,) + tail
    else:
        yield ()
