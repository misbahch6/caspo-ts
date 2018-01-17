# !/usr/bin/python
#call it python testscript.py ../../Benchmarks/nets_to_test/*/asp/

from __future__ import print_function
import os
import sys
import gringo 
import shutil
import time


arguments = []
optimizations = 0
counter = 0
results_app = "results/"
encoding_app = "Consistency.lp"
f = 0

def print_conf(conf, ident):
    for x in conf.keys():
        key = x.split(".")
        if len(key) > 1:
            subconf = getattr(conf, key[0])
            label   = key[0]
            if (len(subconf) >= 0):
                label += "[0.." + str(len(subconf)) + "]"
            print ("{0}{1} - {2}".format(ident, label, getattr(conf, "__desc_" + key[0])))
            print_conf(subconf, ident + "  ")
        else:
            print ("{0}{1}[={2}] - {3}".format(ident, key[0], getattr(conf, key[0]), getattr(conf, "__desc_" + key[0])))

def on_model(m):
        global counter
	global f
	counter = counter + 1
        f.write("Answer:" + str(counter) + "\n")
        f.write(" ".join(map(str, m.atoms(gringo.Model.SHOWN))) + "\n")
#        print "  positive:", ", ".join(map(str, m.atoms(gringo.Model.SHOWN)))
#        print "  negative:", ", ".join(map(str, m.atoms(gringo.Model.SHOWN | gringo.Model.COMP)))
#        print "csp"
#        print "  positive:", ", ".join(map(str, m.atoms(gringo.Model.CSP)))
#        print "  negative:", ", ".join(map(str, m.atoms(gringo.Model.CSP | gringo.Model.COMP)))
#        print "atoms"
#        print "  positive:", ", ".join(map(str, m.atoms(gringo.Model.ATOMS)))
#        print "  negative:", ", ".join(map(str, m.atoms(gringo.Model.ATOMS | gringo.Model.COMP)))
#        print "terms"
#        print "  positive:", ", ".join(map(str, m.atoms(gringo.Model.TERMS)))
#        print "  negative:", ", ".join(map(str, m.atoms(gringo.Model.TERMS | gringo.Model.COMP)))

def on_model_opt(model):
    global optimizations
    optimizations = model.optimization()
#    print optimizations

if __name__ == '__main__':
#    global counter
    #for file in files:
    #    solver.load(file)
    #    solver.ground([("base", [])])
    #    future = solver.solve(None,on_model) 

    for mode in ["local", "support"]:
        print(mode)
        encoding = mode + encoding_app
	results = mode + results_app
#	print "starting encoding " + encoding + " into folder " + results
        for arg in sys.argv:
            datasets = []
            pkn = ""
            path = ""
            for root, dirs, files in os.walk(arg, topdown=False):
                path = root
                for name in files:
                    if name.find("dataset") != -1 and name.find("cmpr") != -1 and name.find(".lp")==len(name)-3:
                        #print("dataset")
                        datasets.append(name)
                        #print(os.path.join(root, name))
                    if name.find("pkn") != -1 and name.find(".lp")==len(name)-3:
                        #print("pkn")
                        pkn = name
                        #print(os.path.join(root, name))
    		
#            print("new try") 
#            if (pkn!=""):
#                print(path)
#                print(pkn)
    	    directory = os.path.join(path,results)
    	    #print(directory, end='')
    	    #shutil.rmtree(directory, ignore_errors=True)
            try:
                #for the_file in os.listdir(directory):
                #    file_path = os.path.join(directory, the_file)
                #    if os.path.isfile(file_path):
                #        os.unlink(file_path)
	        os.makedirs(directory)
            except Exception, e:
	        pass
                #print(e)
            for i in datasets:
                print(i, end=',')
                #help(gringo)
    		control = gringo.Control(["--conf=trendy", "--stats", "0", "--opt-strat=usc"])
                #print_conf(control.conf, "")
		control.load("guessBN.lp")
		control.load(encoding)
		control.load("minimizeWeightOnly.lp")
		control.load("normalize.lp")
#		control.load("../../Benchmarks/nets_to_test/1/asp/pkn.lp")
		control.load(os.path.join(path, pkn))
		control.load(os.path.join(path, i))
		control.ground([("base", [])])

		control.load("show.lp")
		control.ground([("show", [])])
                control.assign_external(gringo.Fun("tolerance"),False)
		
		start = time.time()

		res = control.solve(None, on_model_opt)
		#print("Finding the minimal model: " + str(time.time()-start))
		print(optimizations,end=',')
		print(str(time.time()-start), end=',')

                control.assign_external(gringo.Fun("tolerance"),True)

		control.add("minWeight", [], ":- not " + str(optimizations[0]) + " #sum {Erg,E,T,S : measured(E,T,S,V), not guessed(E,T,S,V), toGuess(E,T,S), obs(E,T,S,M), Erg=50-M, M < 50;" + " Erg,E,T,S : measured(E,T,S,V), not guessed(E,T,S,V), toGuess(E,T,S), obs(E,T,S,M), Erg=M-49, M >= 50} " + str(optimizations[0]) + " .")
                control.ground([("minWeight", [])])

# enable this section to additionally compute all solution size independent
#                control.conf.solve.opt_mode = "ignore"
#                control.conf.solve.project = 1 # ????
#                control.conf.solve.models = 0 # ????
#		counter = 0
#                f = open(os.path.join(directory, i + "_all"),'w')
#		res = control.solve(None, on_model)
#		f.close()
######################################

                #control.add("minSize", [], ":- not " + str(optimizations[1]) + " #sum {L,I,J : dnf(I,J) , hyper(I,J,L)} " + str(optimizations[1]) + ".")
		#control.ground([("minSize", [])])


                control.conf.solve.opt_mode = "ignore"
                control.conf.solve.project = 1 # ????
                control.conf.solve.models = 0 # ????
		#print control.conf.solver[0].keys()
                control.conf.solve.enum_mode = "domRec"
                control.conf.solver[0].heuristic = "Domain"
                control.conf.solver[0].dom_mod = "5,16"
		# --enum-mode=domRec --heuristic=Domain --dom-mod=5,16

		start = time.time()
#		print("only optimal ones:")
		counter = 0
                f = open(os.path.join(directory, i + "_subset"),'w')
		res = control.solve(None, on_model)
		f.close()
		#print("Enumerating all models: " + str(time.time()-start))
		print(str(time.time()-start))






#    for name in dirs:
#        print(os.path.join(root, name))
