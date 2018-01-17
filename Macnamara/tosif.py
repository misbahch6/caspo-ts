import sys

from zope import component

from pyzcasp import potassco, asp
from caspo import core, visualize

reader = component.getUtility(core.ICsvReader)

reader.read(sys.argv[1])
networks = core.ILogicalNetworkSet(reader)

dataset = None
if len(sys.argv) > 2:
    reader.read(sys.argv[2])
    dataset = core.IDataset(reader)

for i,network in enumerate(networks):
    
    if dataset:
        writer = component.getMultiAdapter((visualize.IMultiDiGraph(network), dataset.setup), visualize.IDotWriter)
        writer.write('network-%s.dot' % i)
    
    gate_n = 1
    with open('network-%s.sif' % i,'w') as f:
        for target, formula in network.mapping.iteritems():
            for clause in formula:
                if len(clause) > 1:
                    gate = 'and%s' % gate_n
                    gate_n += 1
                    
                    f.write("%s\t%s\t%s\n" % (gate, 1, target))
            
                    for var,sign in clause:
                        f.write("%s\t%s\t%s\n" % (var, sign, gate))
                else:
                    var, sign = list(clause)[0]
                    f.write("%s\t%s\t%s\n" % (var, sign, target))
