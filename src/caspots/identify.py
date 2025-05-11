"""
This module is provides functions to compute Boolean networks using Answer Set
Programming (ASP). It includes utilities for data processing, error
calculation, and ASP-based problem solving.

- Processes ASP solution data into structured formats.
- Calculates Mean Squared Error (MSE) between observed and guessed data.
- Manages ASP samples and constructs logical networks.
- Runs an ASP solver to generate and iterate over solutions.
"""

from dataclasses import dataclass
import math
from math import log
import os
import tempfile
import time
import random
from typing import Any, Callable, Iterator, Literal, Optional, Sequence
from pprint import pprint

from caspo.core import Dataset, LogicalNetwork
from caspo.core.hypergraph import HyperGraph
from clingo import Configuration
from clingo.control import Control
from clingo.solving import Model
from clingo.symbol import Function, Symbol

from .asputils import funset
from .config import aspf
from .utils import dbg
from .crossvar import globalvariables

CrunchedData = tuple[set[tuple[Symbol]], dict[str, dict[tuple[Symbol], float]]]

@dataclass
class SolverOptions:
    pkn: str
    dataset: str
    output: Optional[str] = None
    family: Literal["all", "subset", "mincard"] = "subset"
    mincard_tolerance: int = 0
    weight_tolerance: int = 0
    enum_traces: bool = False
    fully_controllable: bool = True
    force_weight: Optional[int] = None
    force_size: Optional[int] = None
    debug: bool = False
    RC: Optional[int] = None
    true_positives: bool = False
    limit: int = 0
    semantics: str = "u_general"
    range_from: int = 0
    range_length: int = 0
    networks: Optional[str] = None
    diversify: int = 0
    check_exact: bool = False
    factor: int = 100

#--------------These are data processing functions-----------------
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
    print("I am in crunch_data")

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
    print("I am in calculate_mse")

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
    print("I am in count_predicate")

    return sum(1 for a in answer if a.name == predicate)
#---------------------------------------------------------------

# -----------------ASPSample class is used to handle one solution-----------------
class ASPSample:
    """
    Defines the ASPSample class and related helper functions 
     for handling the output of Answer Set Programming (ASP) solvers 
     in the context of Boolean network inference.

    Attributes:
        atoms: Sequence of Symbol objects representing atoms in the ASP model.
        optimization: Sequence of integers representing optimization values.
    """

    atoms: Sequence[Symbol]
    optimization: Sequence[int]

    def __init__(self, opts: SolverOptions, model: Model):
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
        Produces an ASP constraint to exclude the current solution 
        from future searches (for solution enumeration).

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
        print("I am in asp_exclusion")
        return f":- {', '.join(map(str, clauses))}."

    def mse(self) -> tuple[float, float]:
        """
        Calculates the mean squared error (MSE) between 
        observed and predicted (guessed) data in the sample.
        Returns:
            Tuple of (MSE for measured data, MSE for guessed data).
        """
        cd_measured = crunch_data(self.atoms, "measured", self.opts.factor)
        cd_guessed = crunch_data(self.atoms, "guessed", self.opts.factor)
        mse0 = calculate_mse(cd_measured)
        mse = calculate_mse(cd_guessed)
        print("I am in mse")

        return (mse0, mse)

    def network(self, hypergraph: HyperGraph) -> LogicalNetwork:
        """
        Constructs a LogicalNetwork object from the sample, 
        representing the inferred Boolean network.

        Args:
            hypergraph: Hypergraph object to use in network creation.

        Returns:
            LogicalNetwork object constructed from the sample's atoms.
        """
        print("I am in network")

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
        print("I am in trace")
        return dataset
#---------------------------------------------------------------

# -----------------ASPSolver class is used to solve ASP problems-----------------
class ASPSolver:
    """
    A solver for Answer Set Programming (ASP) problems.

    Attributes:
        termset: Set of terms for the ASP problem.
        data: String representation of the termset.
        opts: Options for the solver.
        debug: Flag for debug mode.
        domain: List of domain files for the ASP problem.
    """

    termset: funset
    data: str
    opts: SolverOptions
    debug: bool
    domain: list[str]

    def __init__(self, termset: funset, opts: SolverOptions, domain: str | None):
        """
        Initialize the ASPSolver.

        Args:
            termset: Set of terms for the ASP problem.
            opts: Options for the solver.
            domain: Domain file or None for default domain.
        """
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

    def default_control(self, *args: str) -> Control:
        """
        Create a default Control object for ASP solving.

        Args:
            *args: Additional arguments for the Control object.

        Returns:
            Configured Control object for ASP solving.
        """
        control = Control(["--conf=trendy", "--stats", "--opt-strat=usc"] + list(args))
        for f in self.domain:
            control.load(f)
        control.load(aspf("supportConsistency.lp"))
        control.load(aspf("normalize.lp"))
        control.add("base", [], self.data)
        print("I am in default_control")
        return control

    def sample(self, first: bool, scripts: Sequence[str] = (), weight: int | None = None) -> ASPSample | None:
        """
        Generate a sample solution for the ASP problem.

        Args:
            first: If True, use weight minimization.
            scripts: Additional script files to load.
            weight: Specific weight to use.

        Returns:
            A sample solution or None if no solution found.
        """
        control = self.default_control()
        if weight is not None:
            control.load(aspf("tolerance.lp"))
            control.add(
                "base",
                [],
                f"#const minWeight={weight}. [override] #const maxWeight={weight}. [override]",
            )

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
        print("I am in sample")

        return None

    def solution_samples(self) -> Iterator[ASPSample]:
        """
        An iterator for solution samples.

        Yields:
            Solution samples for the ASP problem.
        """
        i = 1
        print("# I am in solution_samples")
        if self.debug:
            dbg(f"# model {i}")
        s = self.sample(True)
        if s is None:
            return
        yield s

        weight = s.optimization[0]
        fd, excludelp = tempfile.mkstemp(".lp")
        os.close(fd)

        with open(excludelp, "w", encoding="utf-8") as f:
            f.write(f"{s.asp_exclusion()}\n")

        args = [excludelp]
        while True:
            s = self.sample(False, args, weight=weight)
            if s:
                i += 1
                if self.debug:
                    dbg(f"# model {i}")
                yield s
                with open(excludelp, "a", encoding="utf-8") as f:
                    f.write(f"{s.asp_exclusion()}")
            else:
                print("# Enumeration complete")
                break
        os.unlink(excludelp)

    def solutions(
        self,
        on_model: Callable[[Model], bool | None],
        on_model_weight: Callable[[ASPSample], None] | None = None,
        limit: int = 0,
        force_weight: int | None = None,
    ) -> None:
        """
        Find solutions for the ASP problem.

        Args:
            on_model: Callback for each model found.
            on_model_weight: Callback for weight-based models.
            limit: Maximum number of models to find.
            force_weight: Force a specific weight for solutions.
        """
        control = self.default_control("0")

        do_mincard = self.opts.family == "mincard" or self.opts.force_size is not None
        do_subsets = self.opts.family == "subset" or (self.opts.family == "mincard" and self.opts.mincard_tolerance)
        # FIXME: The code involving minsize seems broken. Without the statement
        # below, minsize would be unbound in some cases. It only gets set for
        # very specific options.
        minsize = 0

        control.load(aspf("minimizeWeightOnly.lp"))
        if do_mincard:
            control.load(aspf("minimizeSizeOnly.lp"))

        control.ground([("base", [])])

        start = time.time()

        if force_weight is None:
            dbg("# start initial solving")
            opt = []
            control.solve(on_model=lambda model: opt.append(model.cost))
            dbg(f"# initial solve took {time.time() - start}")

            optimizations = opt.pop()
            dbg(f"# optimizations = {optimizations}")

            weight = optimizations[0]
            if do_mincard:
                minsize = optimizations[1]
            if weight > 0 and on_model_weight is not None:
                for sample in self.solution_samples():
                    on_model_weight(sample)
                return
        else:
            weight = force_weight
            dbg(f"# force weight = {weight}")

        # NOTE: maybe not set a lower bound for the weight
        # TODO: can be added to the encoding with a parametrized program
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

        solve_opts = control.configuration.solve
        solver_opts = control.configuration.solver
        assert isinstance(solve_opts, Configuration)
        assert isinstance(solver_opts, Configuration)

        solve_opts.opt_mode = "ignore"
        solve_opts.models = limit
        if do_subsets:
            # this configures the heuristic to make shown atoms false 
            # before assigning any other atoms
            solver_opts.heuristic = "Domain"
            solver_opts.dom_mod = "5,16"
            # subset minimize on: dnf, clause, formula
            solve_opts.enum_mode = "domRec"
        else:
            # project on shown atoms: dnf, clause, formula
            solve_opts.project = 1

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

        start = time.time()
        dbg("# begin enumeration")
        control.solve(on_model=on_model)
        dbg(f"# enumeration took {time.time() - start}")
        print("I am in solutions")
#---------------------------------------
