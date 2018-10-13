%-----------include the current state guessed or clamped in meta stat supp in the first two lines
supp(E,T,L,V) :- guessed(E,T,L,V), nextTP(E,T,_).
convert(-1,0).
convert(1,1).
supp(E,T,L,V2) :- clamped(E,L,V1), convert(V1,V2), nextTP(E,T,_).

%---------------derive all values that we can potentially reach by a transition from the state supp
ex_supp(E,T,clause,X,1) :- supp(E,T,L,C) : clause(X,L,V), convert(V,C); timepoint(E,T), clause(X).
ex_supp(E,T,clause,X,0) :- supp(E,T,L,0), clause(X,L,1).
ex_supp(E,T,clause,X,0) :- supp(E,T,L,1), clause(X,L,-1).
dnf(D) :- dnf(D,_).
ex_supp(E,T,dnf,X,1) :- ex_supp(E,T,clause,C,1), dnf(X,C).
ex_supp(E,T,dnf,X,0) :- ex_supp(E,T,clause,C,0) : dnf(X,C); dnf(X), nextTP(E,T,_).

%------------------Question: Here you calculate all the values we can reach from the current state right ? So here it generate the set {0,1} or {0,1,{0,1}}?
% it generated {0,1}
opposite(1,0).
opposite(0,1).

clamped(E,S) :- clamped(E,S,V).

% --------------- enumerate to make a transition or not
%if we do not have guessed the opposing thing, we can have external support

ex_supp(E,T,L,X) :- formula(L,D), ex_supp(E,T,dnf,D,X), not clamped(E,L), opposite(X,Y), not guessed(E,T2,L,Y), nextTP(E,T,T2).
%ex_supp(E,T,L,X) :- formula(L,D), ex_supp(E,T,dnf,D,X), not clamped(E,L), opposite(X,Y), not measured(E,T,L,Y), T <= T', last(_,T').

% if we guessed the opposing thing, the opposing thing needs to be justified before we can give support

{ex_supp(E,T,L,X)} :- formula(L,D), ex_supp(E,T,dnf,D,X), not clamped(E,L), opposite(X,Y), guessed(E,T2,L,Y), nextTP(E,T,T2).

%------Question: Why we have justify if we guess opposite thing ? we should not be able to reach the state if the opposite value is guessed. I don't understand the purpose of this rule. Can you please elaborate it little bit here. 

%---cannot have both values at the same time
%:- ex_supp(E,T,L,1), ex_supp(E,T,L,0).

%------------------if yes, add it to our meta state supp
%supp(E,T,L,X) :- ex_supp(E,T,L,X).

%------------------ensures that the next state belongs to the meta-state supp
:- guessed(E,T2,S,V), not supp(E,T1,S,V), nextTP(E,T1,T2).

%-------------------checks the second condition, that if for some i, x_i = y_i and {0, 1} = u_i then there exists a transition f_i(z) = y_i
:- guessed(E,T2,L,Y), opposite(X,Y), ex_supp(E,T1,L,X), not ex_supp(E,T1,L,Y), nextTP(E,T1,T2).




