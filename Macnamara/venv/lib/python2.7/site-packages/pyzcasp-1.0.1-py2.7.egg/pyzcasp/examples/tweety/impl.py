from zope import interface
from interfaces import *

class Bird(object):
    interface.implements(IBird)
    
    def __init__(self, name, penguin=False):
        self.name = name
        self.penguin = penguin
        
class BirdList(list):
    interface.implements(IBirdList)
    
    def __init__(self, iterable):
        super(BirdList, self).__init__(iterable)
