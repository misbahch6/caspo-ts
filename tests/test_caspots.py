"""
Basic tests for caspots.
"""

import math
import os
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from caspo.core import Graph, HyperGraph, LogicalNetwork, LogicalNetworkList
from clingo import Model

from caspots import identify
from caspots.asputils import funset
from caspots.console import is_true_positive, read_dataset, read_domain, read_networks, read_pkn
from caspots.identify import ASPSolver


class Args:
    pass


@dataclass
class Config:
    fully_controllable: bool = True
    debug: bool = False
    family: str = "subset"
    factor: int = 100
    pkn: str = ""
    dataset: str = ""
    output: str = ""
    networks: str = ""
    force_size: Optional[int] = None
    weight_tolerance: int = 0
    # for mse options
    enum_traces: bool = False
    # for validate
    tee: Optional[str] = None
    range_from: int = 0
    range_lenth: int = 0
    semantics: str = "general"
    diversify: bool = False


class TestCaspots:
    """
    Test cases for caspots.
    """

    def read_inputs(self):
        test_dir = Path(__file__).parent
        args = Config()
        args.pkn = str(test_dir / "resources" / "pkn.sif")
        args.dataset = str(test_dir / "resources" / "dataset.csv")
        args.networks = str(test_dir / "resources" / "results.csv")
        graph, hypergraph = read_pkn(args)
        dataset = read_dataset(args, graph)
        networks = read_networks(args)
        return graph, hypergraph, dataset, networks

    def test_dataset(self):
        """
        Test reading datasets.
        """
        graph, hypergraph, dataset, networks = self.read_inputs()
        assert len(graph.nodes) == 13
        assert len(graph.edges) == 16
        assert len(hypergraph.nodes) == 13
        assert len(hypergraph.edges) == 26
        assert len(dataset.experiments) == 10
        assert len(networks) == 54

    def test_identify(self):
        """
        Test identify command.
        """
        graph, hypergraph, dataset, networks = self.read_inputs()
        termset = funset(hypergraph, dataset)
        print(networks)

        args = Config()

        with tempfile.NamedTemporaryFile(suffix=".lp", delete=False) as tmp:
            domainlp = tmp.name

        try:
            domain = read_domain(args, hypergraph, dataset, domainlp)
            identifier = ASPSolver(termset, args, domain=domain)
            networks = LogicalNetworkList.from_hypergraph(hypergraph)
            count = 0

            def on_model(model: Model):
                nonlocal count
                count += 1
                tuples = []
                for f in model.symbols(atoms=True):
                    if f.name == "dnf" and len(f.arguments) == 2:
                        tuples.append([arg.number for arg in f.arguments])
                network = LogicalNetwork.from_hypertuples(hypergraph, tuples)
                networks.append(network)

            identifier.solutions(on_model, limit=100, force_weight=None)

            assert count == 54
            # if networks:
            #     networks.to_csv(args.output)
        finally:
            if os.path.exists(domainlp):
                os.unlink(domainlp)

    def test_mse(self):
        """
        Test MSE.
        """
        graph, hypergraph, dataset, networks = self.read_inputs()
        termset = funset(hypergraph, dataset)

        args = Config()

        with tempfile.NamedTemporaryFile(suffix=".lp", delete=False) as tmp:
            domainlp = tmp.name

        try:
            domain = read_domain(args, hypergraph, dataset, domainlp)
            identifier = identify.ASPSolver(termset, args, domain=domain)
            for sample in identifier.solution_samples():
                (mse0, mse) = sample.mse()
            assert math.isclose(mse0, 0.1551675841362064, rel_tol=1e-9)
        finally:
            # Ensure the temporary file is always deleted
            if os.path.exists(domainlp):
                os.unlink(domainlp)

    def test_validate(self):
        """
        Test validate.
        """
        graph, hypergraph, dataset, networks = self.read_inputs()
        args = Config()

        tp = 0
        for network in networks:
            if is_true_positive(args, dataset, network):
                tp += 1
        assert tp == 54
