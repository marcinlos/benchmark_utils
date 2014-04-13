'''
Created on Mar 31, 2014

@author: los
'''
from benchmark.util import is_iterable, hasattrs, equal_attrs
from collections import defaultdict


def mapRecord(d, funs):
    return dict((k, funs[k](v)) for k, v in d.items() if k in funs)


class Record(object):

    def __init__(self, names, *args):
        self.__check_args(names, args)
        self.__data = dict(zip(names, args))

    @property
    def data(self):
        return self.__data

    @property
    def keys(self):
        return set(self.data.keys())

    @property
    def items(self):
        return set(self.data.items())

    def select(self, *cols):
        vals = self.values(*cols)
        return Record(cols, *vals)

    def values(self, *cols):
        return tuple(self[col] for col in cols)

    def __getitem__(self, key):
        return self.data[key]

    def __iter__(self):
        return iter(self.items)

    def __eq__(self, other):
        return hasattr(other, 'data') and self.data == other.data

    def __str__(self):
        pairs = self.data.items()
        fields = ', '.join(name + '=' + str(val) for name, val in pairs)
        return 'Record[{0}]'.format(fields)

    def __repr__(self):
        return str(self)

    def __check_args(self, names, args):
        if len(names) != len(args):
            msg = 'Invalid number of arguments ({0} expected, got {1})'
            raise LookupError(msg.format(len(names), len(args)))


def extractor(*cols):
    return lambda record: record.values(*cols)


def equal(**kwargs):
    def checker(record):
        return all(record[k] == v for k, v in kwargs.items())
    return checker


class DataFormat(object):

    __slots__ = ('__args', '__results', '__fields')

    def __init__(self, args, results):
        self.__args = tuple(args)
        self.__results = tuple(results)
        self.__fields = tuple(args + results)

    @property
    def args(self):
        return self.__args

    @property
    def results(self):
        return self.__results

    @property
    def fields(self):
        return self.__fields

    def __iter__(self):
        return iter(self.fields)

    def __len__(self):
        return len(self.fields)

    def __eq__(self, other):
        return equal_attrs(self, other, *DataFormat.__slots__)

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
            row += list(val)
        elif len(self.fmt.results) == 1:
            row += [val]
        else:
            raise ValueError('Collection required as value, given ' + str(val))
        return Record(self.fmt.fields, *row)


class Results(object):

    def __init__(self, names, rows=None):
        self.rows = rows if rows else []
        self.names = frozenset(names)

    def add(self, record):
        if record.keys != self.names:
            raise ValueError('Cannot insert incompatible record')
        self.rows.append(record)

    def gatherBy(self, *cols):
        bag = defaultdict(lambda: defaultdict(list))
        rest = set(self.names) - set(cols)

        for row in self.rows:
            t = row.values(*cols)
            data = bag[t]
            for key, val in row.select(*rest):
                data[key].append(val)
        return bag

    def select(self, *cols, **derived):
        groups = self.gatherBy(*cols)
        new_cols = [col for col in derived if col not in self.names]
        all_cols = cols + tuple(derived)

        results = []
        for key, vals in groups.items():
            aggregated = mapRecord(vals, derived)
            row = dict(zip(cols, key), **vals)
            computed = dict((col, derived[col](row)) for col in new_cols)
            aggregated.update(computed)

            all_vals = key + tuple(aggregated.values())
            r = Record(all_cols, *all_vals)
            results.append(r)

        return Results(all_cols, results)

    def col(self, name):
        return [row[name] for row in self]

    def groupBy(self, *cols):
        groups = defaultdict(lambda: Results(self.names))
        for record in self.rows:
            key = record.values(*cols)
            groups[key].add(record)
        return groups

    def orderBy(self, *cols, **kwargs):
        rev = kwargs.get('desc', False)
        data = sorted(self.rows, key=extractor(*cols), reverse=rev)
        return Results(self.names, data)

    def filter(self, pred):
        return Results(self.names, filter(pred, self.rows))

    def where(self, **values):
        return self.filter(equal(**values))

    def single(self):
        if len(self) > 1:
            raise Exception('There are ' + len(self) + ' rows, not 1')
        else:
            return self[0]

    def __iter__(self):
        return iter(self.rows)

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, n):
        return self.rows[n]

    def __eq__(self, other):
        if hasattrs(other, 'names', 'rows'):
            return self.names == other.names and \
                self.rows == other.rows
        else:
            return False

    def __str__(self):
        head = 'Results({0}):\n   '.format(', '.join(self.names))
        return head + '\n   '.join(map(str, self.rows))

    def __repr__(self):
        return str(self)
