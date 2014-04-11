'''
Created on Mar 31, 2014

@author: los
'''


def hasattrs(obj, *attrs):
    return all(hasattr(obj, attr) for attr in attrs)


def equal_attrs(a, b, *attrs):
    return hasattrs(a, *attrs) and hasattrs(b, *attrs) and \
        all(getattr(a, attr) == getattr(b, attr) for attr in attrs)


def fully_contains(a, b):
    bb = list(b)
    for item in a:
        if item in bb:
            bb.remove(item)
        else:
            return False
    return True


def equal_as_multisets(a, b):
    return fully_contains(a, b) and fully_contains(b, a)


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


def cartesian_product(*args):
    if args:
        first, rest = args[0], args[1:]
        if isinstance(first, seq):
            items = first.items
        else:
            items = (first,)
        for val in items:
            for tail in cartesian_product(*rest):
                yield (val,) + tail
    else:
        yield ()
