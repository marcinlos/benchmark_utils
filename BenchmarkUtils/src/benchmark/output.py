

def center(text, width):
    fmt = '{:^' + str(width) + '}'
    return fmt.format(text)


def right(text, width):
    fmt = '{:>' + str(width) + '}'
    return fmt.format(text)


class ColumnDesc(object):
    def __init__(self, name, header=None, fmt=str):
        self.name = name
        self.header = header if header else name
        self.fmt = fmt


class TableFormatter(object):

    def __init__(self, data, cols, title, params=None):
        self.data = data
        self.cols = cols
        self.title = title
        self.params = params if params else {}
        self.col_width = [self.__max_col_width(col) + 3 for col in cols]

    def __max_col_width(self, col):
        w1 = len(col.header)

        def width(row):
            return len(self.__format_col(row, col))

        w2 = max(width(row) for row in self.data)
        return max(w1, w2)

    def __render_row(self, words):
        text = ''
        for word, width in zip(words, self.col_width):
            text += right(word, width)
        return text

    def __render_title(self):
        width = sum(self.col_width)
        return center(self.title, width)

    def __format_col(self, row, col):
        val = row[col.name]
        fmt = col.fmt
        if isinstance(fmt, str):
            return fmt.format(val)
        else:
            return fmt(val)

    def __format_values(self, row):
        strings = []
        for col in self.cols:
            text = self.__format_col(row, col)
            strings.append(text)
        return strings

    def write(self, out):
        title = self.__render_title()
        out.write(title + '\n' + '\n')

        header = self.__render_row(col.header for col in self.cols)
        out.write(header + '\n')

        for row in self.data:
            vals = self.__format_values(row)
            s = self.__render_row(vals)
            out.write(s + '\n')
