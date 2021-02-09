import math
from procedural_options import optionslist
from z3 import *

def roundMute(v): #muted node, so it's basically commented out
    #return round(v)
    return v

def Memer(A, B, C, D):
    outA = round((A*A) % C)
    outC = roundMute(C)
    outB = roundMute(max(math.floor(B/2), 0))
    bmod2 = B%2
    outD = roundMute((((1-bmod2)+(bmod2*A))*D)%C)
    return (outA, outB, outC, outD)

def Memes(A, B, C):
    (mA, mB, mC, mD) = Memer(A, B, C, 1)
    (mA, mB, mC, mD) = Memer(mA, mB, mC, mD)
    (mA, mB, mC, mD) = Memer(mA, mB, mC, mD)
    (mA, mB, mC, mD) = Memer(mA, mB, mC, mD)
    
    (mA, mB, mC, mD) = Memer(mA, mB, mC, mD)
    (mA, mB, mC, mD) = Memer(mA, mB, mC, mD)
    (mA, mB, mC, mD) = Memer(mA, mB, mC, mD)
    (mA, mB, mC, mD) = Memer(mA, mB, mC, mD)
    
    (mA, mB, mC, mD) = Memer(mA, mB, mC, mD)
    (mA, mB, mC, mD) = Memer(mA, mB, mC, mD)
    (mA, mB, mC, mD) = Memer(mA, mB, mC, mD)
    (mA, mB, mC, mD) = Memer(mA, mB, mC, mD)
    
    (mA, mB, mC, mD) = Memer(mA, mB, mC, mD)
    (mA, mB, mC, mD) = Memer(mA, mB, mC, mD)
    (mA, mB, mC, mD) = Memer(mA, mB, mC, mD)
    (mA, mB, mC, mD) = Memer(mA, mB, mC, mD)
    
    return mD

def Dice1(Meme, A):
    return [Memes(Meme, A, 667), Meme, A]

def Dice2(Meme, A, B):
    temp = Memes(Meme[0], A, 667)
    outX = Memes(temp, B, 667)
    outZ = ((Meme[2]*10)+A)%65536
    return [outX, Meme[1], outZ]

def Dice3(Meme, A):
    temp = Memes(Meme[0], A, 667)
    lhsm = 1 if (abs(temp - Meme[1]) <= 0.1) else 0
    rhsm = 1 if (Meme[2] > 0) else 0 #shouldn't happen since %65536
    return [lhsm*rhsm,Meme[2]]

def NodeGroup005(Z, Char, Base):
    return 1 if (((Z + Char + Base) % 256) <= 0.1) else 0

def NodeGroup006(Z, C1, C2, B1, B2):
    return NodeGroup005(Z%256, C1, B1) * NodeGroup005(math.floor(Z/256) % 256, C2, B2)

def Checker(Z1, Z2, Z3, Z4, Z5, Z6, Z7, flag):
    # there are checks for dice{} here too but who cares
    cond1 = NodeGroup006(Z1, flag[6-1], flag[7-1], 63, 204)
    cond2 = NodeGroup006(Z2, flag[8-1], flag[9-1], 148, 173)
    cond3 = NodeGroup006(Z3, flag[10-1], flag[11-1], 70, 148)
    cond4 = NodeGroup006(Z4, flag[12-1], flag[13-1], 248, 229)
    cond5 = NodeGroup006(Z5, flag[14-1], flag[15-1], 102, 113)
    cond6 = NodeGroup006(Z6, flag[16-1], flag[17-1], 38, 60)
    cond7 = NodeGroup006(Z7, flag[18-1], flag[19-1], 63, 14)
    cond8 = NodeGroup006(Z1, flag[20-1], flag[21-1], 56, 136)
    cond9 = NodeGroup006(Z2, flag[22-1], flag[23-1], 234, 235)
    return (cond1 * cond2 * cond3 * cond4 * cond5 * cond6 * cond7 * cond8 * cond9) == 1

def getZValue(x1c, x2c, x3c, x4c, x5c, x6c, x7c):
    x1 = Dice1(inp, values1[x1c])
    x2 = Dice2(x1, values2_A[x2c], values2_B[x2c])
    x3 = Dice2(x2, values3_A[x3c], values3_B[x3c])
    x4 = Dice2(x3, values4_A[x4c], values4_B[x4c])
    x5 = Dice2(x4, values5_A[x5c], values5_B[x5c])
    x6 = Dice2(x5, values6_A[x6c], values6_B[x6c])       
    x7 = Dice3(x6, values7[x7c])
    return x7[1] # Z value

def brute_checker(Z1, Z2, Z3, Z4, Z5, Z6, Z7):   
    a = [[],[],[],[],[],[],[],[],[]]
    for x in range(255):
        for y in range(255):
            cond1 = NodeGroup006(Z1, x, y, 63, 204) == 1
            cond2 = NodeGroup006(Z2, x, y, 148, 173) == 1
            cond3 = NodeGroup006(Z3, x, y, 70, 148) == 1
            cond4 = NodeGroup006(Z4, x, y, 248, 229) == 1
            cond5 = NodeGroup006(Z5, x, y, 102, 113) == 1
            cond6 = NodeGroup006(Z6, x, y, 38, 60) == 1
            cond7 = NodeGroup006(Z7, x, y, 63, 14) == 1
            cond8 = NodeGroup006(Z1, x, y, 56, 136) == 1
            cond9 = NodeGroup006(Z2, x, y, 234, 235) == 1
            if cond1:
                a[0].append(chr(x) + " " + chr(y) + f" {x}, {y}")
            if cond2:
                a[1].append(chr(x) + " " + chr(y) + f" {x}, {y}")
            if cond3:
                a[2].append(chr(x) + " " + chr(y) + f" {x}, {y}")
            if cond4:
                a[3].append(chr(x) + " " + chr(y) + f" {x}, {y}")
            if cond5:
                a[4].append(chr(x) + " " + chr(y) + f" {x}, {y}")
            if cond6:
                a[5].append(chr(x) + " " + chr(y) + f" {x}, {y}")
            if cond7:
                a[6].append(chr(x) + " " + chr(y) + f" {x}, {y}")
            if cond8:
                a[7].append(chr(x) + " " + chr(y) + f" {x}, {y}")
            if cond9:
                a[8].append(chr(x) + " " + chr(y) + f" {x}, {y}")
    print(a[0])
    print(a[1])
    print(a[2])
    print(a[3])
    print(a[4])
    print(a[5])
    print(a[6])
    print(a[7])
    print(a[8])

###########################################################################

values1   = [13,17,19,23,29,31,37]
values2_A = [41,43,47,53,59,61,67]
values2_B = [237,375,227,85,145,159,333]
values3_A = [71,73,79,83,89,97,101]
values3_B = [355,43,601,331,367,93,101]
values4_A = [103,107,109,113,127,131,137]
values4_B = [481,353,295,489,39,61,475]
values5_A = [139,149,151,157,163,167,173]
values5_B = [9,395,519,169,373,403,311]
values6_A = [179,181,191,193,197,199,211]
values6_B = [291,565,381,195,277,359,391]
values7   = [405,487,499,435,233,197,551]

c1 = [BitVec(f'{i}', 8) for i in range(7*7)]
s = Solver()

# Dice1
for i in range(7):
    s.add(c1[7*i]==i)

# Dice2 & Dice3
for j in range(1, 7):
    for i in range(7):
        s.add(c1[j+7*i] >= 0)
        s.add(c1[j+7*i] <= 6)

# Unique columns (connections)
for i in range(7):
    s.add(Distinct(c1[i], c1[i+7*1], c1[i+7*2], c1[i+7*3], c1[i+7*4], c1[i+7*5], c1[i+7*6]))

# This would be the result if the output from MemeGenerator was 665
# I just chose this since it was right under 667
inp = 665

print("brute forcing x1-x7... hold on")
# Simple brute force since I'm too dumb to figure this out with z3
for x1c in range(7):
    cond = False
    x1 = Dice1(inp, values1[x1c])
    for x2c in range(7):
        x2 = Dice2(x1, values2_A[x2c], values2_B[x2c])
        for x3c in range(7):
            x3 = Dice2(x2, values3_A[x3c], values3_B[x3c])
            for x4c in range(7):
                x4 = Dice2(x3, values4_A[x4c], values4_B[x4c])
                for x5c in range(7):
                    x5 = Dice2(x4, values5_A[x5c], values5_B[x5c])
                    for x6c in range(7):
                        x6 = Dice2(x5, values6_A[x6c], values6_B[x6c])
                        for x7c in range(7):
                            x7 = Dice3(x6, values7[x7c])
                            
                            valid = False
                            if x7[0] != 0: # dice3 is not 0 (1)
                                # if Z value is either 0 or 1, it needs to
                                # be printable for the last two nodes too
                                if x7c == 0 or x7c == 1:
                                    if (x7[1] in optionslist[x7c] and
                                        x7[1] in optionslist[x7c+7]):
                                        valid = True
                                # otherwise, check the list like normal
                                else:
                                    if x7[1] in optionslist[x7c]:
                                        valid = True
                            
                            if valid:
                                cond = (Or(cond,
                                    And(c1[1+x1c*7]==x2c,
                                        c1[2+x1c*7]==x3c,
                                        c1[3+x1c*7]==x4c,
                                        c1[4+x1c*7]==x5c,
                                        c1[5+x1c*7]==x6c,
                                        c1[6+x1c*7]==x7c
                                    )
                                ))
    s.add(cond)

print("done.")

print(s.check())
model = s.model()
results = ([int(str(model[c1[i]])) for i in range(len(model))])

print(results[7*0:7*1])
print(results[7*1:7*2])
print(results[7*2:7*3])
print(results[7*3:7*4])
print(results[7*4:7*5])
print(results[7*5:7*6])
print(results[7*6:7*7])

Zarr = [None] * 7
Zarr[results[6+7*0]] = getZValue(*results[7*0:7*1])
Zarr[results[6+7*1]] = getZValue(*results[7*1:7*2])
Zarr[results[6+7*2]] = getZValue(*results[7*2:7*3])
Zarr[results[6+7*3]] = getZValue(*results[7*3:7*4])
Zarr[results[6+7*4]] = getZValue(*results[7*4:7*5])
Zarr[results[6+7*5]] = getZValue(*results[7*5:7*6])
Zarr[results[6+7*6]] = getZValue(*results[7*6:7*7])

brute_checker(*Zarr)