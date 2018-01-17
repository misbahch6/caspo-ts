import os
from zope import component
from pyzcasp import asp, examples

from adapters import *

gsm = component.getGlobalSiteManager()
path = os.path.dirname(examples.__file__)

gsm.registerAdapter(BirdList2TermSet)
gsm.registerAdapter(AnswerSet2BirdList)
gsm.registerAdapter(FlyQuery)

gsm.registerUtility(asp.EncodingRegistry(), asp.IEncodingRegistry, 'example.tweety')

reg = component.getUtility(asp.IEncodingRegistry, 'example.tweety')
reg.register('flies', os.path.join(path, 'encodings/flies.lp'), potassco.IGringo4)
