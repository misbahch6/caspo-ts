someerror(E,T,S) :- measured(E,T,S,V), not guessed(E,T,S,V), toGuess(E,T,S).
#show someerror/3.
