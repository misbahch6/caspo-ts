
from __future__ import print_function

import math
from math import log
import os
from subprocess import *
import sys
import tempfile
import time
import random

#import gringo
import clingo
#from caspo.core import LogicalNetwork

from caspots.config import *
from caspots import asputils
from caspots.utils import *
from .console import *
#from caspo.core import Graph, HyperGraph, LogicalNetwork, LogicalNetworkList
from .graph import Graph
from .hypergraph import HyperGraph
from .logicalnetwork import LogicalNetwork, LogicalNetworkList
from .networks import *
from xor_counting import Propagator
from crossvar import globalvariables
from pprint import pprint

#print (contraintonexp)
def crunch_data(answer, predicate, factor):
    factor = float(factor)
    data = {
        "obs": {},
        "bin": {}
    }
    keys = set()
    for a in answer:
        p = a.name
        if p in ["obs", predicate]:
            args = a.arguments
            key = tuple(args[:3])
            val = args[3].number
            if p == "obs":
                val /= factor
            t = "obs" if p == "obs" else "bin"
            data[t][key] = val
            keys.add(key)
    return (keys, data)

def MSE(cd):
    cum = 0
    keys, data = cd
    n = 0
    for key in keys:
        if key not in data["obs"]:
            continue
        n += 1
        cum += (data["obs"][key] - data["bin"][key])**2
    return math.sqrt(cum/n)

def count_predicate(answer, predicate):
    return len([a for a in answer if a.name == predicate])

class ASPSample:
    def __init__(self, opts, model):
        self.opts = opts
        self.atoms = model.symbols(atoms=True)
        self.optimization = model.cost

    def weight(self):
        return self.optimization

    def asp_exclusion(self):
        predicates = ["formula", "dnf", "clause"]
        if self.opts.enum_traces:
            predicates += ["guessed"]
        clauses = [a for a in self.atoms if a.name in predicates]
        if self.opts.family == "all":
            nb_formula = count_predicate(self.atoms, "formula")
            nb_dnf = count_predicate(self.atoms, "dnf")
            nb_clause = count_predicate(self.atoms, "clause")
            clauses += [
                "%d{formula(V,I): node(V,I)}%d" % (nb_formula, nb_formula),
                "%d{dnf(I,J): hyper(I,J,N)}%d" % (nb_dnf, nb_dnf),
                "%d{clause(J,V,B): edge(J,V,B)}%d" % (nb_clause, nb_clause)
            ]
        return ":- %s." % ", ".join(map(str, clauses))

    def mse(self):
        cd_measured = crunch_data(self.atoms, "measured", self.opts.factor)
        cd_guessed = crunch_data(self.atoms, "guessed", self.opts.factor)
        mse0 = MSE(cd_measured)
        mse = MSE(cd_guessed)
        return (mse0, mse)

    def network(self, hypergraph):
        tuples = (f.arguments for f in self.atoms if f.name == "dnf")
        return LogicalNetwork.from_hypertuples(hypergraph, tuples)

    def trace(self, dataset):
        # rewrite dataset using guessed predicate
        for a in self.atoms:
            if a.name == "guessed":
                eid, t, node, value = a.arguments
                if node not in dataset.readout:
                    continue
                if dataset.experiments[eid].obs[t][node] != value:
                    #print(((eid,t,node),dataset.experiments[eid].obs[t][node], value), file=sys.stderr)
                    dataset.experiments[eid].obs[t][node] = value
        return dataset


class ASPSolver:
    def __init__(self, termset, opts, domain=None):
        self.termset = termset
        self.data = termset.to_str()
        self.opts = opts
	#self.atoms = model.atoms()
        self.debug = opts.debug
        if domain is None:
            self.domain = [aspf("guessBN.lp")]
            if opts.fully_controllable:
                self.domain.append(aspf("guessBN-controllable.lp"))
        else:
            self.domain = [domain]

    def default_control(self, *args):
        control = clingo.Control([ "--stats", "--opt-strat=usc", #"--no-ufs-check",#, "--sign-def=rnd", "--sign-fix" #random solution
] + list(args))
        #"--conf=trendy"
        for f in self.domain:
            control.load(f)
        control.load(aspf("supportConsistency.lp"))
        control.load(aspf("normalize.lp"))
        control.add("base", [], self.data)
        return control

    def sample(self, first, scripts=[], weight=None):
        control = self.default_control("--no-ufs-check")
        if weight:
            control.load(aspf("tolerance.lp"))
            control.add("base", [], "#const minWeight=%s. #const maxWeight=%s" %
                                        (weight,weight))

        control.load(aspf("showMeasured.lp"))
        if self.opts.family == "subset":
            control.load(aspf("minimizeSizeOnly.lp"))
        if first:
            control.load(aspf("minimizeWeightOnly.lp"))
        for f in scripts:
            control.load(f)
        control.ground([("base", [])])

        with control.solve(yield_=True) as solutions:
            for model in solutions:
                #print (model)
                return ASPSample(self.opts, model)

    def solution_samples(self):
        i = 1
        if self.debug:
            dbg("# model %d" %i)
        s = self.sample(True)
        yield s

        weight = s.weight()
        fd, excludelp = tempfile.mkstemp(".lp")
        os.close(fd)

        with open(excludelp, "w") as f:
            f.write("%s\n" % s.asp_exclusion())

        args = [excludelp]
        while True:
            s = self.sample(False, args, weight=weight)
            if s:
                i += 1
                if self.debug:
                    dbg("# model %d" %i)
                yield s
                with open(excludelp, "a") as f:
                    f.write("%s\n" % s.asp_exclusion())
            else:
                print("# Enumeration complete")
                break
        #os.unlink(excludelp)

    def solutions(self, on_model, on_model_weight=None, limit=0,
                    force_weight=None):

        control = self.default_control("0")

        do_mincard = self.opts.family == "mincard" \
            or self.opts.force_size is not None
        do_subsets = self.opts.family == "subset" \
            or (self.opts.family =="mincard" and self.opts.mincard_tolerance)

        control.load(aspf("minimizeWeightOnly.lp"))
        if do_mincard:
            control.load(aspf("minimizeSizeOnly.lp"))

        control.ground([("base", [])])

        control.load(aspf("show.lp"))
        control.ground([("show", [])])


        #if crossvar.myflag:
            #mystr = open("constraintssss.lp", 'r').read()
            #control.add("RC", [], mystr)
            #control.load(aspf("constraintssss.lp"))
            #control.ground([("RC", [])]) 

            #print(crossvar.FO)	
            #print(crossvar.myflag)
            #print("hello from the other side")


        #Flavio-Xor'''


        start = time.time()

        if force_weight is None:
            control.assign_external(clingo.Function("tolerance"),False)
            dbg("# start initial solving")
            opt = []
            res = control.solve(None, lambda model: opt.append(model.cost))
            print(opt)
            dbg("# initial solve took %s" % (time.time()-start))

            optimizations = opt.pop()
            dbg("# optimizations = %s" % optimizations)

            weight = optimizations[0]
            if do_mincard:
                minsize = optimizations[1]
            if weight > 0 and on_model_weight is not None:
                for sample in self.solution_samples():
                    on_model_weight(sample)
                return

            control.assign_external(clingo.Function("tolerance"),True)
        else:
            weight = force_weight
            dbg("# force weight = %d" % weight)

        max_weight = weight + self.opts.weight_tolerance
        print("weight %s",weight)
        control.add("minWeight", [], ":- not " + str(weight) + " #sum {Erg,E,T,S : measured(E,T,S,V), not guessed(E,T,S,V), toGuess(E,T,S), obs(E,T,S,M), Erg=50-M, M < 50;" + " Erg,E,T,S : measured(E,T,S,V), not guessed(E,T,S,V), toGuess(E,T,S), obs(E,T,S,M), Erg=M-49, M >= 50} " + str(max_weight) + " .")
        control.ground([("minWeight", [])])

        control.configuration.solve.opt_mode ="ignore"#"optN" #
        control.configuration.solve.project = "project" # ????
        control.configuration.solve.models = limit # ????
        #print control.conf.solver[0].keys()


        if do_mincard:
            if self.opts.force_size:
                maxsize = self.opts.force_size
            else:
                maxsize = minsize + self.opts.mincard_tolerance
            control.add("minSize", [], ":- not " + str(minsize) + " #sum {L,I,J : dnf(I,J) , hyper(I,J,L)} " + str(maxsize) + ".")
            control.ground([("minSize", [])])

        if do_subsets:
        # ----------------------------- Misbah ------------------------------------------
            control.configuration.solver[0].heuristic = "Domain"
            #control.configuration.solve.enum_mode = "domRec"
            #control.configuration.solver[0].dom_mod = "5,16"
            
            class Context:
                def __init__(self):
                    self.dnf_args = []
                    self.ndnf_args = []
                def dnf(self):
                    return self.dnf_args
                def ndnf(self):
                    return self.ndnf_args

            ctx = Context()

            start = time.time()
            dbg("# begin enumeration")
            
            control.load(aspf("diversity.lp"))
            control.ground([("diversity", [])], ctx)
            
            models = 0
            while True:
                atoms, natoms = [], []
                with control.solve(yield_=True) as solutions:
                    for model in solutions:
                        atoms = model.symbols(atoms=True)
                        natoms = model.symbols(atoms=True, complement=True)
                        on_model(model)
                        #print ("Model: True Atoms", atoms, "Model: False Atoms", natoms)
                        #if globalvariables.check:
                            #model_found = True
                        break
                    else: 
                        #if not model_found:
                        break

                ctx.dnf_args = []
                for atom in atoms:
                    n, a = atom.name, atom.arguments
                    if n == "dnf" and len(a) == 2:
                        #print (atom)
                        control.assign_external(clingo.Function("before",a),True)
                        ctx.dnf_args.append(tuple(a))
                for atom in natoms:
                    n, a = atom.name, atom.arguments
                    if n == "dnf" and len(a) == 2:
                        control.assign_external(clingo.Function("before",a),False)

                control.ground([("skip", [])], ctx)
                models += 1
            dbg("# enumeration took %s" % (time.time()-start))
        # ----------------------------- Misbah ------------------------------------------

        '''#Flavio-Xor	
        if self.opts.xor is not None:
            file = open("xorfile.txt","w")
            parities = []
            constraints = [] 

            clause = [atom.symbol for atom in control.symbolic_atoms.by_signature("clause",3)]
            dnf = [atom.symbol for atom in control.symbolic_atoms.by_signature("dnf",2)]
            literals = clause + dnf
            for element in literals:
                file.write("%s\n"%(element))
            
            # Read grounded atoms and randomly add xor constraints
            if self.opts.xor > 0:
                estimateds = self.opts.xor
            else:
                estimateds = int(log(len(literals),2))
            file.write("adding %s xor constraints\n"%(estimateds))

            for i in range(estimateds):
                size = random.randint(1, (len(literals) + 1) / 2)
                terms = random.sample(literals, size)
                parity = random.randint(0,1)
                print("constraint: %s, parity: %s, terms: %s"%(i+1, parity, terms))
                constraints.append(terms)
                
                parities.append(parity)

            for index in range(len(constraints)):
                terms = " ; ".join(str(x) for x in constraints[index])
                aspconstr = ":- X = { %s }, X\\2==%s."%(terms, parities[index])
                file.write("%s\n"%(aspconstr))
                #control.add("q", ["t"], aspconstr)
                #control.ground([("q", [terms])])
            file.close()'''

        if self.opts.xor is not None:
            control.register_propagator(Propagator(self.opts.xor))
        
        if not do_subsets:
            start = time.time()
            dbg("# begin enumeration")
        
            res = control.solve(on_model=on_model)
            pprint(control.statistics)
            #res = control.solve_async(None, on_model, on_finish)
            #res.wait()
            dbg("# enumeration took %s" % (time.time()-start))
        #pprint(control.statistics)
            #print(on_model)

#Misbah --- Solving at Execution time ---

#Misbah --- Solving at Execution time ---
