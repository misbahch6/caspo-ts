ab(X)    :- penguin(X).
flies(X) :- bird(X); not ab(X).

#show flies/1.
