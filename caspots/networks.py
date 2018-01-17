
import itertools as it

import gringo

import pandas as pd

from .asputils import *

def domain_of_networks(networks, hypergraph, dataset):
    fs = funset(networks)
    domain = ["1{%s}1." % ("; ".join(["model(%d)" % i for i in range(len(networks))]))]

    formulas = set()
    for network in networks:
        formulas = formulas.union(it.imap(lambda (_, f): f, network.formulas_iter()))
    formulas = pd.Series(list(formulas))

    for i, network in enumerate(networks):
        for v, f in network.formulas_iter():
            f= gringo.Fun("formula", [v, formulas[formulas == f].index[0]])
            domain.append("%s :- model(%d)." % (f,i))

    return "%s%s\n" % (fs.to_str(), "\n".join(domain))

