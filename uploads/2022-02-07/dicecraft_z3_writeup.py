from z3 import *

# initial bumper seed
initSeed = 0xD1C40677

# the directions each bumper needs to go (right, down, right, up, right...)
dirsToMatch = [0,2,0,3,0,2,0,3,0,2,0,3,0,2,0,3]
# every bumper starts with an initial value of 0xD1C40677
seedTemplate = [initSeed] * 16


# these are the values on the top terminal computers
stringEncryptionTable = [
    0xC7F55F80,
    0xEC0172A7,
    0x42C649D1,
    0x61F1EFE3,
    0xE093FF3D,
    0xF433EDE6,
    0x141E5834,
    0x0241026E,
    0xF4F89624,
    0x09C64458
]

# this is the scramble table used in the mut computer after adding
stringScrambleTable = [
    7, 9, 5, 6, 14, 10, 12, 8, 1, 2, 13, 15, 4, 11, 0, 3
]

# reverses mut computer output by brute force
def decryptString(result, index):
    stringEncryptionBlock = stringEncryptionTable[index]
    strPieces = 0
    for charIdx in range(8):
        resPiece = (result >> (28 - (charIdx * 4))) & 0xf
        encPiece = (stringEncryptionBlock >> (28 - (charIdx * 4))) & 0xf
        for scramIdx in range(16):
            if stringScrambleTable[(encPiece + scramIdx) & 0xf] == resPiece:
                strPieces <<= 4
                strPieces |= scramIdx
                break
    return bytes.fromhex(hex(strPieces)[2:]).decode("latin-1")


# simulates bumper computers
class Simulator():
    def __init__(self, powerLevel):
        self.powerLevel = powerLevel
        self.seeds = [0] * 16

    def simulate(self, index, useSeedsArray):
        originalPowerLevel = self.powerLevel
        self.powerLevel >>= 2
        
        seed = seedTemplate[index]
        
        seed = ((seed << 13) & 0xffffffff) ^ seed
        seed = ((seed >> 17) & 0xffffffff) ^ seed
        seed = ((seed <<  5) & 0xffffffff) ^ seed
        
        if index != 15:
            seed = ((seed * self.powerLevel) & 0xffffffff) ^ self.powerLevel
        
        seed += originalPowerLevel & 3
        
        dirResult = seed % 4
        dirToMatch = dirsToMatch[index]
        
        if useSeedsArray:
            self.seeds[index] = seed
        
        return (dirResult, dirToMatch)


def runSimulation(index):
    global seedTemplate
    
    # run simulation for z3
    solution = BitVec("sol", 32)
    s = Solver()
    
    sim = Simulator(solution)
    for i in range(16):
        j = sim.simulate(i, False)
        s.add(j[0] == j[1])
    
    s.check()
    model = s.model()
    
    realSolution = int(model[solution].as_long())
    print(decryptString(realSolution, index))
    
    # update seeds for next eight hex characters
    simReal = Simulator(realSolution)
    for i in range(16):
        simReal.simulate(i, True)
    
    seedTemplate = simReal.seeds


def main():
    for i in range(10):
        runSimulation(i)

main()