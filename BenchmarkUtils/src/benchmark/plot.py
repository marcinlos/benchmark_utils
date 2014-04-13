
import matplotlib.pyplot as plt
from .aggr import Dev


class PlotDesc(object):
    def __init__(self, name, val, props=None, label=None, dev=False):
        self.name = '_' + name + '_derived'
        self.val = val
        self.props = props
        self.label = label if label else name
        self.dev = dev


class Plot(object):

    def __init__(self, data, ox=None, out=None, params=None):
        self.data = data
        self.ox = ox
        self.out = out
        self.params = params
        self.xlabel = None
        self.ylabel = None
        self.cols = []
        self.grid = False
        self.group_by = ()

    @property
    def labels(self):
        return (self.xlabel, self.ylabel)

    @labels.setter
    def labels(self, lab):
        xlab, ylab = lab
        self.xlabel = xlab
        self.ylabel = ylab

    def series(self, name, val, props='', label=None, dev=False):
        desc = PlotDesc(name, val, props, label, dev)
        self.cols.append(desc)

    def __col_dict(self):
        d = {}
        for c in self.cols:
            d[c.name] = c.val
            if c.dev:
                d[c.name + '#dev'] = Dev(*c.val.args)
        return d

    def __ordinary_plot(self, ax, groups, col_vals):
        for plotKey in sorted(groups.keys()):
            plotRes = groups[plotKey]
            rows = plotRes.select(self.ox, **col_vals).orderBy(self.ox)
            main_axis = rows.col(self.ox)
            plotParams = dict(zip(self.group_by, plotKey))
            for c in self.cols:
                data = rows.col(c.name)
                label = c.label.format(**plotParams)
                ax.plot(main_axis, data, c.props, label=label)
                if c.dev:
                    dev = rows.col(c.name + '#dev')
                    ax.errorbar(main_axis, data, yerr=dev, fmt='.')
            ax.legend(framealpha=0.2)

    def __stacked_plot(self, ax, groups, col_vals):
        data, labels = [], []
        for plotKey in sorted(groups.keys()):
            plotRes = groups[plotKey]
            rows = plotRes.select(self.ox, **col_vals).orderBy(self.ox)
            main_axis = rows.col(self.ox)
            plotParams = dict(zip(self.group_by, plotKey))
            for c in self.cols:
                data.append(rows.col(c.name))
                label = c.label.format(**plotParams)
                labels.append(label)

        stack = ax.stackplot(main_axis, *data, linewidth=0.5)
        proxy_rects = [plt.Rectangle((0, 0), 1, 1, fc=pc.get_facecolor()[0])
            for pc in stack]
        ax.legend(proxy_rects, labels, framealpha=0.2)

    def __generate_plot(self, key, res, method):
        params = dict(zip(self.params, key))

        path = self.out.format(**params)
        col_vals = self.__col_dict()

        fig, ax = plt.subplots(figsize=(12, 7))
        ax.set_title(self.title.format(**params))

        groups = res.groupBy(*self.group_by)
        method(ax, groups, col_vals)

        if self.xlabel:
            ax.set_xlabel(self.xlabel)
        if self.ylabel:
            ax.set_ylabel(self.ylabel)

        ax.grid(self.grid)
        ax.set_ylim(ymin=0)
        fig.savefig(path, dpi=100)
        plt.close(fig)

    def __generate_all_plots(self, method):
        groups = self.data.groupBy(*self.params)
        for key, res in groups.iteritems():
            self.__generate_plot(key, res, method)

    def plot(self):
        self.__generate_all_plots(self.__ordinary_plot)

    def stacked(self):
        self.__generate_all_plots(self.__stacked_plot)
