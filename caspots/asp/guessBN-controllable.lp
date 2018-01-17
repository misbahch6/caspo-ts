
% V is not reached by any stimulus (non-controllable)
:- dnf(I,J); edge(J,V,_); not stimulus(V);
   not path(U,V) : stimulus(U).

