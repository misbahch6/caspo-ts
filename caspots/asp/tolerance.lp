
%:- not 11 #sum {1,E,T,L,Y : mynewerror(E,T,L,Y)} 11.
#const minErrors=#infimum.
#const maxErrors=#supremum.
#const minSize=#infimum.
#const maxSize=#supremum.
#const minWeight=#infimum.
#const maxWeight=#supremum.
%:- not minErrors #sum {1,E,T,S : error(E,T,S); 1,E,T,L,Y : mynewerror(E,T,L,Y)} maxErrors.
:- not minSize #sum {L,I,J : dnf(I,J) , hyper(I,J,L)} maxSize.
%:- not minWeight #sum {Erg,E,T,S : error(E,T,S), obs(E,T,S,V), Erg=50-V, V < 50; Erg,E,T,L,Y : mynewerror(E,T,L,Y), obs(E,T,L,V), Erg=50-V, V < 50;
%                       Erg,E,T,S : error(E,T,S), obs(E,T,S,V), Erg=V-49, V >= 50; Erg,E,T,L,Y : mynewerror(E,T,L,Y), obs(E,T,L,V), Erg=V-49, V >= 50} maxWeight.

%#show measured/4.
%#show guessed/4.
:-  not minErrors #sum {1,E,T,S : measured(E,T,S,V), not guessed(E,T,S,V), toGuess(E,T,S)} maxErrors.
:- not minWeight #sum {Erg,E,T,S : measured(E,T,S,V), not guessed(E,T,S,V), toGuess(E,T,S), obs(E,T,S,M), Erg=50-M, M < 50;
                       Erg,E,T,S : measured(E,T,S,V), not guessed(E,T,S,V), toGuess(E,T,S), obs(E,T,S,M), Erg=M-49, M >= 50} maxWeight.

#show formula/2.
#show dnf/2.
#show clause/3.

