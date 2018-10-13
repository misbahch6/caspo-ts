
% Generate Set of States

states(E,T,L,V) :- measured(E,T,L,V), nextTP(E,T,_).
convert(-1,0).
convert(1,1).
states(E,T,L,V2) :- clamped(E,L,V1), convert(V1,V2), nextTP(E,T,_).

% Generate Reachable Values 1 or 0

reach(E,T,clause,X,1) :- states(E,T,L,C) : clause(X,L,V), convert(V,C); timepoint(E,T), clause(X).
reach(E,T,clause,X,0) :- states(E,T,L,0), clause(X,L,1).
reach(E,T,clause,X,0) :- states(E,T,L,1), clause(X,L,-1).
dnf(D) :- dnf(D,_).
reach(E,T,dnf,X,1) :- reach(E,T,clause,C,1), dnf(X,C).
reach(E,T,dnf,X,0) :- reach(E,T,clause,C,0) : dnf(X,C); dnf(X), nextTP(E,T,_).

opposite(1,0).
opposite(0,1).

clamped(E,S) :- clamped(E,S,V).

% Check Reachability
reach(E,T,L,X) :- formula(L,D), reach(E,T,dnf,D,X), not clamped(E,L), opposite(X,Y), not measured(E,T2,L,Y), nextTP(E,T,T2).

states(E,T,L,X) :- reach(E,T,L,X).
:- measured(E,T2,S,V), not states(E,T1,S,V), nextTP(E,T1,T2).
