import argparse

from zope import component

from pyzcasp import asp, potassco

def main(args):
    gringo = component.getUtility(potassco.IGringoGrounder)
    clasp = component.getUtility(potassco.IClaspSolver)
    clingo = component.getMultiAdapter((gringo, clasp), asp.IGrounderSolver)
    
    encodings = component.getUtility(asp.IEncodingRegistry).encodings(gringo)
    
    models = clingo.run(grounder_args=["-c k=2", encodings('enco-1')], solver_args=["0"])
    print [term for term in models[0]]
    print [term for term in models[1]]

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
                        
    parser.add_argument("--clasp", dest="clasp", default="clasp",
                        help="clasp solver binary (Default to 'clasp')", metavar="C")
                        
    parser.add_argument("--gringo", dest="gringo", default="gringo",
                        help="gringo grounder binary (Default to 'gringo')", metavar="G")

    parser.add_argument("--gringo-series", dest="gringo_series", type=int, default=4, choices=[3,4],
                        help="gringo series", metavar="S")

                        
    args = parser.parse_args()
    
    gsm = component.getGlobalSiteManager()

    if args.gringo_series == 3:
        potassco.configure(gringo3=args.gringo, clasp3=args.clasp)
    else:
        potassco.configure(gringo4=args.gringo, clasp3=args.clasp)
        
    gsm.registerUtility(asp.EncodingRegistry(), asp.IEncodingRegistry, 'example')

    root = __file__.rsplit('/', 1)[0]
    reg = component.getUtility(asp.IEncodingRegistry, 'example')
    reg.register('enco-1', root + '/encodings/encoding-1-gringo3.lp', potassco.IGringo3)
    reg.register('enco-1', root + '/encodings/encoding-1-gringo4.lp', potassco.IGringo4)
    
    main(args)
