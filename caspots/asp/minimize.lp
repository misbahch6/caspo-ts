#show measured/4.
#show guessed/4.
#minimize {1@2,E,T,S : measured(E,T,S,V), not guessed(E,T,S,V), toGuess(E,T,S)}.

#minimize{L@1,I,J : dnf(I,J) , hyper(I,J,L)}.
