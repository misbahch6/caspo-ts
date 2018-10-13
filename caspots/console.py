
from __future__ import print_function

import os
import sys
import tempfile
import time
#import gringo
import clingo

from .graph import Graph
from .hypergraph import HyperGraph
from .logicalnetwork import LogicalNetwork, LogicalNetworkList

#import logicalnetworklist as LogicalNetworkList

from .networks import *
from .utils import *
from .asputils import *
from .dataset import *
from caspots import identify
from crossvar import globalvariables
from caspots import modelchecking

def read_pkn(args):
    graph = Graph.read_sif(args.pkn)
    hypergraph = HyperGraph.from_graph(graph)
    return graph, hypergraph

def dataset_name(args):
    return os.path.basename(args.dataset).replace(".csv", "")

def read_dataset(args, graph):
    ds = Dataset(dataset_name(args), dfactor=args.factor)
    ds.load_from_midas(args.dataset, graph)
    return ds

def read_networks(args):
    networks = LogicalNetworkList.from_csv(args.networks)
    if args.range_from:
        end = len(networks)
        if args.range_length:
            end = args.range_from + args.range_length
        indexes = range(args.range_from, end)
        networks = networks[indexes]
    return networks

def read_domain(args, hypergraph, dataset, outf):
    if args.networks:
        networks = read_networks(args)
        out = domain_of_networks(networks, hypergraph, dataset)
        with open(outf, "w") as fd:
	    #print("%s\n" %out)
            fd.write(out)
        return outf
    else:
        return None

def is_true_positive(args, dataset, network):
    fd, smvfile = tempfile.mkstemp(".smv")
    os.close(fd)
    exact = modelchecking.verify(dataset, network, smvfile, args.semantics)
    #print(globalvariables.contraintonexp, "\n")
    if args.debug: #misbah
        dbg("# %s" % smvfile)
    else:
        os.unlink(smvfile)
    return exact

def do_pkn2lp(args):
    funset(read_pkn(args)[1]).to_file(args.output)

def do_midas2lp(args):
    graph, _ = read_pkn(args)
    dataset = read_dataset(args, graph)
    funset(dataset).to_file(args.output)

def do_results2lp(args):
    graph, hypergraph = read_pkn(args)
    dataset = read_dataset(args, graph)
    networks = read_networks(args)
    out = domain_of_networks(networks, hypergraph, dataset)
    print(out)

def do_mse(args):
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
	    #print("%s" % mse0)
            #if mse0 == mse:
             #   print("MSE_sample >= MSE_discrete")
            #else:
            print("MSE_sample >= %s" % mse)
            #print("%s" % mse)
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


def do_identify(args):
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


    def on_model(model):
        globalvariables.numberofsol = args.limit 
        globalvariables.check = False
	#file = open("checkmodels.txt","w")
        c["found"] += 1
	mcounter = 1
        skip = False
	#print(model.cost)
	#print(model.symbols(atoms=True))
	#for f in model.symbols(atoms=True):
	#    if f.name == "dnf" and len(f.arguments) == 2:
	#	print(f)
	#for f in model.symbols(atoms=True): 
	    #if f.name == "supp":
	        #print(f)
	#print(model.symbols(shown=True))
	#print(model, model.optimality_proven, model.cost)
        tuples = ([x.number for x in f.arguments] for f in model.symbols(shown=True) if f.name == "dnf")
        network = LogicalNetwork.from_hypertuples(hypergraph, tuples)
	#print(dir(model))	
	#print(dir(model.symbols(atoms=True)))

	#for item in network:
	    #print("%s,"%item)
        if args.true_positives:
            if is_true_positive(args, dataset, network):
                globalvariables.check = True
                c["tp"] += 1 
		'''############# -------------Misbah------------------

	    	for exp in dataset.experiments.values():
		    if exp.id == globalvariables.contraintonexp:
			dvars = dataset.setup.nodes.union(network.variables())
			varying_nodes = set([node for node, _ in network.formulas_iter()])
			clampable = varying_nodes.intersection(dataset.inhibitors.union(dataset.stimulus))
			#print(dvars)
			#print(clampable)		
		    	for t, values in exp.obs.items():
            	    	    for n, v in values.items():
				#print(n, v)
				    #print("%d, %d, %s, %s" % (exp.id, t, n, "0" if not v else "1"))
				print([(clingo.Function("supp",[exp.id,t,n,not v]), True)])
				model.context.add_nogood([(clingo.Function("supp",[globalvariables.contraintonexp,t,n, not v]), True)])
	############# ------------- Misbah--------------------'''
            else:
                skip = True
        show_stats()
        if skip:
            return
        networks.append(network)
	#print(globalvariables.contraintonexp)
	'''
        if skip and args.RC:
	    crossvar.myflag=True
	    forcommaordot = len(model.symbols(shown=True))
	    count=0
	    for item in model.symbols(shown=True):
		crossvar.FO = crossvar.FO +" "+ str(item)
		count = count+1
		if count < forcommaordot:
		    crossvar.FO = crossvar.FO + ","
	    	else:
		    crossvar.FO = crossvar.FO + "."
	    f=open("constraintssss.lp","a+")
	    f.write(crossvar.FO + "\n")
	    f.close()		
	    print(crossvar.FO)
            print(crossvar.myflag)
	    crossvar.FO=":-"
	    return


	#Misbah	

	#for item1, item2 in network.formulas_iter():
		#print(item)

	print("-----------%d Solution----------"% c["found"])
	def forliteral((var, sign)):
           return "%s%s" % ("!" if sign == -1 else "", var)

    	def clausesforand(clause):
           expr = " & ".join(map(forliteral, clause))
           if len(clause) > 1:
              return "(%s)" % expr
           return expr

    	def clauseforor(clauses):
           if len(clauses) == 0:
              return "FALSE"
           return " | ".join(map(clausesforand, clauses))

   	for n, item in network.formulas_iter():
           expr = clauseforor(item)
           #print("%s <- %s;" % (n, expr))
	#Misbah'''
    try:
        identifier.solutions(on_model, limit=args.limit, force_weight=args.force_weight)
    finally:
        print("%d solution(s) for the over-approximation" % c["found"])
        if args.true_positives and c["found"]:
            print("%d/%d true positives [rate: %0.2f%%]" \
                % (c["tp"], c["found"], (100.*c["tp"])/c["found"]))
        if networks:
            networks.to_csv(args.output)
        os.unlink(domainlp)
    

def do_validate(args):
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
            sys.stderr.write("%d/%d... " % (c,nb))
	    #print("%d/%d... " % (c,nb))
            sys.stderr.flush()
            if is_true_positive(args, dataset, network):
                tp_indexes.append(c-1)
                tp += 1
                if tp == 1:
                    firstTPtime = time.time() - TPtime
                    print(firstTPtime)
            sys.stderr.write("%d/%d true positives\r" % (tp,c))
        res = "%d/%d true positives [rate: %0.2f%%]" % (tp, nb, (100.*tp)/nb)
        print(res, firstTPtime)
        if args.tee:
            with open(args.tee, "w") as f:
                f.write("%s\n" % res)
		print("%s\n" % res)
    finally:
        if args.output and tp_indexes:
            networks[tp_indexes].to_csv(args.output)


from argparse import ArgumentParser

def run():

    parser = ArgumentParser(prog=sys.argv[0])
    parser.add_argument("--debug", action="store_true", default=False)
    parser.add_argument("--debug-dir", type=str, default=tempfile.gettempdir())
    subparsers = parser.add_subparsers(help="commands help")

    identify_parser = ArgumentParser(add_help=False)
    identify_parser.add_argument("--family", choices=["all", "subset", "mincard"],
                                    default="subset",
                                    help="result family (default: subset)")
    identify_parser.add_argument("--mincard-tolerance", type=int, default=0,
                                    help="consider (subset minimal) solutions with cardinality at most tolerance + the minimum cardinality")
    identify_parser.add_argument("--weight-tolerance", type=int, default=0,
                                    help="consider (subset minimal) solutions with weight at most tolerance + the minimum weight")
    identify_parser.add_argument("--enum-traces", action="store_true",
                                    default=False,
                                    help="enumerate over traces")
    identify_parser.add_argument("--fully-controllable", action="store_true",
                                    help="only consider BNs where all nodes have a stimulus in their ancestors (default)")
    identify_parser.add_argument("--no-fully-controllable", action="store_false", dest="fully_controllable",
                                    help="do not only consider BNs where all nodes have a stimulus in their ancestors")
    identify_parser.set_defaults(fully_controllable=True)
    identify_parser.add_argument("--force-weight", type=int, default=None,
                                    help="Force the maximum weight of a solution")
    identify_parser.add_argument("--force-size", type=int, default=None,
                                    help="Force the maximum size of a solution")
    #xor-start
    identify_parser.add_argument("--xor", type=int, default=None,
                                 help="The number of xor constraints to create")
    #identify_parser.add_argument("--q", type=int, default=2,
	#			help="The sampling factor related to the size of each constraint")
    #xor-end

    #Misbah -- Execution time Recalling Solver
    identify_parser.add_argument("--debug", action="store_true", default=False)
    identify_parser.add_argument("--RC", type=int, default=None,
                                 help="Invoke Solver Again")
    #Misbah -- Execution time Recalling Solver

    #Misbah -- Try Planning Instead of Model Checking ---
    identify_parser.add_argument("--plan", type=int, default=None,
                                 help="Invoke planning.lp to verify traces of BNs")
    #Misbah -- Try Planning Instead of Model Checking ---

    modelchecking_p = ArgumentParser(add_help=False)
    modelchecking_p.add_argument("--semantics",
        choices=modelchecking.MODES, default=modelchecking.U_GENERAL,
        help="Updating mode of the Boolean network (default: %s)" \
            % modelchecking.U_GENERAL)

    pkn_parser = ArgumentParser(add_help=False)
    pkn_parser.add_argument("pkn", help="Prior knowledge network (sif format)")
    dataset_parser = ArgumentParser(add_help=False)
    dataset_parser.add_argument("dataset", help="Dataset (midas csv format)")
    dataset_parser.add_argument("--factor", type=int, default=100,
                                    help="discretization factor (default: 100)")

    networks_parser = ArgumentParser(add_help=False)
    networks_parser.add_argument("--range-from", type=int, default=0,
        help="Validate only networks from given row (starting at 0)")
    networks_parser.add_argument("--range-length", type=int, default=0,
        help="Number of networks to validate (0 means all)")

    domain_parser = ArgumentParser(add_help=False,
        parents=[networks_parser])
    domain_parser.add_argument("--networks", help="Networks to as domain (.csv)")

    parser_pkn2lp = subparsers.add_parser("pkn2lp",
        help="Export PKN (sif format) to ASP (lp format)",
        parents=[pkn_parser])
    parser_pkn2lp.add_argument("output", help="Output file (.lp format)")
    parser_pkn2lp.set_defaults(func=do_pkn2lp)

    parser_midas2lp = subparsers.add_parser("midas2lp",
        help="Export dataset (midas csv format) to ASP (lp format)",
        parents=[pkn_parser, dataset_parser])
    parser_midas2lp.add_argument("output", help="Output file (.lp format)")
    parser_midas2lp.set_defaults(func=do_midas2lp)

    parser_results2lp = subparsers.add_parser("results2lp",
        help="Export results to ASP (lp format)",
        parents=[pkn_parser, dataset_parser, networks_parser])
    parser_results2lp.add_argument("networks", help="Networks file (.csv format)")
    parser_results2lp.set_defaults(func=do_results2lp)

    parser_mse = subparsers.add_parser("mse",
        help="Compute the best MSE",
        parents=[pkn_parser, dataset_parser, identify_parser,
                    modelchecking_p, domain_parser])
    parser_mse.add_argument("--check-exact", action="store_true", default=False,
                            help="look for a true positive with the computed MSE")
    parser_mse.set_defaults(func=do_mse)

    parser_identify = subparsers.add_parser("identify",
        help="Identify all the best Boolean networks",
        parents=[pkn_parser, dataset_parser, identify_parser,
                    modelchecking_p, domain_parser])
    parser_identify.add_argument("--true-positives", default=False, action="store_true",
        help="filter solutions to keep only true positives (exact identification)")
    parser_identify.add_argument("--limit", default=0, type=int,
        help="Limit the number of solutions")
    parser_identify.add_argument("output", help="output file (csv format)")
    parser_identify.set_defaults(func=do_identify)

    parser_validate = subparsers.add_parser("validate",
        help="Compute the true positive rate of *exactly* identified networks",
        parents=[pkn_parser, dataset_parser,
                    modelchecking_p])
    parser_validate.add_argument("--range-from", type=int, default=0,
        help="Validate only networks from given row (starting at 0)")
    parser_validate.add_argument("--range-length", type=int, default=0,
        help="Number of networks to validate (0 means all)")
    parser_validate.add_argument("--output", 
        help="output true positive network to file (csv format)")
    parser_validate.add_argument("--tee", type=str, default=None,
        help="Output result to given file (in addition to stdout).")
    parser_validate.add_argument("networks", help="network set (csv format)")
    parser_validate.set_defaults(func=do_validate)

    args = parser.parse_args()
    #print("#### OPTIONS ######")
    #for k,v in args._get_kwargs():
       # if k in ["func"]:
           # continue
       # print("# %s = %s" % (k,v))
   #print("###################")
    args.func(args)

