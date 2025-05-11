#const maxsize = -1.
#const maxrss = -1.
#const minErrors=#infimum.
#const maxErrors=#supremum.
#const minSize=#infimum.
#const maxSize=#supremum.
#const minWeight=#infimum.
#const maxWeight=#supremum.

#program base.

%% bn generation

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

:- maxsize + 1 #sum {L,I,J : dnf(I,J) , hyper(I,J,L) }; maxsize >= 0.
%:- maxrss + 1 #sum {W,E,V,S : not eval(E,V,-S) , obs(E,V,D) , rss(D,V,S,W) }; maxrss >= 0.

%% data normalization

obsSpec(E,T,S) :- obs(E,T,S,X).
obsSpec(E,T,S) :- clamped(E,S,X), timepoint(E,T).
species(S) :- node(S,_).
unobsSpec(E,T,S) :- timepoint(E,T), species(S), not obsSpec(E,T,S).

measured(E,T,S,1) :- obs(E,T,S,X), X >= 50.
measured(E,T,S,0) :- obs(E,T,S,X), X < 50.

obsSpec(E,T,S) :- obs(E,T,S,X).
obsSpec(E,T,S) :- clamped(E,S,X), timepoint(E,T).

timepoint(E,T) :- measured(E,T,_,_).

maxtp(E,M) :- M = #max {T : timepoint(E,T)}, exp(E).
nextTP(E,T,T+1)    :- timepoint(E,T), timepoint(E,T+1).
nnextTP(E,T,T+1)   :- timepoint(E,T), not timepoint(E,T+1), T < M, maxtp(E,M).
nnextTP(E,T1,T2+1) :- nnextTP(E,T1,T2), not timepoint(E,T2+1).
nextTP(E,T1,T2+1)  :- nnextTP(E,T1,T2), timepoint(E,T2+1).

last(E,T) :- maxtp(E,T).

clause(X) :- clause(X,_,_).

toGuess(E,T,S) :- obs(E,T,S,X).
1{guessed(E,T,S,(1;0))}1  :- toGuess(E,T,S).
1{guessed(E,T,S,(1;0))}1  :- unobsSpec(E,T,S).
1{measured(E,T,S,(1;0))}1 :- unobsSpec(E,T,S).
%no errors in the unmeasured species
:-  unobsSpec(E,T,S), measured(E,T,S,V), not guessed(E,T,S,V).

%i have to have the same precondition (time 0) in all experiments
:- unobsSpec(E1,0,S), unobsSpec(E2,0,S), E1 < E2, measured(E1,0,S,V), not measured(E2,0,S,V).

#program support_consistency.

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

opposite(1,0).
opposite(0,1).
clamped(E,S) :- clamped(E,S,V).
%if we do not have guessed the opposing thing, we can have external support
ex_supp(E,T,L,X) :- formula(L,D), ex_supp(E,T,dnf,D,X), not clamped(E,L), opposite(X,Y), not guessed(E,T2,L,Y), nextTP(E,T,T2).
% if we guessed the opposing thing, the opposing thing needs to be justified before we can give support
{ex_supp(E,T,L,X)} :- formula(L,D), ex_supp(E,T,dnf,D,X), not clamped(E,L), opposite(X,Y), guessed(E,T2,L,Y), nextTP(E,T,T2).

supp(E,T,L,X) :- ex_supp(E,T,L,X).

:- guessed(E,T2,S,V), not supp(E,T1,S,V), nextTP(E,T1,T2).
:- guessed(E,T2,L,Y), opposite(X,Y), ex_supp(E,T1,L,X), not ex_supp(E,T1,L,Y), nextTP(E,T1,T2).

#program guess_bn_controllable.

% V is not reached by any stimulus (non-controllable)
:- dnf(I,J); edge(J,V,_); not stimulus(V);
   not path(U,V) : stimulus(U).

#program diversity.

#heuristic dnf(I,J) : before(I,J). [2@2,false] %diversity
#heuristic dnf(I,J). [1,false] %subset
#external before(I,J)  : dnf(I,J). %diversity

#program block_solution.

:- dnf(I,J) : (I,J) = @dnf(). % no repeating of answer sets

#program minimize_size.

#minimize{L@1,I,J : dnf(I,J) , hyper(I,J,L)}.

#program minimize_weight.

#minimize {Erg@2,E,T,S : measured(E,T,S,V), not guessed(E,T,S,V), toGuess(E,T,S), obs(E,T,S,M), Erg=50-M, M < 50}.
#minimize {Erg@2,E,T,S : measured(E,T,S,V), not guessed(E,T,S,V), toGuess(E,T,S), obs(E,T,S,M), Erg=M-49, M >= 50}.

#program tolerance.
:- not minSize #sum {L,I,J : dnf(I,J) , hyper(I,J,L)} maxSize.

:- not minErrors #sum {1,E,T,S : measured(E,T,S,V), not guessed(E,T,S,V), toGuess(E,T,S)} maxErrors.
:- not minWeight #sum {Erg,E,T,S : measured(E,T,S,V), not guessed(E,T,S,V), toGuess(E,T,S), obs(E,T,S,M), Erg=50-M, M < 50;
                       Erg,E,T,S : measured(E,T,S,V), not guessed(E,T,S,V), toGuess(E,T,S), obs(E,T,S,M), Erg=M-49, M >= 50} maxWeight.

#show formula/2.
#show dnf/2.
#show clause/3.