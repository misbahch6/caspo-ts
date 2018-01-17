%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Meta-encoding of dominance check w.r.t. complex optimization criteria   %
% (to be combined with meta.lp and metaD.lp; configurable via facts over  %
%  user predicate optimize/3, cardinality considered by default; Pareto   %
%  improvement over weights used for comparison at a priority level)      %
% NOTE: complex optimization criteria are applied only to non-empty sets  %
%       of literals, as given via facts over minimize/2 and wlist/4       %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% extract (complex) optimization criteria per priority level and weight
% (relative to user predicate optimize/3; cardinality taken by default;
%  Pareto improvement over weights used for comparison at a priority level)

cxopt(card).  cxopt(incl).  cxopt(pref).

cxopt(J,W,O)    :- minimize(J,S), wlist(S,_,_,W), cxopt(O), optimize(J,W,O).
cxopt(J,W,card) :- minimize(J,S), wlist(S,_,_,W),
                   not optimize(J,W,O) : optimize(J,W,O).

% verify dominance

equal(J)     :- cxopt(J,_,_), equal(J,W,O) : cxopt(J,W,O).

chain(J1,J2) :- cxopt(J1;J2,_,_), J2 < J1,
                not cxopt(J3,W,O) : cxopt(J3,W,O) : J2 < J3 : J3 < J1.

check(J2)    :- cxopt(J2,_,_), not chain(J1,J2) : chain(J1,J2).
check(J2)    :- chain(J1,J2), check(J1), equal(J1).

bot          :- not cxopt(J,W,O) : cxopt(J,W,O).
bot          :- check(J1), worse(J1).
bot          :- check(J1), equal(J1), not chain(J1,J2) : chain(J1,J2).

% require non-existence of dominating answer set

:- not bot.

% check cardinality criteria

count(S,W)      :- cxopt(J,W,card), minimize(J,S).

count(S,W,0)    :- count(S,W), 0 #sum [ hold(P) = -1 : wlist(S,Q,pos(P),W),
                                    not hold(N) = -1 : wlist(S,Q,neg(N),W),
                                        true(P) =  1 : wlist(S,Q,pos(P),W),
                                        fail(N) =  1 : wlist(S,Q,neg(N),W) ].
count(S,W,1)    :- count(S,W), 1 #sum [ hold(P) = -1 : wlist(S,Q,pos(P),W),
                                    not hold(N) = -1 : wlist(S,Q,neg(N),W),
                                        true(P) =  1 : wlist(S,Q,pos(P),W),
                                        fail(N) =  1 : wlist(S,Q,neg(N),W) ].

equal(J,W,card) :- cxopt(J,W,card), minimize(J,S), count(S,W,0).

worse(J)        :- cxopt(J,W,card), minimize(J,S), count(S,W,1).

% check inclusion criteria

ndiff(pos(P))   :- cxopt(J,W,incl), minimize(J,S), wlist(S,_,pos(P),W),
                   true(P).
ndiff(pos(P))   :- cxopt(J,W,incl), minimize(J,S), wlist(S,_,pos(P),W),
                            not hold(P).
ndiff(pos(P))   :- cxopt(J,W,incl), minimize(J,S), wlist(S,_,pos(P);neg(P),W).
ndiff(neg(N))   :- cxopt(J,W,incl), minimize(J,S), wlist(S,_,neg(N),W),
                   fail(N).
ndiff(neg(N))   :- cxopt(J,W,incl), minimize(J,S), wlist(S,_,neg(N),W),
                                hold(N).
ndiff(neg(N))   :- cxopt(J,W,incl), minimize(J,S), wlist(S,_,neg(N);pos(N),W).

equal(J,W,incl) :- cxopt(J,W,incl), minimize(J,S), ndiff(E) : wlist(S,_,E,W).

worse(J)        :- cxopt(J,W,incl), minimize(J,S), wlist(S,_,pos(P),W),
                   true(P), not hold(P).
worse(J)        :- cxopt(J,W,incl), minimize(J,S), wlist(S,_,neg(N),W),
                   fail(N),     hold(N).

% check preference criteria (relative to user predicate prefer/2)

cando(pos(P))   :- cxopt(J,W,pref), minimize(J,S), wlist(S,_,pos(P),W),
                   fail(P),     hold(P).
cando(neg(N))   :- cxopt(J,W,pref), minimize(J,S), wlist(S,_,neg(N),W),
                   true(N), not hold(N).
nocan(pos(P))   :- cxopt(J,W,pref), minimize(J,S), wlist(S,_,pos(P),W),
                   true(P).
nocan(pos(P))   :- cxopt(J,W,pref), minimize(J,S), wlist(S,_,pos(P),W),
                            not hold(P).
nocan(neg(N))   :- cxopt(J,W,pref), minimize(J,S), wlist(S,_,neg(N),W),
                   fail(N).
nocan(neg(N))   :- cxopt(J,W,pref), minimize(J,S), wlist(S,_,neg(N),W),
                                hold(N).

condo(pos(P))   :- cxopt(J,W,pref), minimize(J,S), wlist(S,_,pos(P),W),
                   true(P), not hold(P).
condo(neg(N))   :- cxopt(J,W,pref), minimize(J,S), wlist(S,_,neg(N),W),
                   fail(N),     hold(N).
nocon(pos(P))   :- cxopt(J,W,pref), minimize(J,S), wlist(S,_,pos(P),W),
                   fail(P).
nocon(pos(P))   :- cxopt(J,W,pref), minimize(J,S), wlist(S,_,pos(P),W),
                                hold(P).
nocon(neg(N))   :- cxopt(J,W,pref), minimize(J,S), wlist(S,_,neg(N),W),
                   true(N).
nocon(neg(N))   :- cxopt(J,W,pref), minimize(J,S), wlist(S,_,neg(N),W),
                            not hold(N).

cando(S,W,E)    :- cxopt(J,W,pref), minimize(J,S), wlist(S,_,E;E1,W),
                   prefer(E,E1), E1 != E, cando(E), condo(E1).

nocon(S,W,E)    :- cxopt(J,W,pref), minimize(J,S), wlist(S,_,E,W), nocon(E).
nocon(S,W,E)    :- cxopt(J,W,pref), minimize(J,S), wlist(S,_,E,W),
                   nocan(E1) : wlist(S,_,E1,W) : E1 != E : prefer(E,E1).
nocon(S,W,E)    :- cxopt(J,W,pref), minimize(J,S), wlist(S,_,E;E2,W),
                   prefer(E2,E), not prefer(E,E2), cando(E2).

equal(J,W,pref) :- cxopt(J,W,pref), minimize(J,S), cando(S,W,E),
                   nocon(E2) : wlist(S,_,E2,W) : prefer(E2,E) : not prefer(E,E2).

worse(J)        :- cxopt(J,W,pref), minimize(J,S), nocon(S,W,E) : wlist(S,_,E,W).
