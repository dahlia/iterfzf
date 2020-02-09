"""Currently ``fzf`` and ``iterfzf()`` takes only some kind of strings,
so you can't pass arbitrary Python objects into that.  Also there is no way
to give each item some "hidden keys" besides displayed values.

Therefore, if you want to show items in a dictionary, and make users to choose
some items, then get chosen item keys, you need to give ``iterfzf()`` string
representations of key-value pairs.  Here's an example:

"""
from iterfzf import iterfzf


def fzf_dict(d, multi):
    r"""This assumes keys must have no tabs, hence ``'\t'`` as a separator."""
    options = ('{0}\t{1}'.format(k, v) for k, v in d.items())
    for kv in iterfzf(options, multi=multi):
        yield kv[:kv.index('\t')]


def main():
    d = {
        '1': 'foo',
        '2': 'bar',
        '3': 'spam',
        '4': 'egg',
    }
    print(iterfzf(d.values()))
    keys = fzf_dict(d, multi=True)
    for key in keys:
        print(repr(key), '=>', repr(d[key]))


if __name__ == '__main__':
    main()
