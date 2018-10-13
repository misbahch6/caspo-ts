:- formula("ap1",0), formula("map3k1",1), formula("erk",12), formula("creb",9), formula("pi3k",2), formula("gsk3",3), formula("nfkb",4), formula("sos",5), formula("ikb",6), formula("raf1",10), formula("p38",7), dnf(6,13), dnf(6,12), dnf(5,11), dnf(7,15), dnf(4,8), dnf(0,0), dnf(12,20), dnf(1,3), dnf(10,19), dnf(2,5), dnf(3,7), clause(3,"pi3k",1), clause(5,"egf",1), clause(20,"raf1",1), clause(19,"sos",1), clause(15,"map3k1",1), clause(3,"sos",1), clause(7,"pi3k",-1), clause(0,"map3k1",1), clause(8,"ikb",-1), clause(11,"egf",1), clause(11,"erk",-1), clause(12,"nfkb",1), clause(13,"tnfa",-1).

-----------4 Solution---------- 
map3k1 <- sos;
pi3k <- (tnfa & egf);
gsk3 <- !pi3k;
ap1 <- map3k1;
p38 <- (tnfa & map3k1);
ikb <- nfkb | !tnfa;
sos <- (egf & !erk);
nfkb <- !ikb;
raf1 <- sos;
erk <- raf1;
-----------5 Solution----------
map3k1 <- sos;
pi3k <- tnfa;
gsk3 <- !pi3k;
ap1 <- map3k1;
p38 <- (tnfa & map3k1);
ikb <- nfkb | !tnfa;
sos <- (egf & !erk);
nfkb <- !ikb;
raf1 <- sos;
erk <- raf1;
-----------6 Solution----------
map3k1 <- sos;
pi3k <- egf;
gsk3 <- !pi3k;
ap1 <- map3k1;
p38 <- (tnfa & map3k1);
ikb <- nfkb | !tnfa;
sos <- (egf & !erk);
nfkb <- !ikb;
raf1 <- sos;
erk <- raf1;



	
	FO = ":-"
	if args.RC:
	    mcounter = True
	    if len(networks) == 5:
		forcommaordot = len(model.atoms())
		print(len(networks))
		count=0
		print("coucouuuuuu")
		print(forcommaordot)
	    	for item in model.atoms():
		    FO = FO +" "+ str(item)
		    count = count+1
		    if count < forcommaordot:
			FO = FO + ","
	    	    else:
			FO = FO + "."
		f=open("/home/user/Downloads/caspots-master/caspots/asp/guessBN.lp","a+")
		f.write(FO)
		f.close()		
		print(FO)
		mcounter = False
		#control = gringo.Control([ "--stats", "--opt-strat=usc"] + list(args))
		identifier.justtry(FO)
		#identifier.filterouts(on_model,FO, limit=args.limit, force_weight=args.force_weight)
	#Misbah

#Misbah --- Solving at Execution time ---

    def filterouts(self, on_model,FO, limit = 0,force_weight=None):
        start = time.time()
	control = self.default_control("0")

	control.add("RC", [],FO) ####
	control.ground([("base", [])]) ####

        start = time.time()

        if force_weight is None:
            control.assign_external(gringo.Fun("tolerance"),False)
            dbg("# start initial solving")
            opt = []
            res = control.solve(None, lambda model: opt.append(model.optimization()))
	    
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

            control.assign_external(gringo.Fun("tolerance"),True)
        else:
            weight = force_weight
            dbg("# force weight = %d" % weight)

        max_weight = weight + self.opts.weight_tolerance
        control.add("minWeight", [], ":- not " + str(weight) + " #sum {Erg,E,T,S : measured(E,T,S,V), not guessed(E,T,S,V), toGuess(E,T,S), obs(E,T,S,M), Erg=50-M, M < 50;" + " Erg,E,T,S : measured(E,T,S,V), not guessed(E,T,S,V), toGuess(E,T,S), obs(E,T,S,M), Erg=M-49, M >= 50} " + str(max_weight) + " .")
        control.ground([("minWeight", [])])

        control.conf.solve.opt_mode = "ignore"
        control.conf.solve.project = 1 # ????
        control.conf.solve.models = limit # ????
        #print control.conf.solver[0].keys()

        if do_mincard:
            if self.opts.force_size:
                maxsize = self.opts.force_size
            else:
                maxsize = minsize + self.opts.mincard_tolerance
            control.add("minSize", [], ":- not " + str(minsize) + " #sum {L,I,J : dnf(I,J) , hyper(I,J,L)} " + str(maxsize) + ".")
            control.ground([("minSize", [])])

        if do_subsets:
            control.conf.solve.enum_mode = "domRec"
            control.conf.solver[0].heuristic = "Domain"
            control.conf.solver[0].dom_mod = "5,16"

        start = time.time()
        dbg("# begin enumeration")
        res = control.solve(None, on_model)
        dbg("# enumeration took %s" % (time.time()-start))
	#Misbah --- Solving at Execution time ---
