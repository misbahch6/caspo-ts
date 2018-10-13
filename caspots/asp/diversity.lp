#program diversity.
#heuristic dnf(I,J) : before(I,J). [2@2,false] %diversity
#heuristic dnf(I,J). [1,false] %subset
#external before(I,J)  : dnf(I,J). %diversity

#program skip.
:- dnf(I,J) : (I,J) = @dnf(). % no repeating of answer sets
