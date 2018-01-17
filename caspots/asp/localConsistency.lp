
supp(E,T,L,V) :- guessed(E,T,L,V), nextTP(E,T,_).
convert(-1,0).
convert(1,1).
supp(E,T,L,V2) :- clamped(E,L,V1), convert(V1,V2), nextTP(E,T,_).

ex_supp(E,T,clause,X,1) :- supp(E,T,L,C) : clause(X,L,V), convert(V,C); timepoint(E,T), clause(X).
ex_supp(E,T,clause,X,0) :- supp(E,T,L,0), clause(X,L,1).
ex_supp(E,T,clause,X,0) :- supp(E,T,L,1), clause(X,L,-1).

dnf(D) :- dnf(D,_).
ex_supp(E,T,dnf,X,1) :- ex_supp(E,T,clause,C,1), dnf(X,C).
ex_supp(E,T,dnf,X,0) :- ex_supp(E,T,clause,C,0) : dnf(X,C); dnf(X), nextTP(E,T,_).

clamped(E,S) :- clamped(E,S,V).

ex_supp(E,T,L,X) :- formula(L,D), ex_supp(E,T,dnf,D,X), not clamped(E,L).



supp(E,T,L,X) :- ex_supp(E,T,L,X).

:- guessed(E,T2,S,V), not supp(E,T1,S,V), nextTP(E,T1,T2).


