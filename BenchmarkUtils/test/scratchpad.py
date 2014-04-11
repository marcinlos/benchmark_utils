'''
Created on Mar 31, 2014

@author: los
'''
from random import random
from benchmark.util import *
from benchmark.run import *
from benchmark.data import equal
from benchmark.io import saveResults, FileSink, readResults
from benchmark.aggr import *#avg, Dev
from benchmark.plot import plot, Plot

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

# s = 0.2
# 
# 
# def f(n, p):
#     x = 1 + 0.3 * (random() - 0.5)
#     return {'dupa': x * n * (s + (1 - s) / p), 'fak': random()}
# 
# fmt = DataFormat(['n', 'p'], ['dupa', 'fak'])
# # r = Runner(f, fmt, sink=FileSink.make('dupa'))
# 
# 
# r = Runner(f, fmt)
# args = [seq(10, 100, 1000), seq(xrange(1, 9))]
# r.repeat(100, args)

fields = [
    ('ver', str), ('n', int), ('procs', int),
    ('total', float), ('bcast', float), ('scatter', float),
    ('work', float), ('gather', float)
]

res = readResults('../data/data', *fields)

p = Plot(res, 'procs', 'times_{ver}_{n}')
p.params = ('ver', 'n')
p.title = 'Total running time\n({ver}, n={n})'
p.labels = ('# of processes', 'total time [ms]')
p.plot('min', Min('total'), ':')
p.plot('avg', Avg('total'))
p.plot('median', Median('total'))
p.plot('max', Max('total'), ':')
p.generate()


pat = 'dupa_{ver}_{n}'
title = 'Total running time\n({ver}, n={n})'
xlabel = '# of processes'
ylabel = 'total time [ms]'

cols = [('min', Min('total')),
        ('avg', Avg('total')),
        ('median', Median('total')),
        ('max', Max('total'))]

plot(res, pat, title, xlabel, ylabel, ['ver', 'n'], 'procs', *cols)


r = res.filter(equal(ver='mpihosts_multicore', n=1500))\
    .select('procs', total_min=Min('total'), total_avg=Avg('total'),
        total_med=Median('total'), total_max=Max('total'))\
    .orderBy('procs')


procs = r.col('procs')
tmin = r.col('total_min')
tavg = r.col('total_avg')
tmed = r.col('total_med')
tmax = r.col('total_max')

fig, ax = plt.subplots(figsize=(9, 5))

ax.set_title('Total running time\n(no multicore, n=1500)')
ax.set_xlabel('# of processes')
ax.set_ylabel('total time [ms]')
ax.grid(True)
ax.plot(procs, tmin, '--', label='min')
ax.plot(procs, tavg, label='avg')
ax.plot(procs, tmed, label='median')
ax.plot(procs, tmax, '--', label='max')
ax.legend(shadow=True)
fig.savefig('dupa.png', dpi=100)

#plt.show()


# res = r.sink
# print res.select('n', 'p', dupa=avg, fak=avg, dev=Dev('dupa'))
#  
# pat = 'data_{n}'
# cols = [('dupa', avg), ('fak', avg), ('dev', Dev('dupa'))]
# saveResults(res, pat, ['n'], 'p', *cols)
