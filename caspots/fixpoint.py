
import gringo

import pandas as pd

from .asputils import *

class Fixpoint(object):
    def __init__(self, id, state):
        self.id = id
        self.state = state

    @classmethod
    def from_file(celf, filename):
        df = pd.read_table(filename, index_col=0, header=None, delim_whitespace=True)
        return [Fixpoint(i, dict(df[i+1][df[i+1] >= 0])) for i in range(df.shape[1])]

    def to_funset(self):
        fs = funset()
        fs.update([gringo.Fun("fp", [self.id, n, v]) \
                    for (n,v) in self.state.items()])
        return fs



