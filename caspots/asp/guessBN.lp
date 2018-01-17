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

