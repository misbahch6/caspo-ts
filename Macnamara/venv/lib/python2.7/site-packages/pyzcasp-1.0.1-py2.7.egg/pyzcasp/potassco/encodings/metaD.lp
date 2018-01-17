%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Disjunctive meta-encoding of reified logic programs' answer sets        %
% (to be combined with meta.lp and metaO.lp)                              %
% NOTE: not applicable to disjunctions and avg, even, and odd aggregates  %
%       as well as sum aggregates including literals with negative weight %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% extract scope of interpretations

elem(E)  :- eleb(E).
elem(E)  :- rule(pos(E),_).
elem(P)  :- rule(pos(sum(_,S,_)),_), wlist(S,_,pos(P),_).
elem(P)  :- rule(pos(min(_,S,_)),_), wlist(S,_,pos(P),_).
elem(P)  :- rule(pos(max(_,S,_)),_), wlist(S,_,pos(P),_).
elem(P)  :- minimize(J,S),           wlist(S,_,pos(P),W), cxopt(J,W,_).
elem(N)  :- rule(pos(sum(_,S,_)),_), wlist(S,_,neg(N),_).
elem(N)  :- rule(pos(min(_,S,_)),_), wlist(S,_,neg(N),_).
elem(N)  :- rule(pos(max(_,S,_)),_), wlist(S,_,neg(N),_).
elem(N)  :- minimize(J,S),           wlist(S,_,neg(N),W), cxopt(J,W,_).

sum(S,T) :- elem(sum(_,S,_)), T = #sum [ wlist(S,Q,_,W) = W ].

% extract supports of atoms and facts

supp(atom(A),B) :- rule(pos(atom(A)),   pos(B)).
supp(atom(A),B) :- rule(pos(sum(_,S,_)),pos(B)), wlist(S,_,pos(atom(A)),_).
supp(atom(A),B) :- rule(pos(min(_,S,_)),pos(B)), wlist(S,_,pos(atom(A)),_).
supp(atom(A),B) :- rule(pos(max(_,S,_)),pos(B)), wlist(S,_,pos(atom(A)),_).

supp(atom(A))   :- supp(atom(A),B).

fact(atom(A))   :- rule(pos(atom(A)),pos(conjunction(S))),
                   not set(S,E) : set(S,E).

% generate interpretation

true(atom(A))                 :- fact(atom(A)).
true(atom(A)) | fail(atom(A)) :- supp(atom(A)), not fact(atom(A)).
                fail(atom(A)) :- elem(atom(A)), not supp(atom(A)).

fail(false).

true(conjunction(S)) :- elem(conjunction(S)),
                        true(P) : set(S,pos(P)), fail(N) : set(S,neg(N)).
fail(conjunction(S)) :- elem(conjunction(S)), set(S,pos(P)), fail(P).
fail(conjunction(S)) :- elem(conjunction(S)), set(S,neg(N)), true(N).

true(sum(L,S,U))     :- elem(sum(L,S,U)), sum(S,T),
                      L     #sum   [ true(P) = W : wlist(S,Q,pos(P),W),
                                     fail(N) = W : wlist(S,Q,neg(N),W) ],
                      T-U   #sum   [ fail(P) = W : wlist(S,Q,pos(P),W),
                                     true(N) = W : wlist(S,Q,neg(N),W) ].
fail(sum(L,S,U))     :- elem(sum(L,S,U)), sum(S,T),
                      T-L+1 #sum   [ fail(P) = W : wlist(S,Q,pos(P),W),
                                     true(N) = W : wlist(S,Q,neg(N),W) ].
fail(sum(L,S,U))     :- elem(sum(L,S,U)),
                      U+1   #sum   [ true(P) = W : wlist(S,Q,pos(P),W),
                                     fail(N) = W : wlist(S,Q,neg(N),W) ].

true(min(L,S,U))     :- elem(min(L,S,U)),
                      1     #count {      U == #supremum,
                                     true(P)     : wlist(S,_,pos(P),W) : L <= W : W <= U,
                                     fail(N)     : wlist(S,_,neg(N),W) : L <= W : W <= U },
                                     fail(P)     : wlist(S,_,pos(P),W) : W <  L,
                                     true(N)     : wlist(S,_,neg(N),W) : W <  L.
fail(min(L,S,U))     :- elem(min(L,S,U)), U != #supremum,
                                     fail(P)     : wlist(S,_,pos(P),W) : L <= W : W <= U,
                                     true(N)     : wlist(S,_,neg(N),W) : L <= W : W <= U.
fail(min(L,S,U))     :- elem(min(L,S,U)),
                      1     #count { true(P)     : wlist(S,_,pos(P),W) : W <  L,
                                     fail(N)     : wlist(S,_,neg(N),W) : W <  L }.

true(max(L,S,U))     :- elem(max(L,S,U)),
                      1     #count {      L == #infimum,
                                     true(P)     : wlist(S,_,pos(P),W) : L <= W : W <= U,
                                     fail(N)     : wlist(S,_,neg(N),W) : L <= W : W <= U },
                                     fail(P)     : wlist(S,_,pos(P),W) : U <  W,
                                     true(N)     : wlist(S,_,neg(N),W) : U <  W.
fail(max(L,S,U))     :- elem(max(L,S,U)), L != #infimum,
                                     fail(P)     : wlist(S,_,pos(P),W) : L <= W : W <= U,
                                     true(N)     : wlist(S,_,neg(N),W) : L <= W : W <= U.
fail(max(L,S,U))     :- elem(max(L,S,U)),
                      1     #count { true(P)     : wlist(S,_,pos(P),W) : U <  W,
                                     fail(N)     : wlist(S,_,neg(N),W) : U <  W }.

% verify supported model properties

bot :- rule(pos(H),pos(B)), true(B), fail(H).
bot :- true(atom(A)), fail(B) : supp(atom(A),B).

% verify acyclic derivability

step(C,Z)                :- scc(C,_), Z = #sum [ scc(C,pos(atom(A))) : not fact(atom(A)) ].

sccw(A)                  :- scc(C,pos(atom(A))), not fact(atom(A)),
                            fail(B) : supp(atom(A),B) : not scc(C,pos(B)).

wait(E,D-1)              :- scc(C,pos(E)), fail(E), step(C,Z), D = 1..Z.

wait(atom(A),0)          :- scc(C,pos(atom(A))), not fact(atom(A)).
wait(atom(A),D)          :- scc(C,pos(atom(A))), sccw(A), step(C,Z), D = 1..Z,
                            wait(B,D-1) : supp(atom(A),B) : scc(C,pos(B)).

wait(sum(L,S,U),D-1) :- scc(C,pos(sum(L,S,U))), sum(S,T), step(C,Z), D = 1..Z,
       T-L+1 #sum [ fail(P) = W : wlist(S,Q,pos(P),W) : not scc(C,pos(P)),
                wait(P,D-1) = W : wlist(S,Q,pos(P),W) :     scc(C,pos(P)),
                    true(N) = W : wlist(S,Q,neg(N),W) ].

wait(min(L,S,U),0)   :- scc(C,pos(min(L,S,U))), U != #supremum,
                    fail(P)     : wlist(S,_,pos(P),W) : not scc(C,pos(P)) : L <= W : W <= U,
                  wait(P,0)     : wlist(S,_,pos(P),W) :     scc(C,pos(P)) : L <= W : W <= U,
                    true(N)     : wlist(S,_,neg(N),W)                     : L <= W : W <= U.
wait(min(L,S,U),D-1) :- scc(C,pos(min(L,S,U))), wait(min(L,S,U),0), step(C,Z), D = 2..Z,
                wait(P,D-1)     : wlist(S,_,pos(P),W) :     scc(C,pos(P)) : L <= W : W <= U.

wait(max(L,S,U),0)   :- scc(C,pos(max(L,S,U))), L != #infimum,
                    fail(P)     : wlist(S,_,pos(P),W) : not scc(C,pos(P)) : L <= W : W <= U,
                  wait(P,0)     : wlist(S,_,pos(P),W) :     scc(C,pos(P)) : L <= W : W <= U,
                    true(N)     : wlist(S,_,neg(N),W)                     : L <= W : W <= U.
wait(max(L,S,U),D-1) :- scc(C,pos(max(L,S,U))), wait(max(L,S,U),0), step(C,Z), D = 2..Z,
                wait(P,D-1)     : wlist(S,_,pos(P),W) :     scc(C,pos(P)) : L <= W : W <= U.

wait(conjunction(S),D-1) :- scc(C,pos(conjunction(S))), set(S,pos(P)),
                            scc(C,pos(P)), wait(P,D-1), step(C,Z), D = 1..Z.

bot :- scc(C,pos(atom(A))), true(atom(A)), wait(atom(A),Z), step(C,Z).

% saturate interpretations that are not answer sets

true(atom(A)) :- supp(atom(A)), not fact(atom(A)), bot.
fail(atom(A)) :- supp(atom(A)), not fact(atom(A)), bot.
