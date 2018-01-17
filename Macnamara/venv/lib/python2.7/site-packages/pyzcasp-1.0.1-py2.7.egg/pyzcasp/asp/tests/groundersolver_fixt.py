from zope import interface, component
from pyzcasp import asp

class GrounderMock(asp.Grounder):
    def execute(self, lp, *args):
        if lp:
            assert('-' in args)
            
        return "",0

class SolverMock(asp.Solver):
    def execute(self, gr, *args):
        return "",0
        
    def answers(self):
        return [asp.AnswerSet(['a','b'], 10), asp.AnswerSet(['a','c','a(1)'], 12)]

class IScore(interface.Interface):
    score = interface.Attribute("a score")

class INoAdapter(interface.Interface):
    pass
    
class MockAdapter(object):
    component.adapts(asp.IAnswerSet)
    interface.implements(IScore)
    
    def __init__(self, answer):
        self.score = answer.score
    
    def __repr__(self):
        return "%s" % self.score

component.globalSiteManager.registerAdapter(MockAdapter)


def setup_test(test):
    test.globs['fake_grounder'] = GrounderMock(None)
    test.globs['fake_solver'] = SolverMock(None)
    test.globs['IScore'] = IScore
    test.globs['INoAdapter'] = INoAdapter

setup_test.__test__ = False
