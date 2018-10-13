% guess a formula compatible with the pkn for each node
formula(V,I)              :- node(V,I); hyper(I,_,_).
{dnf(I,J) : hyper(I,J,N)} :- formula(V,I).
clause(J,V,S)             :- edge(J,V,S); dnf(_,J).

% paths derived from the guess Boolean network 
path(U,V) :- formula(V,I); dnf(I,J); edge(J,U,_).
path(U,V) :- path(U,W); path(W,V).

% J2 subsumed by J1
:- formula(V,I); hyper(I,J1,N); hyper(I,J2,M); N < M,
   dnf(I,J1);  dnf(I,J2); clause(J2,U,S) : clause(J1,U,S).

% contradictions
:- formula(V,I); dnf(I,J); edge(J,U,S); edge(J,U,-S).

% V is not leading to any readout (non-observable)
:- path(_,V); not readout(V); not path(V,U) : readout(U).


% clampings from each experimental condition
%clamped(E,V) :- clamped(E,V,_).
%free(E,V,I)  :- formula(V,I); dnf(I,_); exp(E); not clamped(E,V).

% Signal propagation according to Boolean logic
%eval_clause(E,J,-1) :- clause(J,V,S); eval(E,V,-S).

%eval(E,V, S) :- clamped(E,V,S).
%eval(E,V, 1) :- free(E,V,I); eval(E,W,T) : clause(J,W,T); dnf(I,J).
%eval(E,V,-1) :- free(E,V,I); eval_clause(E,J,-1) : dnf(I,J).

%rss(D,V,1,(F-D)**2) :- obs(E,V,D); dfactor(F).
%rss(D,V,-1,D**2)  :- obs(E,V,D).

%this is the correct one, use this


#const maxsize = -1.
#const maxrss = -1.

:- maxsize + 1 #sum {L,I,J : dnf(I,J) , hyper(I,J,L) }; maxsize >= 0.
%:- maxrss + 1 #sum {W,E,V,S : not eval(E,V,-S) , obs(E,V,D) , rss(D,V,S,W) }; maxrss >= 0.

%:- formula("sos",8), formula("traf2",0), formula("map3k1",1), formula("ikb",7), formula("ap1",10), formula("pi3k",2), formula("gsk3",3), formula("raf1",11), formula("nfkb",4), formula("egfr",5), formula("erk",13), formula("p38",6), dnf(8,20), dnf(10,23), dnf(11,24), dnf(5,12), dnf(4,10), dnf(13,25), dnf(0,0), dnf(1,3), dnf(5,11), dnf(7,17), clause(20,"egfr",1), clause(17,"traf2",-1), clause(24,"sos",1), clause(3,"raf1",1), clause(23,"map3k1",1), clause(0,"map3k1",-1), clause(25,"raf1",1), clause(10,"ikb",-1), clause(11,"map3k1",-1), clause(12,"egf",1).

