'''
Created on Apr 11, 2014

@author: los
'''
from .data import Results, Record
import csv


class FileSink(object):

    def __init__(self, path, fmt, **params):
        self.path = path
        self.names = fmt.fields
        self.truncateFile()

    def add(self, record):
        with open(self.path, 'a') as out:
            writeRecord(out, record, self.names, sep=';')

    @staticmethod
    def make(path, **params):
        return lambda fmt: FileSink(path, fmt, **params)

    def truncateFile(self):
        open(self.path, 'w').close()


def readRecords(path, *fields):
    names = [name for name, _ in fields]
    convs = [conv for _, conv in fields]
    with open(path, 'r') as source:
        reader = csv.reader(source, delimiter=';')
        for row in reader:
            vals = [conv(text) for conv, text in zip(convs, row)]
            yield Record(names, *vals)


def readResults(path, *fields):
    rows = list(readRecords(path, *fields))
    return Results([name for name, _ in fields], rows)


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
