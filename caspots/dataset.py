
import sys

import pandas as pd
import numpy as np

#import gringo
import clingo 
#from caspo.core.setup import Setup
#from caspo.core.literal import Literal
#from caspo.core.clamping import Clamping, ClampingList

from .setup import Setup
from .literal import Literal
from .clamping import Clamping, ClampingList

from .asputils import *
from .utils import *

from crossvar import globalvariables
class Experiment:
    def __init__(self, id):
        self.id = id
        self.obs = {}
        self.dobs = {}
        self.mutations = {}

    def add_mutation(self, node, clamp):
        self.mutations[node] = clamp

    def add_obs(self, t, node, value, dvalue):
        if t not in self.obs:
            self.obs[t] = {}
            self.dobs[t] = {}
        self.obs[t][node] = value
        self.dobs[t][node] = dvalue

    def commit(self):
        if len(self.obs) == 1:
            warning("Experiment %d with clamping %s has only one data point (at time=%d)!"\
                        % (self.id, self.mutations, list(self.obs.keys())[0]))

    def __str__(self):
        buf = "Experiment(%d):\n" % self.id
        for a, c in sorted(self.mutations.items()):
            buf += "\t%2d %s\n" % (c,a)
        buf += "----\n"
        for t, values in sorted(self.obs.items()):
            buf += "\t%4d |" % t
            for n, v in sorted(values.items()):
                buf += "\t%s=%d" % (n,v)
            buf += "\n"
        buf += "----"
        return buf

class Dataset:
    def __init__(self, name, dfactor=100, discretize="round"):
        self.name = name
        self.dfactor = dfactor
        self.discretize = getattr(self, "discretize_%s" % discretize)

    def discretize_round(self, value):
        return int(round(self.dfactor*value))

    def binarize(self, dvalue):
        return 1 if dvalue >= self.dfactor/2 else 0

    def load_from_midas(self, midas, graph):
        df = pd.read_csv(midas)
        df.drop(df.columns[0], axis=1, inplace=True)
        df = df.reset_index(drop=True)

        def is_stimulus(name):
            return name.startswith('TR') and not name.endswith('i')
        def is_inhibitor(name):
            return name.startswith('TR') and name.endswith('i')
        def is_readout(name):
            return name.startswith('DV')

        stimuli = [c[3:] for c in [c for c in df.columns if is_stimulus(c)]]
        inhibitors = [c[3:-1] for c in [c for c in df.columns if is_inhibitor(c)]]
        readouts = [c[3:] for c in [c for c in df.columns if is_readout(c)]]
        self.setup = Setup(stimuli, inhibitors, readouts)

        self.stimulus = set(self.setup.stimuli)
        self.inhibitors = set(self.setup.inhibitors)
        self.readout = set(self.setup.readouts)
        self.experiments = {}

        exp_t = {}
        order = {}
        def exp_of_clamps(clamps, time=None):
            if time is not None:
                key = (clamps, time)
                if key not in order:
                    order[key] = 1
                else:
                    order[key] += 1
                key = (clamps, order[key])
            else:
                key = clamps
            if key not in exp_t:
                eid = len(exp_t)
                exp = Experiment(eid)
                for node, clamp in clamps:
                    exp.add_mutation(node, clamp)
                self.experiments[eid] = exp
                exp_t[key] = exp
                return exp
            else:
                return exp_t[key]

        for i, row in df.iterrows():
            clamps = set()
            for var, sign in row.filter(regex='^TR').iteritems():
                var = var[3:]
                sign = int(sign)
                if var in stimuli:
                    if sign == 1 or not len(graph.predecessors(var)):
                        clamps.add((var, sign or -1))
                elif sign == 1:
                    clamps.add((var[:-1], -1))
            clamps = tuple(clamps)

            times = list(set(map(int,row.filter(regex='^DA:').values)))
            if len(times) == 1:
                time = times[0]
            else:
                time = None
            exp = exp_of_clamps(clamps, time)

            for var, fvalue in row.filter(regex='^DV').iteritems():
                if np.isnan(fvalue):
                    continue
                var = var[3:]
                time = int(row.get("DA:%s" % var))
		#time = int(row.get("DA_%s" % var))
                dvalue = self.discretize(fvalue)
                bvalue = self.binarize(dvalue)
                exp.add_obs(time, var, bvalue, dvalue)

        todel = []
        for exp in self.experiments.values():
            exp.commit()
            if len(exp.obs) == 1 and 0 in exp.obs:
                todel.append(exp.id)
        for eid in todel:
            del self.experiments[eid]


    def to_funset(self):
        fs = funset(self.setup)
        clampings = []
        for exp in sorted(self.experiments.values(), key=lambda e: e.id):
            i = exp.id
            literals = [Literal(node, sign) for node, sign in \
                            exp.mutations.items()]
            clampings.append(Clamping(literals))
            for time, obs in exp.dobs.items():
                for var, dval in obs.items():
                    fs.add(clingo.Function('obs', [i, time, var, dval]))
        clampings = ClampingList(clampings)
        fs.update(clampings.to_funset("exp"))
        fs.add(clingo.Function('dfactor', [self.dfactor]))
        return fs

    def __str__(self):
        buf = "%s %s %s\n" % ("#"*10, self.name, "#"*10)
        buf += "\n".join(map(str, self.experiments.values()))
        return buf

