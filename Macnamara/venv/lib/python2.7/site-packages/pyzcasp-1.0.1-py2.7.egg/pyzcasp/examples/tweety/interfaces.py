from zope import interface

class IBird(interface.Interface):
    name = interface.Attribute("bird name")
    penguin = interface.Attribute("True if is a penguin, False otherwise")

class IBirdList(interface.Interface):
    
    def __iter__(self):
        pass
        
class IFlyingBirds(IBirdList):
    pass