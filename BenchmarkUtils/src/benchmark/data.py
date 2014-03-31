'''
Created on Mar 31, 2014

@author: los
'''


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
    def __init__(self, names=[], *args, **kwargs):
        pairs = zip(names, args)
        self.data = dict(pairs, **kwargs)

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

    def __str__(self):
        pairs = self.data.items()
        fields = ', '.join(name + '=' + str(val) for name, val in pairs)
        return 'Record[{0}]'.format(fields)

    def __repr__(self):
        return str(self)


class Results(object):

    def __init__(self, names, results=None):
        self.results = results if results else []
        self.names = tuple(names)

    def add(self, *args, **kwargs):
        row = Record(self.names, *args, **kwargs)
        self.results.append(row)

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

            r = Record(cols, *key, **aggregated)
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

    def __iter__(self):
        return iter(self.results)

    def __str__(self):
        head = 'Results({0}):\n   '.format(', '.join(self.names))
        return head + '\n   '.join(map(str, self.results))

    def __repr__(self):
        return str(self)


def formatRow(*args, **kwargs):
    if 'sep' in kwargs:
        sep = kwargs['sep']
    else:
        sep = '\t'
    return sep.join(map(str, args)) + '\n'


def writeRecord(out, record):
    out.write(formatRow(*record.flatten()))


def saveResults(results, pattern, filesBy, main, **kwargs):
    groups = results.groupBy(*filesBy)
    for key, res in groups.iteritems():
        params = dict(zip(filesBy, key))
        path = pattern.format(**params)
        with open(path, 'w') as out:
            for record in res.select(main, **kwargs):
                writeRecord(out, record)
