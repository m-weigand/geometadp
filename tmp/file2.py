from file1 import A  # you need this import for `B.py` to know what is `A`
from file1bis import Abis  # you need this import for `B.py` to know what is `A`
import copy 

class B(A,Abis): # Mean B inherit A
    def __init__(self):
        super(B, self).__init__() # This line all its parent's method (`__init__()`)
        print(Abis())
        for k, v in Abis().__dict__.items():
            print(k,v)
            self.__dict__[k] = copy.deepcopy(v)
            
            
    def printB(self):
        print("BBBBBBBBBBBB")

        super(B, self).printA()  # This line all its parent's method (`printA`)

# And you instantiate a `B` instance, then call a method of it, which call its super method `printA`
#b = B()
#b.printB()

#print(B.test)