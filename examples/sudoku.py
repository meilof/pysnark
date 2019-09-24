# Verify Sudoku/Killer Sudoku puzzles
# Copyright (C) Meilof Veeningen 2019

import functools
import itertools
import operator

from pysnark.runtime import PrivVal, ignore_errors
from pysnark.hash import ggh_hash
from pysnark.pack import PackRepeat, PackIntMod

def vararray(vals):
    return list(map(lambda x: PrivVal(x) if x>=0 else -x, vals))

#ignore_errors(True)
#sol = list(map(vararray, 
#    [[0,0,0,0,0,-4,0,-9,0],
#     [-8,0,-2,-9,-7,0,0,0,0],
#     [-9,0,-1,-2,0,0,-3,0,0],
#     [0,0,0,0,-4,-9,-1,-5,-7],
#     [0,-1,-3,0,-5,0,-9,-2,0],
#     [-5,-7,-9,-1,-2,0,0,0,0],
#     [0,0,-7,0,0,-2,-6,0,-3],
#     [0,0,0,0,-3,-8,-2,0,-5],
#     [0,-2,0,-5,0,0,0,0,0]]))

sol = list(map(vararray, 
    [[7,3,5,6,1,-4,8,-9,2],
     [-8,4,-2,-9,-7,3,5,6,1],
     [-9,6,-1,-2,8,5,-3,7,4],
     [2,8,6,3,-4,-9,-1,-5,-7],
     [4,-1,-3,8,-5,7,-9,-2,6],
     [-5,-7,-9,-1,-2,6,4,3,8],
     [1,5,-7,4,9,-2,-6,8,-3],
     [6,9,4,7,-3,-8,-2,1,-5],
     [3,-2,8,-5,6,1,7,4,9]]))


# killer sudoku exercise specification
# "##": means a sum of a cage
# "< ": cell is in same cage as cell to the left of it
# "> ": cell is in same cage as cell to the right of it (use only if ##, < and ^ do not apply)
# "^ ": cell is in same cage as cell above it

## example taken from https://en.wikipedia.org/wiki/Killer_sudoku
#killer = [
#    "3 < 15< < 224 1615",
#    "25< 17< > ^ ^ ^ ^ ",
#    "^ ^ 9 < ^ 8 20< ^ ",
#    "6 14< ^ 17^ ^ 17^ ",
#    "^ 13< 20^ ^ > ^ 12",
#    "27^ 6 ^ ^ 206 < ^ ",
#    "^ > ^ ^ 10^ < 14< ",
#    "^ 8 16> ^ 15< ^ ^ ",
#    "^ ^ ^ ^ 13< < 17< "
#]

#sol=[[PrivVal(0) for _ in range(9)] for _ in range(9)]
#ignore_errors(True)

## solution taken from https://en.wikipedia.org/wiki/Killer_sudoku
#sol = list(map(vararray, 
#    [[2,1,5,6,4,7,3,9,8],
#     [3,6,8,9,5,2,1,7,4],
#     [7,9,4,3,8,1,6,5,2],
#     [5,8,6,2,7,4,9,3,1],
#     [1,4,2,5,9,3,8,6,7],
#     [9,7,3,8,1,6,4,2,5],
#     [8,2,1,7,3,9,5,4,6],
#     [6,5,9,4,2,8,7,1,3],
#     [4,3,7,1,6,5,2,8,9]]))


def prod(iterable):
    return functools.reduce(operator.mul, iterable, 1)

def check1to9(vals):
    print("checking 1-9 in", vals)
    for i in range(1,10):
        prod([val-i for val in vals]).assert_zero()
        
def block(vals,i,j):
    return [vals[i+(k//3)][j+(k%3)] for k in range(9)]
        
for (i,j) in itertools.product(range(3), repeat=2):
    check1to9(block(sol,3*i,3*j))
    
for i in range(9): check1to9(sol[i])
for j in range(9): check1to9([sol[i][j] for i in range(9)])

def killersums(kdesc):
    allsums = []
    for i in range(9):
        sums = []
        for j in range(9):
            cur = kdesc[i][j*2:j*2+2]
            if cur=="^ ":
                prevsums[j][1].append(sol[i][j])
                sums.append(prevsums[j])
            elif cur=="< ":
                sums[j-1][1].append(sol[i][j])
                sums.append(sums[j-1])
            elif cur=="> ":
                # find reference to above
                for k in range(j+1,9):
                    curk = kdesc[i][k*2:k*2+2]
                    if curk=="^ ":
                        prevsums[k][1].append(sol[i][j])
                        sums.append(prevsums[k])
                        break
            else:
                vl = int(kdesc[i][j*2:j*2+2])
                cursm = (vl, [sol[i][j]])
                allsums.append(cursm)
                sums.append(cursm)
        prevsums = sums
    return allsums
            
if "killer" in locals():
    for (sm,vls) in killersums(killer):
        print("checking sum", sm, vls)
        (sm-sum(vls)).assert_zero()
    
        # all points mutually different
        prod([vls[i]-vls[j] for i in range(len(vls)) for j in range(i+1,len(vls))]).assert_nonzero()
    
print("Solution hash:", ggh_hash(PackRepeat(PackRepeat(PackIntMod(16), 9), 9).pack(sol)).val())
    