class NoneObject:
    def __add__(self, other): return NoneObject()
    def __sub__(self, other): return NoneObject()
    def __mul__(self, other): return NoneObject()
    def __neg__(self): return NoneObject()

def privval(val):
    return NoneObject()

def pubval(val):
    return NoneObject()

def zero():
    return NoneObject()
    
def one():
    return NoneObject()

def fieldinverse(val):
    return 0

def get_modulus():
    return 1

def add_constraint(v, w, y):
    pass
    
def prove():
    pass