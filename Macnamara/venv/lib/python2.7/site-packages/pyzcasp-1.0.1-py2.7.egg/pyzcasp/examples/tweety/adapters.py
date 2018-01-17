from zope import component, interface
from pyzcasp import asp, potassco

from interfaces import *
from impl import *

class BirdList2TermSet(asp.TermSetAdapter):
    component.adapts(IBirdList)
    interface.implements(asp.ITermSet)
    
    def __init__(self, birds):
        super(BirdList2TermSet, self).__init__()
        for bird in birds:
            self._termset.add(asp.Term('bird', [bird.name]))
            if bird.penguin:
                self._termset.add(asp.Term('penguin', [bird.name]))

class AnswerSet2BirdList(object):
    component.adapts(asp.IAnswerSet)
    interface.implements(IBirdList)
    
    def __init__(self, answer):
        super(AnswerSet2BirdList, self).__init__()

        parser = asp.Grammar()
        parser.function.setParseAction(lambda t: Bird(t['args'][0]))
        self.birds = BirdList([parser.parse(atom) for atom in answer.atoms])
        
    def __iter__(self):
        return iter(self.birds)

class FlyQuery(object):
    component.adapts(IBirdList, potassco.IGrounderSolver)
    interface.implements(IFlyingBirds)
    
    def __init__(self, birds, clingo):
        #adapt list of birds to logic facts
        self.instance = asp.ITermSet(birds)
        self.clingo = clingo
        
        # get encodings for the grounder
        encodings = component.getUtility(asp.IEncodingRegistry).encodings(self.clingo.grounder) 
        
        #run clingo with an instance and encoding. Resulting answer sets are adapted to a list of birds
        self._answers = self.clingo.run(self.instance.to_str(), grounder_args=[encodings('flies')], adapter=IBirdList)
        if not self.clingo.sat:
            raise "Something went very wrong..."
            
    def __iter__(self):
        return iter(self._answers[0])
        
        