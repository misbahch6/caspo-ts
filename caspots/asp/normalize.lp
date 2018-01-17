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


