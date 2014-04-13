
from benchmark.io import readResults
from benchmark.aggr import avg, Avg, Min, Max
from benchmark.plot import Plot


fields = [
    ('ver', str), ('n', int), ('procs', int),
    ('total', float), ('bcast', float), ('scatter', float),
    ('work', float), ('gather', float)
]

res = readResults('data/data', *fields)

labels = ('# of processes', 'total time [ms]')

p = Plot(res, 'procs', 'img/times_{ver}_{n}.png')
p.params = ('ver', 'n')
p.title = 'Total running time\n({ver}, n={n})'
p.labels = labels
p.series('min', Min('total'), '--')
p.series('max', Max('total'), '--')
p.series('avg', Avg('total'), dev=True)
p.plot()

p = Plot(res, 'procs', 'img/summary_{ver}.png')
p.params = ['ver']
p.group_by = ['n']
p.title = 'Total running time\n({ver})'
p.labels = labels
p.series('avg', Avg('total'), '.-', label='n={n}')
p.plot()

p = Plot(res, 'procs', 'img/details_{ver}_{n}.png')
p.params = ('ver', 'n')
p.title = 'Times of specific operations\n({ver}, n={n})'
p.labels = labels
p.series('work', Avg('work'))
p.series('bcast', Avg('bcast'))
p.series('scatter', Avg('scatter'))
p.series('gather', Avg('gather'))
p.stacked()


base_times = res.where(procs=1).select('ver', 'n', total=avg)


def speedup(row):
    ver, n = row['ver'][0], row['n'][0]
    t = base_times.where(ver=ver, n=n).single()['total']
    return t / avg(row['total'])


def efficiency(row):
    return speedup(row) / row['procs']


def serial_fraction(row):
    p = row['procs']
    return (1.0 / speedup(row)) / (1 - 1.0 / p)


p = Plot(res, 'procs', 'img/speedup_{ver}.png')
p.params = ['ver']
p.group_by = ['n']
p.title = 'Speedup ({ver})'
p.labels = (labels[0], 'speedup')
p.series('speedup', speedup, '.-', label='n={n}')
p.plot()

p = Plot(res, 'procs', 'img/efficiency_{ver}.png')
p.params = ['ver']
p.group_by = ['n']
p.title = 'Efficiency ({ver})'
p.labels = (labels[0], 'efficiency')
p.series('efficiency', efficiency, '.-', label='n={n}')
p.plot()

forKf = res.filter(lambda row: row['procs'] > 1)
p = Plot(forKf, 'procs', 'img/serial_fraction_{ver}.png')
p.params = ['ver']
p.group_by = ['n']
p.title = 'Serial fraction ({ver})'
p.labels = (labels[0], 'serial fraction')
p.series('sf', serial_fraction, '.-', label='n={n}')
p.plot()

noSmall = forKf.filter(lambda row: row['n'] > 200)
p = Plot(noSmall, 'procs', 'img/serial_fraction_filtered_{ver}.png')
p.params = ['ver']
p.group_by = ['n']
p.title = 'Serial fraction ({ver})'
p.labels = (labels[0], 'serial fraction')
p.series('sf', serial_fraction, '.-', label='n={n}')
p.plot()

# Scaled
res = readResults('data/data_scaled', *fields)
p = Plot(res, 'procs', 'img/scaled_times_{ver}_{n}.png')
p.params = ('ver', 'n')
p.title = 'Total running time\n({ver}, n={n})'
p.labels = labels
p.series('min', Min('total'), '--')
p.series('max', Max('total'), '--')
p.series('avg', Avg('total'), dev=True)
p.plot()

p = Plot(res, 'procs', 'img/scaled_summary_{ver}.png')
p.params = ['ver']
p.group_by = ['n']
p.title = 'Total running time\n({ver})'
p.labels = labels
p.series('avg', Avg('total'), '.-', label='n={n}')
p.plot()

p = Plot(res, 'procs', 'img/scaled_details_{ver}_{n}.png')
p.params = ('ver', 'n')
p.title = 'Times of specific operations\n({ver}, n={n})'
p.labels = labels
p.series('work', Avg('work'))
p.series('bcast', Avg('bcast'))
p.series('scatter', Avg('scatter'))
p.series('gather', Avg('gather'))
p.stacked()


base_times = res.where(procs=1).select('ver', 'n', total=avg)


def scaled_speedup(row):
    ver, n, p = row['ver'][0], row['n'][0], row['procs']
    t = base_times.where(ver=ver, n=n).single()['total']
    return p * t / avg(row['total'])


def scaled_efficiency(row):
    return scaled_speedup(row) / row['procs']


def scaled_serial_fraction(row):
    p = row['procs']
    return (1.0 / scaled_speedup(row)) / (1 - 1.0 / p)


p = Plot(res, 'procs', 'img/scaled_speedup_{ver}.png')
p.params = ['ver']
p.group_by = ['n']
p.title = 'Speedup ({ver})'
p.labels = (labels[0], 'speedup')
p.series('speedup', scaled_speedup, '.-', label='n={n}')
p.plot()

p = Plot(res, 'procs', 'img/scaled_efficiency_{ver}.png')
p.params = ['ver']
p.group_by = ['n']
p.title = 'Efficiency ({ver})'
p.labels = (labels[0], 'efficiency')
p.series('efficiency', scaled_efficiency, '.-', label='n={n}')
p.plot()

forKf = res.filter(lambda row: row['procs'] > 1)
p = Plot(forKf, 'procs', 'img/scaled_serial_fraction_{ver}.png')
p.params = ['ver']
p.group_by = ['n']
p.title = 'Serial fraction ({ver})'
p.labels = (labels[0], 'serial fraction')
p.series('sf', scaled_serial_fraction, '.-', label='n={n}')
p.plot()

noSmall = forKf.filter(lambda row: row['n'] > 200)
p = Plot(noSmall, 'procs', 'img/scaled_serial_fraction_filtered_{ver}.png')
p.params = ['ver']
p.group_by = ['n']
p.title = 'Serial fraction ({ver})'
p.labels = (labels[0], 'serial fraction')
p.series('sf', scaled_serial_fraction, '.-', label='n={n}')
p.plot()
