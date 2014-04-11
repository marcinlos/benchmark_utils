'''
Created on Mar 31, 2014

@author: los
'''
from benchmark.util import is_iterable


def mapRecord(d, funs):
    dd = {}
    for key, val in d.items():
        if key in funs:
            dd[key] = funs[key](val)
    return dd


def mapDict(d, f):
    dd = {}
    for key, val in d.iteritems():
        dd[key] = f(val)
    return dd


class Record(object):
    def __init__(self, names, *args):
        self.data = dict(zip(names, args))

    def select(self, *cols):
        vals = self.values(*cols)
        return Record(cols, *vals)

    def values(self, *cols):
        return tuple(self.data[col] for col in cols)

    def flatten(self):
        return self.values(*self.data.keys())

    def items(self):
        return self.data.items()

    def __getitem__(self, key):
        return self.data[key]

    def __eq__(self, other):
        return hasattr(other, 'data') and self.data == other.data

    def __str__(self):
        pairs = self.data.items()
        fields = ', '.join(name + '=' + str(val) for name, val in pairs)
        return 'Record[{0}]'.format(fields)

    def __repr__(self):
        return str(self)


class DataFormat(object):
    def __init__(self, args, results):
        self.args = tuple(args)
        self.results = tuple(results)
        self.all = tuple(args + results)

    def __iter__(self):
        return iter(self.all)

    def __str__(self):
        args = ', '.join(self.args)
        results = ', '.join(self.results)
        return 'DataFormat[args=({0}), results=({1})]'.format(args, results)


class ResultConverter(object):
    def __init__(self, fmt):
        self.fmt = fmt

    def __call__(self, args, val):
        row = list(args)
        if isinstance(val, dict):
            pairs = [val[k] for k in self.fmt.results]
            row += pairs
        elif is_iterable(val):
            row += val
        elif len(self.fmt.results) == 1:
            row += [val]
        else:
            raise Exception('Collection required as value, given ' + str(val))
        return Record(self.fmt.all, *row)


def recordMultiSort(records, *cols):
    return sorted(records, key=lambda a: a.values(*cols))


class Results(object):

    def __init__(self, names, results=None):
        self.results = results if results else []
        self.names = names

    def add(self, record):
        self.results.append(record)

    def gather(self, *cols):
        bag = {}
        rest = set(self.names) - set(cols)

        for row in self.results:
            t = row.values(*cols)
            data = bag.setdefault(t, {})
            for key, val in row.select(*rest).items():
                vals = data.setdefault(key, [])
                vals.append(val)
        return bag

    def select(self, *cols, **derived):
        grouped = self.gather(*cols)
        results = []
        for key, vals in grouped.items():
            aggregated = mapRecord(vals, derived)

            funs = [n for n in derived if n not in self.names]
            groupedRow = dict(zip(cols, key), **vals)
            computed = [(f, derived[f](groupedRow)) for f in funs]
            aggregated.update(dict(computed))

            colss = cols + tuple(aggregated.keys())
            valss = key + tuple(aggregated.values())
            r = Record(colss, *valss)
            results.append(r)

        names = cols + tuple(derived)
        return Results(names, results)

    def groupBy(self, *cols):
        groups = {}
        for record in self.results:
            key = record.values(*cols)
            vals = groups.setdefault(key, Results(self.names))
            vals.results.append(record)
        return groups

    def orderBy(self, *cols):
        data = sorted(self.results, key=lambda a: a.values(*cols))
        return Results(self.names, data)

    def __iter__(self):
        return iter(self.results)

    def __str__(self):
        head = 'Results({0}):\n   '.format(', '.join(self.names))
        return head + '\n   '.join(map(str, self.results))

    def __repr__(self):
        return str(self)


class FileSink(object):

    def __init__(self, path, fmt, **params):
        self.path = path
        self.names = fmt.all
        self.truncateFile()

    def add(self, record):
        with open(self.path, 'a') as out:
            writeRecord(out, record, self.names, sep=';')

    @staticmethod
    def make(path, **params):
        return lambda fmt: FileSink(path, fmt, **params)

    def truncateFile(self):
        open(self.path, 'w').close()


def formatRow(*args, **kwargs):
    if 'sep' in kwargs:
        sep = kwargs['sep']
    else:
        sep = '\t'
    return sep.join(map(str, args)) + '\n'


def writeRecord(out, record, cols, sep='\t'):
    vals = record.values(*cols)
    s = formatRow(*vals, sep=sep)
    out.write(s)


def saveResults(results, pattern, filesBy, main, *cols):
    groups = results.groupBy(*filesBy)
    for key, res in groups.iteritems():
        params = dict(zip(filesBy, key))
        path = pattern.format(**params)
        with open(path, 'w') as out:
            for record in res.select(main, **dict(cols)).orderBy(main):
                writeRecord(out, record, [main] + [c[0] for c in cols])
