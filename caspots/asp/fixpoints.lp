
fp(E) :- fp(E,_,_).
readout(L) :- fp(E,L,_).

convert(-1,0).
convert(1,1).
dnf(D) :- dnf(D,_).
clause(X) :- clause(X,_,_).

constant(L) :- formula(L, D); not dnf(D).
constant(L) :- fp(_,L,_); not formula(L, _).

constval(L, B) :- constant(L); fp(_,L,B).
:- constval(L, B); constval(L, B'); B != B'.

eval(E,clause,C,0) :- clause(C,L,-1); fp(E,L,1).
eval(E,clause,C,0) :- clause(C,L,1); fp(E,L,0).
eval(E,clause,C,1) :- fp(E,L,B) : clause(C,L,S),convert(S,B) ; clause(C) ; fp(E).

eval(E,dnf,D,1) :- eval(E,clause,C,1); dnf(D,C).
eval(E,dnf,D,0) :- eval(E,clause,C,0) : dnf(D,C); dnf(D) ; fp(E).

eval(E,L,B) :- formula(L,D) ; eval(E,dnf,D,B).
eval(E,L,B) :- constval(L,B); fp(E).

:- fp(E,L,B); not eval(E,L,B).


%#show eval/4.
%#show eval/3.
%#show constant/1.
%#show constval/2.

