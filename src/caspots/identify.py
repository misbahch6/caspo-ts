from __future__ import print_function

import math
import os
import tempfile
import time
from typing import Sequence

from caspo.core import Dataset, LogicalNetwork
from caspo.core.hypergraph import HyperGraph
from clingo.control import Control
from clingo.solving import Model
from clingo.symbol import Function, Symbol

from caspots.config import aspf
from caspots.utils import dbg

CrunchedData = tuple[set[tuple[Symbol]], dict[str, dict[tuple[Symbol], float]]]


def crunch_data(answer: Sequence[Symbol], predicate: str, factor: float) -> CrunchedData:
    """
    Process and organize data from Symbols into 'obs' and 'bin' categories.

    Args:
        answer: Sequence of Symbol objects to process.
        predicate: String specifying the predicate for binary data.
        factor: Float value to scale 'obs' data.

    Returns:
        Tuple containing a set of unique keys and a dictionary of processed
        data.
    """
    factor = float(factor)
    data = {"obs": {}, "bin": {}}
    keys = set()
    for a in answer:
        p = a.name
        if p in ["obs", predicate]:
            args = a.arguments
            key = tuple(args[:3])
            val = float(args[3].number)
            if p == "obs":
                val /= factor
            t = "obs" if p == "obs" else "bin"
            data[t][key] = val
            keys.add(key)
    return keys, data


def calculate_mse(cd: CrunchedData) -> float:
    """
    Calculate the Mean Squared Error (MSE) from CrunchedData.

    Args:
        cd: CrunchedData containing processed observation and binary data.

    Returns:
        Float value representing the square root of the average squared
        difference between 'obs' and 'bin' data.
    """
    cum = 0
    keys, data = cd
    n = 0
    for key in keys:
        if key not in data["obs"]:
            continue
        n += 1
        cum += (data["obs"][key] - data["bin"][key]) ** 2
    return math.sqrt(cum / n)


def count_predicate(answer: Sequence[Symbol], predicate: str) -> int:
    """
    Count occurrences of a specific predicate in a sequence of Symbols.

    Args:
        answer: Sequence of Symbol objects to search.
        predicate: String representing the predicate to count.

    Returns:
        Number of Symbols with matching predicate name.
    """
    return sum(1 for a in answer if a.name == predicate)


class ASPSample:
    """
    Represents a sample from an Answer Set Programming (ASP) solution.

    Attributes:
        atoms: Sequence of Symbol objects representing atoms in the ASP model.
        optimization: Sequence of integers representing optimization values.
    """

    atoms: Sequence[Symbol]
    optimization: Sequence[int]

    def __init__(self, opts, model: Model):
        """
        Initialize ASPSample with options and ASP model.

        Args:
            opts: Options object containing configuration settings.
            model: ASP model object.
        """
        self.opts = opts
        self.atoms = model.symbols(atoms=True)
        self.optimization = model.cost

    def asp_exclusion(self) -> str:
        """
        Generate ASP exclusion constraint based on current atoms.

        Returns:
            String representation of the ASP exclusion constraint.
        """
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
                "%d{clause(J,V,B): edge(J,V,B)}%d" % (nb_clause, nb_clause),
            ]
        return f":- {', '.join(map(str, clauses))}."

    def mse(self) -> tuple[float, float]:
        """
        Calculate Mean Squared Error for measured and guessed data.

        Returns:
            Tuple of (MSE for measured data, MSE for guessed data).
        """
        cd_measured = crunch_data(self.atoms, "measured", self.opts.factor)
        cd_guessed = crunch_data(self.atoms, "guessed", self.opts.factor)
        mse0 = calculate_mse(cd_measured)
        mse = calculate_mse(cd_guessed)
        return (mse0, mse)

    def network(self, hypergraph: HyperGraph) -> LogicalNetwork:
        """
        Create a LogicalNetwork from the sample's atoms and given hypergraph.

        Args:
            hypergraph: Hypergraph object to use in network creation.

        Returns:
            LogicalNetwork object constructed from the sample's atoms.
        """
        tuples = (tuple(arg.number for arg in f.arguments) for f in self.atoms if f.match("dnf", 2))
        return LogicalNetwork.from_hypertuples(hypergraph, tuples)

    def trace(self, dataset: Dataset) -> Dataset:
        """
        Update the given dataset using the 'guessed' predicates from the sample.

        Args:
            dataset: Dataset object to be updated.

        Returns:
            Updated dataset with modifications based on 'guessed' predicates.
        """
        # rewrite dataset using guessed predicate
        for a in self.atoms:
            if a.name == "guessed":
                eid, t, node, value = a.arguments
                if node not in dataset.readout:
                    continue
                if dataset.experiments[eid].obs[t][node] != value:
                    # print(((eid,t,node),dataset.experiments[eid].obs[t][node], value), file=sys.stderr)
                    dataset.experiments[eid].obs[t][node] = value
        return dataset


class ASPSolver:
    def __init__(self, termset, opts, domain=None):
        self.termset = termset
        self.data = termset.to_str()
        self.opts = opts
        self.debug = opts.debug
        if domain is None:
            self.domain = [aspf("guessBN.lp")]
            if opts.fully_controllable:
                self.domain.append(aspf("guessBN-controllable.lp"))
        else:
            self.domain = [domain]

    def default_control(self, *args):
        control = Control(["--conf=trendy", "--stats", "--opt-strat=usc"] + list(args))
        control.add("base", [], "#show.")
        for f in self.domain:
            control.load(f)
        control.load(aspf("supportConsistency.lp"))
        control.load(aspf("normalize.lp"))
        control.add("base", [], self.data)
        return control

    def sample(self, first, scripts=(), weight=None) -> ASPSample | None:
        control = self.default_control()
        if weight:
            control.load(aspf("tolerance.lp"))
            control.add(
                "base",
                [],
                "#const minWeight=%s. #const maxWeight=%s" % (weight, weight),
            )

        control.load(aspf("showMeasured.lp"))
        if self.opts.family == "subset":
            control.load(aspf("minimizeSizeOnly.lp"))
        if first:
            control.load(aspf("minimizeWeightOnly.lp"))
        for f in scripts:
            control.load(f)
        control.ground([("base", [])])
        with control.solve(yield_=True) as hnd:
            for model in hnd:
                return ASPSample(self.opts, model)

        return None

    def solution_samples(self):
        i = 1
        if self.debug:
            dbg("# model %d" % i)
        s = self.sample(True)
        yield s

        weight = s.optimization
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
                    dbg("# model %d" % i)
                yield s
                with open(excludelp, "a") as f:
                    f.write("%s\n" % s.asp_exclusion())
            else:
                print("# Enumeration complete")
                break
        os.unlink(excludelp)

    def solutions(self, on_model, on_model_weight=None, limit=0, force_weight=None):
        control = self.default_control("0")

        do_mincard = self.opts.family == "mincard" or self.opts.force_size is not None
        do_subsets = self.opts.family == "subset" or (self.opts.family == "mincard" and self.opts.mincard_tolerance)

        control.load(aspf("minimizeWeightOnly.lp"))
        if do_mincard:
            control.load(aspf("minimizeSizeOnly.lp"))

        control.ground([("base", [])])

        control.load(aspf("show.lp"))
        control.ground([("show", [])])

        # ****Flavio****

        start = time.time()

        if force_weight is None:
            control.assign_external(Function("tolerance"), False)
            dbg("# start initial solving")
            opt = []
            res = control.solve(on_model=lambda model: opt.append(model.cost))
            dbg("# initial solve took %s" % (time.time() - start))

            optimizations = opt.pop()
            dbg("# optimizations = %s" % optimizations)

            weight = optimizations[0]
            if do_mincard:
                minsize = optimizations[1]
            if weight > 0 and on_model_weight is not None:
                for sample in self.solution_samples():
                    on_model_weight(sample)
                return

            control.assign_external(Function("tolerance"), True)
        else:
            weight = force_weight
            dbg("# force weight = %d" % weight)

        max_weight = weight + self.opts.weight_tolerance
        control.add(
            "minWeight",
            [],
            ":- not "
            + str(weight)
            + " #sum {Erg,E,T,S : measured(E,T,S,V), not guessed(E,T,S,V), toGuess(E,T,S), obs(E,T,S,M), Erg=50-M, M < 50;"
            + " Erg,E,T,S : measured(E,T,S,V), not guessed(E,T,S,V), toGuess(E,T,S), obs(E,T,S,M), Erg=M-49, M >= 50} "
            + str(max_weight)
            + " .",
        )
        control.ground([("minWeight", [])])

        control.configuration.solve.opt_mode = "ignore"
        control.configuration.solve.project = 1  # ????
        control.configuration.solve.models = limit  # ????
        # print control.conf.solver[0].keys()

        if do_mincard:
            if self.opts.force_size:
                maxsize = self.opts.force_size
            else:
                maxsize = minsize + self.opts.mincard_tolerance
            control.add(
                "minSize",
                [],
                ":- not " + str(minsize) + " #sum {L,I,J : dnf(I,J) , hyper(I,J,L)} " + str(maxsize) + ".",
            )
            control.ground([("minSize", [])])

        if do_subsets:
            control.configuration.solve.enum_mode = "domRec"
            control.configuration.solver[0].heuristic = "Domain"
            control.configuration.solver[0].dom_mod = "5,16"

        start = time.time()
        dbg("# begin enumeration")
        res = control.solve(on_model=on_model)
        dbg("# enumeration took %s" % (time.time() - start))
