import flatbuffers
import sys

import pysnark.gmpy as gmpy

import pysnark.zkinterface.BilinearConstraint as BilinearConstraint
import pysnark.zkinterface.Circuit as Circuit
import pysnark.zkinterface.Message as Message
import pysnark.zkinterface.R1CSConstraints as R1CSConstraints
import pysnark.zkinterface.Root as Root
import pysnark.zkinterface.Variables as Variables
import pysnark.zkinterface.Witness as Witness

modulus=21888242871839275222246405745257275088548364400416034343698204186575808495617

class LinearCombination:
    def __init__(self, lc): self.lc = lc
    def __add__(self, other):
        lc = dict()
        for a in self.lc:
            if a in other.lc:
                lc[a] = self.lc[a] + other.lc[a]
            else:
                lc[a] = self.lc[a]
        for b in other.lc:
            if not b in self.lc:
                lc[b] = other.lc[b]
        return LinearCombination(lc)
    
    def __sub__(self, other):
        return self+(-other)
    
    def __mul__(self, other):
        return LinearCombination({key:value*other for (key,value) in self.lc.items()})

    def __neg__(self):
        return self*-1

privvals = []
    
def privval(val):
    privvals.append(val)
    return LinearCombination({-len(privvals):1})

pubvals = []

def pubval(val):
    pubvals.append(val)
    return LinearCombination({len(pubvals):1})

def zero():
    return LinearCombination({})
    
def one():
    return LinearCombination({0:1})

def fieldinverse(val):
    return int(gmpy.invert(val, modulus))

def get_modulus():
    return modulus

constraints = []
def add_constraint(v, w, y):
    constraints.append([v,w,y])
    
def write_varlist(builder, vals, offset):
    Variables.VariablesStartVariableIdsVector(builder, len(vals))
    for i in reversed(range(len(vals))):
        builder.PrependUint64(i+offset)
    ixs = builder.EndVector(len(vals))
    
    Variables.VariablesStartValuesVector(builder, 32*len(vals))
    for i in reversed(range(len(vals))):
        val=vals[i]%modulus
        for j in reversed(range(32)):
            builder.PrependByte((val>>(j*8))&255)
    vals = builder.EndVector(32*len(vals))
        
    Variables.VariablesStart(builder)
    Variables.VariablesAddVariableIds(builder, ixs)
    Variables.VariablesAddValues(builder, vals)
    return Variables.VariablesEnd(builder)   
    
    
    
def prove():
    # TODO: this is pretty slow, maybe use this to improve performance:
    # https://github.com/google/flatbuffers/issues/4668
    
    f = open('computation.zkif', 'wb')
    
    print("*** zkinterface: writing circuit", file=sys.stderr)
    
    builder = flatbuffers.Builder(1024)

    vars = write_varlist(builder, pubvals, 1)
    
    Circuit.CircuitStartFieldMaximumVector(builder, 32)
    for i in reversed(range(32)):
        builder.PrependByte((modulus>>(i*8))&255)
    maxi = builder.EndVector(32)
    
    Circuit.CircuitStart(builder)
    Circuit.CircuitAddConnections(builder, vars)
    Circuit.CircuitAddFreeVariableId(builder, len(pubvals)+len(privvals)+1)
    Circuit.CircuitAddR1csGeneration(builder, True)
    Circuit.CircuitAddWitnessGeneration(builder, True)
    Circuit.CircuitAddFieldMaximum(builder, maxi)
    circ = Circuit.CircuitEnd(builder)
    
    Root.RootStart(builder)
    Root.RootAddMessageType(builder, Message.Message.Circuit)
    Root.RootAddMessage(builder, circ)
    root = Root.RootEnd(builder)
        
    builder.FinishSizePrefixed(root)
    buf = builder.Output()
    f.write(buf)
    
    print("*** zkinterface: writing witness", file=sys.stderr)
    
    # build witness
    builder = flatbuffers.Builder(1024)
    
    vars = write_varlist(builder, privvals, len(pubvals)+1)
    
    Witness.WitnessStart(builder)
    Witness.WitnessAddAssignedVariables(builder, vars)
    wit = Witness.WitnessEnd(builder)
    
    Root.RootStart(builder)
    Root.RootAddMessageType(builder, Message.Message.Witness)
    Root.RootAddMessage(builder, wit)
    root = Root.RootEnd(builder)    
    
    builder.FinishSizePrefixed(root)
    buf = builder.Output()
    f.write(buf)    
    
    print("*** zkinterface: writing constraints", file=sys.stderr)
    
    builder = flatbuffers.Builder(1024)
    
    def write_lc(lc):
        varls = list(lc.lc.keys())
        
        Variables.VariablesStartVariableIdsVector(builder, len(varls))
        for i in reversed(range(len(varls))):
            varix = varls[i] if varls[i]>=0 else len(pubvals)-varls[i]
            builder.PrependUint64(varix)
        vars = builder.EndVector(len(varls))
        
        Variables.VariablesStartValuesVector(builder, 32*len(varls))
        for i in reversed(range(len(varls))):
            for j in reversed(range(32)):
                val=lc.lc[varls[i]]%modulus
                builder.PrependByte((val>>(j*8))&255)
        vals = builder.EndVector(32*len(varls))
        
        Variables.VariablesStart(builder)
        Variables.VariablesAddVariableIds(builder, vars)
        Variables.VariablesAddValues(builder, vals)
        return Variables.VariablesEnd(builder)
    
    def write_constraint(c):
        la = write_lc(c[0])
        lb = write_lc(c[1])
        lc = write_lc(c[2])
        
        BilinearConstraint.BilinearConstraintStart(builder)
        BilinearConstraint.BilinearConstraintAddLinearCombinationA(builder, la)
        BilinearConstraint.BilinearConstraintAddLinearCombinationB(builder, lb)
        BilinearConstraint.BilinearConstraintAddLinearCombinationC(builder, lc)
        
        return BilinearConstraint.BilinearConstraintEnd(builder)       
        
    cs = [write_constraint(c) for c in constraints]
    
    R1CSConstraints.R1CSConstraintsStartConstraintsVector(builder, len(cs))
    for i in reversed(range(len(cs))):
        builder.PrependUOffsetTRelative(cs[i])
    cvec = builder.EndVector(len(cs))
    
    R1CSConstraints.R1CSConstraintsStart(builder)
    R1CSConstraints.R1CSConstraintsAddConstraints(builder, cvec)
    r1cs = R1CSConstraints.R1CSConstraintsEnd(builder)
    
    Root.RootStart(builder)
    Root.RootAddMessageType(builder, Message.Message.R1CSConstraints)
    Root.RootAddMessage(builder, r1cs)
    root = Root.RootEnd(builder)    
    
    builder.FinishSizePrefixed(root)
    buf = builder.Output()
    f.write(buf)

    f.close() 
    
    print("*** zkinterface circuit, witness, constraints written to 'computation.zkif', size", len(buf))
