from zope import interface, component
from pyzcasp import asp, potassco

class Gringo3Mock(potassco.Gringo3):
    def execute(self, lp, *args):
        if lp:
            assert('-' in args)
            
        return "",0

class ClaspMock(potassco.ClaspSolver):
    interface.implements(potassco.IDisjunctiveSolver)
    
    def execute(self, gr, *args):
        return "",0
        
    def answers(self):
        atoms = ["hold(atom(a(5)))", "hold(atom(a(4)))", "hold(atom(a(3)))", "hold(atom(a(2)))", "hold(atom(a(1)))"]
        return [asp.AnswerSet(atoms)]

class INumbers(interface.Interface):
    numbers = interface.Attribute("numbers")

class INoAdapter(interface.Interface):
    pass
    
class MockAdapter(object):
    component.adapts(asp.IAnswerSet)
    interface.implements(INumbers)
    
    def __init__(self, answer):
        self.numbers = []
        parser = asp.Grammar()
        parser.integer.addParseAction(lambda t: self.numbers.append(t[0]))
        [parser.parse(atom) for atom in answer.atoms]
        self.numbers = sorted(self.numbers)
    
    def __repr__(self):
        return "%s" % self.numbers

component.globalSiteManager.registerAdapter(MockAdapter)


def setup_test(test):
    test.globs['fake_gringo'] = Gringo3Mock(None)
    test.globs['fake_clasp'] = ClaspMock(None)
    test.globs['INumbers'] = INumbers

setup_test.__test__ = False
