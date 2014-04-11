
from benchmark.data import DataFormat
from benchmark.run import Runner, retry, runCmd
from benchmark.io import saveResults, FileSink


args = ['ver', 'n', 'procs']
results = ['total', 'bcast', 'scatter', 'work', 'gather']
fmt = DataFormat(args, results)

