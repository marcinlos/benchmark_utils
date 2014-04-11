
import matplotlib.pyplot as plt


class PlotDesc(object):
    def __init__(self, name, val, props=None, label=None):
        self.name = name
        self.val = val
        self.props = props
        self.label = label if label else name


class Plot(object):

    slots = ('data', 'params', 'out', 'title', 'ox', 'xlabel', 'ylabel',
        'cols')

    def __init__(self, data, ox=None, out=None, params=None):
        self.data = data
        self.ox = ox
        self.out = out
        self.params = params
        self.cols = []

    @property
    def labels(self):
        return (self.xlabel, self.ylabel)

    @labels.setter
    def labels(self, lab):
        xlab, ylab = lab
        self.xlabel = xlab
        self.ylabel = ylab

    def plot(self, name, val, props=''):
        desc = PlotDesc(name, val, props)
        self.cols.append(desc)

    def __col_dict(self):
        return dict((c.name, c.val) for c in self.cols)

    def generate(self):
        groups = self.data.groupBy(*self.params)
        for key, res in groups.iteritems():
            params = dict(zip(self.params, key))

            path = self.out.format(**params) + '.png'
            col_vals = self.__col_dict()
            rows = res.select(self.ox, **col_vals).orderBy(self.ox)

            main_axis = rows.col(self.ox)
            data = dict((c.name, rows.col(c.name)) for c in self.cols)

            fig, ax = plt.subplots(figsize=(9, 5))

            ax.set_title(self.title.format(**params))
            if self.xlabel:
                ax.set_xlabel(self.xlabel)
            if self.ylabel:
                ax.set_ylabel(self.ylabel)

            ax.grid(True)

            for c in self.cols:
                ax.plot(main_axis, data[c.name], c.props, label=c.label)

            ax.legend(framealpha=0.2)
            fig.savefig(path, dpi=100)
            plt.close(fig)


def plot(results, pattern, title, xlabel, ylabel, filesBy, main, *cols):
    groups = results.groupBy(*filesBy)
    for key, res in groups.iteritems():
        params = dict(zip(filesBy, key))

        path = pattern.format(**params) + '.png'
        rows = res.select(main, **dict(cols)).orderBy(main)

        main_axis = rows.col(main)
        data = dict((c, rows.col(c)) for c, _ in cols)
        fig, ax = plt.subplots(figsize=(9, 5))

        ax.set_title(title.format(**params))
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(True)

        for c, _ in cols:
            ax.plot(main_axis, data[c], label=c)

        ax.legend(shadow=True)
        fig.savefig(path, dpi=100)
