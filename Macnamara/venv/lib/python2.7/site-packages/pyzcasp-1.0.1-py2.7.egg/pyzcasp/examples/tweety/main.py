from zope import component
from pyzcasp import potassco, asp
from pyzcasp.examples.tweety import *
    
if __name__ == '__main__':
    # first thing you would do is to register clingo utility
    potassco.configure(clingo="clingo")
    clingo = component.getUtility(potassco.IClingo)
    
    # tweety and sam are birds, sam is a penguin
    birds = BirdList([Bird('tweety'), Bird('sam', True)])

    flying_birds = component.getMultiAdapter((birds, clingo), IFlyingBirds)
    for bird in flying_birds:
        print bird.name # prints only tweety

    print '---'
    birds[1].penguin = False # fly sam, fly!!!
    flying_birds = component.getMultiAdapter((birds, clingo), IFlyingBirds)

    for bird in flying_birds:
        print bird.name # prints tweety and sam
