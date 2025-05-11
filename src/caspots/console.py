from __future__ import print_function

import os
import sys
import tempfile
import time
from argparse import ArgumentParser
from dataclasses import dataclass
from typing import Literal, Optional

from caspo.core import Graph, HyperGraph, LogicalNetwork, LogicalNetworkList
from clingo.solving import Model

from caspots import identify, modelchecking

from .asputils import *
from .crossvar import globalvariables
from .dataset import *
from .networks import *
from .utils import *


@dataclass
class ValidateArgs:
    pkn: str
    dataset: str
    networks: str
    range_from: int = 0
    range_length: int = 0
    output: Optional[str] = None
    tee: Optional[str] = None
    semantics: str = "u_general"
    factor: int = 100


@dataclass
class PKN2LPArgs:
    pkn: str
    output: str


@dataclass
class MIDAS2LPArgs:
    pkn: str
    dataset: str
    output: str
    factor: int = 100


@dataclass
class Results2LPArgs:
    pkn: str
    dataset: str
    networks: str
    range_from: int = 0
    range_length: int = 0


# TODO: the argument should be path
def read_pkn(args):
    if not args.pkn.endswith(".sif"):
        raise ValueError(f"sif file expected but got {args.pkn}")
    graph = Graph.read_sif(args.pkn)
    hypergraph = HyperGraph.from_graph(graph)
    print("I am in read_pkn")
    return graph, hypergraph


# TODO: the argument should be path
def dataset_name(args):
    print("I am in dataset_name")
    return os.path.basename(args.dataset).replace(".csv", "")


# TODO: the argument should be path, factor, graph
def read_dataset(args, graph):
    if not args.dataset.endswith(".csv"):
        raise ValueError(f"csv file expected but got {args.dataset}")
    ds = Dataset(dataset_name(args), dfactor=getattr(args, "factor", 100))
    ds.load_from_midas(args.dataset, graph)
    print("I am in read_dataset")
    return ds


def read_networks(args):
    networks = LogicalNetworkList.from_csv(args.networks)
    if args.range_from:
        end = len(networks)
        if args.range_length:
            end = args.range_from + args.range_length
        indexes = range(args.range_from, end)
        networks = networks[indexes]
        print("I am in read_networks")

    return networks


def read_domain(args, hypergraph, dataset, outf):
    if args.networks:
        networks = read_networks(args)
        out = domain_of_networks(networks, hypergraph, dataset)
        with open(outf, "w") as fd:
            fd.write(out)
        return outf
    else:
        return None


def is_true_positive(args, dataset, network):
    fd, smvfile = tempfile.mkstemp(".smv")
    os.close(fd)
    exact = modelchecking.verify(dataset, network, smvfile, args.semantics)
    if getattr(args, "debug", False):
        dbg("# %s" % smvfile)
    else:
        os.unlink(smvfile)
    print("I am in is true_positive")

    return exact


def do_pkn2lp(args):
    funset(read_pkn(args)[1]).to_file(args.output)


def do_midas2lp(args):
    print("I am in midas2lp")

    graph, _ = read_pkn(args)
    dataset = read_dataset(args, graph)
    funset(dataset).to_file(args.output)


def do_results2lp(args):
    print("I am in results2lp")

    graph, hypergraph = read_pkn(args)
    dataset = read_dataset(args, graph)
    networks = read_networks(args)
    out = domain_of_networks(networks, hypergraph, dataset)
    print(out)


def do_mse(args):
    print("I am in do_mse")
    graph, hypergraph = read_pkn(args)
    dataset = read_dataset(args, graph)

    termset = funset(hypergraph, dataset)

    fd, domainlp = tempfile.mkstemp(".lp")
    os.close(fd)
    domain = read_domain(args, hypergraph, dataset, domainlp)

    identifier = identify.ASPSolver(termset, args, domain=domain)

    first = True
    exact = False
    for sample in identifier.solution_samples():
        (mse0, mse) = sample.mse()
        if first:
            print("MSE_discrete = %s" % mse0)
            print("MSE_sample >= %s" % mse)
        if args.check_exact:
            network = sample.network(hypergraph)
            trace = sample.trace(dataset)
            exact = is_true_positive(args, trace, network)
            if exact:
                break
        else:
            break
        first = False
    if args.check_exact:
        if exact:
            print("MSE_sample is exact")
        else:
            print("MSE_sample may be under-estimated (no True Positive found)")
    os.unlink(domainlp)


def do_identify(args: identify.SolverOptions):
    print("I am in do_identify")

    graph, hypergraph = read_pkn(args)
    dataset = read_dataset(args, graph)
    termset = funset(hypergraph, dataset)

    fd, domainlp = tempfile.mkstemp(".lp")
    os.close(fd)
    domain = read_domain(args, hypergraph, dataset, domainlp)

    identifier = identify.ASPSolver(termset, args, domain=domain)

    networks = LogicalNetworkList.from_hypergraph(hypergraph)

    c = {
        "found": 0,
        "tp": 0,
    }

    def show_stats(output=sys.stderr):
        if args.true_positives:
            output.write("%d solution(s) / %d true positives\r" % (c["found"], c["tp"]))
        else:
            output.write("%d solution(s)\r" % c["found"])
        output.flush()

    def on_model(model: Model):
        c["found"] += 1
        skip = False
        tuples = []
        for f in model.symbols(atoms=True):
            if f.name == "dnf" and len(f.arguments) == 2:
                tuples.append([arg.number for arg in f.arguments])
        network = LogicalNetwork.from_hypertuples(hypergraph, tuples)
        if args.true_positives:
            if is_true_positive(args, dataset, network):
                c["tp"] += 1
            else:
                skip = True
        show_stats()
        if skip:
            return
        networks.append(network)

    try:
        identifier.solutions(on_model, limit=args.limit, force_weight=args.force_weight)
    finally:
        print("%d solution(s) for the over-approximation" % c["found"])
        if args.true_positives and c["found"]:
            print("%d/%d true positives [rate: %0.2f%%]" % (c["tp"], c["found"], (100.0 * c["tp"]) / c["found"]))
        if networks:
            networks.to_csv(args.output)
        os.unlink(domainlp)


def do_diversify(args):
    graph, hypergraph = read_pkn(args)
    dataset = read_dataset(args, graph)
    termset = funset(hypergraph, dataset)

    fd, domainlp = tempfile.mkstemp(".lp")
    os.close(fd)
    domain = read_domain(args, hypergraph, dataset, domainlp)

    identifier = identify.ASPSolver(termset, args, domain=domain)

    networks = LogicalNetworkList.from_hypergraph(hypergraph)

    c = {
        "found": 0,
        "tp": 0,
    }

    def show_stats(output=sys.stderr):
        if args.true_positives:
            output.write("%d solution(s) / %d true positives\r" % (c["found"], c["tp"]))
        else:
            output.write("%d solution(s)\r" % c["found"])
        output.flush()

    def on_model(model: Model):
        globalvariables.numberofsol = args.limit
        globalvariables.check = False
        c["found"] += 1
        mcounter = 1
        skip = False
        tuples = []
        tuples = (
            [x.number for x in f.arguments]
            for f in model.symbols(atoms=True)
            if f.name == "dnf" and len(f.arguments) == 2
        )
        network = LogicalNetwork.from_hypertuples(hypergraph, tuples)
        if args.true_positives:
            if is_true_positive(args, dataset, network):
                globalvariables.check = True
                c["tp"] += 1
            else:
                skip = True
        show_stats()
        if skip:
            return
        networks.append(network)

    try:
        identifier.solutions(on_model, limit=args.limit, force_weight=args.force_weight)
    finally:
        print("%d solution(s) for the over-approximation" % c["found"])
        if args.true_positives and c["found"]:
            print("%d/%d true positives [rate: %0.2f%%]" % (c["tp"], c["found"], (100.0 * c["tp"]) / c["found"]))
        if networks:
            networks.to_csv(args.output)
        os.unlink(domainlp)


def do_validate(args):
    print("I am in do_validate")
    print(args)
    graph, hypergraph = read_pkn(args)
    dataset = read_dataset(args, graph)
    networks = read_networks(args)

    TPtime = time.time()
    tp = 0
    c = 0
    nb = len(networks)
    tp_indexes = []
    firstTPtime = 0
    try:
        for network in networks:
            c += 1
            sys.stderr.write("%d/%d... " % (c, nb))
            sys.stderr.flush()
            if is_true_positive(args, dataset, network):
                tp_indexes.append(c - 1)
                tp += 1
                if tp == 1:
                    firstTPtime = time.time() - TPtime
                    print("First true positive found after %0.2f seconds" % firstTPtime)
            sys.stderr.write("%d/%d true positives\r" % (tp, c))
        res = "%d/%d true positives [rate: %0.2f%%]" % (tp, nb, (100.0 * tp) / nb)
        print(res, firstTPtime)
        if args.tee:
            with open(args.tee, "w") as f:
                f.write("%s\n" % res)
                print("Results written to %s\n" % res)
    finally:
        if args.output and tp_indexes:
            networks[tp_indexes].to_csv(args.output)


def run():
    parser = ArgumentParser(prog=sys.argv[0])
    subparsers = parser.add_subparsers(dest="command", required=True)

    # identify
    p_identify = subparsers.add_parser("identify", help="Identify Boolean networks")
    p_identify.add_argument("pkn")
    p_identify.add_argument("dataset")
    p_identify.add_argument("output")
    p_identify.add_argument("--family", choices=["all", "subset", "mincard"], default="subset")
    p_identify.add_argument("--mincard-tolerance", type=int, default=0)
    p_identify.add_argument("--weight-tolerance", type=int, default=0)
    p_identify.add_argument("--enum-traces", action="store_true", default=False)
    p_identify.add_argument("--fully-controllable", action="store_true", default=True)
    p_identify.add_argument("--force-weight", type=int, default=None)
    p_identify.add_argument("--force-size", type=int, default=None)
    p_identify.add_argument("--debug", action="store_true", default=False)
    p_identify.add_argument("--RC", type=int, default=None)
    p_identify.add_argument("--true-positives", action="store_true", default=False)
    p_identify.add_argument("--limit", type=int, default=0)
    p_identify.add_argument("--semantics", default="u_general")
    p_identify.add_argument("--range-from", type=int, default=0)
    p_identify.add_argument("--range-length", type=int, default=0)
    p_identify.add_argument("--networks", default=None)
    p_identify.add_argument("--factor", type=int, default=100)

    # diversify
    p_diversify = subparsers.add_parser("diversify", help="Diversify Boolean networks")
    p_diversify.add_argument("pkn")
    p_diversify.add_argument("dataset")
    p_diversify.add_argument("output")
    p_diversify.add_argument("--diversify", type=int, default=0)
    p_diversify.add_argument("--true-positives", action="store_true", default=False)
    p_diversify.add_argument("--limit", type=int, default=0)
    p_diversify.add_argument("--semantics", default="u_general")
    p_diversify.add_argument("--range-from", type=int, default=0)
    p_diversify.add_argument("--range-length", type=int, default=0)
    p_diversify.add_argument("--networks", default=None)
    p_diversify.add_argument("--factor", type=int, default=100)

    # validate
    p_validate = subparsers.add_parser("validate", help="Validate networks")
    p_validate.add_argument("pkn")
    p_validate.add_argument("dataset")
    p_validate.add_argument("networks")
    p_validate.add_argument("--range-from", type=int, default=0)
    p_validate.add_argument("--range-length", type=int, default=0)
    p_validate.add_argument("--output", default=None)
    p_validate.add_argument("--tee", default=None)
    p_validate.add_argument("--semantics", default="u_general")
    p_validate.add_argument("--factor", type=int, default=100)

    # mse - only pkn and dataset are positional; networks is required
    p_mse = subparsers.add_parser("mse", help="Compute MSE")
    p_mse.add_argument("pkn")
    p_mse.add_argument("dataset")
    p_mse.add_argument("--networks", required=True, help="Networks file (.csv format)")
    p_mse.add_argument("--family", choices=["all", "subset", "mincard"], default="subset")
    p_mse.add_argument("--mincard-tolerance", type=int, default=0)
    p_mse.add_argument("--weight-tolerance", type=int, default=0)
    p_mse.add_argument("--enum-traces", action="store_true", default=False)
    p_mse.add_argument("--fully-controllable", action="store_true", default=True)
    p_mse.add_argument("--force-weight", type=int, default=None)
    p_mse.add_argument("--force-size", type=int, default=None)
    p_mse.add_argument("--debug", action="store_true", default=False)
    p_mse.add_argument("--RC", type=int, default=None)
    p_mse.add_argument("--check-exact", action="store_true", default=False)
    p_mse.add_argument("--semantics", default="u_general")
    p_mse.add_argument("--range-from", type=int, default=0)
    p_mse.add_argument("--range-length", type=int, default=0)
    p_mse.add_argument("--factor", type=int, default=100)

    # pkn2lp
    p_pkn2lp = subparsers.add_parser("pkn2lp", help="Export PKN to ASP")
    p_pkn2lp.add_argument("pkn")
    p_pkn2lp.add_argument("output")

    # midas2lp
    p_midas2lp = subparsers.add_parser("midas2lp", help="Export dataset to ASP")
    p_midas2lp.add_argument("pkn")
    p_midas2lp.add_argument("dataset")
    p_midas2lp.add_argument("output")
    p_midas2lp.add_argument("--factor", type=int, default=100)

    # results2lp
    p_results2lp = subparsers.add_parser("results2lp", help="Export results to ASP")
    p_results2lp.add_argument("pkn")
    p_results2lp.add_argument("dataset")
    p_results2lp.add_argument("networks")
    p_results2lp.add_argument("--range-from", type=int, default=0)
    p_results2lp.add_argument("--range-length", type=int, default=0)

    ns = parser.parse_args()

    def from_namespace(cls, ns):
        # Get dataclass field names
        field_names = cls.__dataclass_fields__.keys()
        # Build args dict from ns if attribute exists
        args = {name: getattr(ns, name) for name in field_names if hasattr(ns, name)}
        return cls(**args)

    dispatch = {
        "identify": (do_identify, identify.SolverOptions),
        "diversify": (do_diversify, identify.SolverOptions),
        "validate": (do_validate, ValidateArgs),
        "mse": (do_mse, identify.SolverOptions),
        "pkn2lp": (do_pkn2lp, PKN2LPArgs),
        "midas2lp": (do_midas2lp, MIDAS2LPArgs),
        "results2lp": (do_results2lp, Results2LPArgs),
    }

    if ns.command not in dispatch:
        parser.error("Unknown command")
    do_command, args_cls = dispatch[ns.command]
    do_command(from_namespace(args_cls, ns))


if __name__ == "__main__":
    run()
