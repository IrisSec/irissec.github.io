import sys

class SimSim:
    def loadText(self, text):
        self.text = bytearray(text.encode("utf-8"))

    def start(self, lines):
        self.lines = lines
        self.lineIdx = 0
        self.tmp0 = 0

        while True:
            self.step()
            if self.lineIdx >= len(self.lines):
                break
            
        
    def scramble(self, startx, countx, starty, county):
        newList = []
        actualStartx = startx
        actualCountx = countx
        actualCounty = county
        while True:
            if county > 0:
                newList.append(self.text[starty])
                starty += 1
                county -= 1
            
            if countx > 0:
                newList.append(self.text[startx])
                startx += 1
                countx -= 1
                
            if countx == 0 and county == 0:
                break
        
        newList.reverse()
        
        for i in range(0, actualCountx + actualCounty):
            self.text[i + actualStartx] = newList[i]
    
    def getnarg(self, idx):
        line = self.lines[self.lineIdx]
        inText = line[line.find("(")+1:line.find(")")]
        inTextSpl = inText.split(",")[idx]
        return int(inTextSpl)
    
    def getparg(self, idx):
        line = self.lines[self.lineIdx]
        inText = line[line.find("(")+1:line.find(")")].replace(" ", "")
        inTextSpl = inText.split(",")[idx]
        return int(inTextSpl[5:-1])
    
    def obf(self, num):
        esi = num
        ecx = num
        ecx <<= 6
        esi ^= ecx
        ecx = esi
        ecx = (ecx >> 8 << 8) | ((ecx & 0xff) >> 7)
        ecx ^= esi
        esi = ecx << 1
        ecx ^= esi
        return ecx & 0xff
    
    def step(self):
        line = self.lines[self.lineIdx]
        if line.startswith("abbaab_mix("):
            cx = self.getnarg(2)
            cy = self.getnarg(4)
            sx = self.getparg(1)
            sy = self.getparg(3)
            self.scramble(sx, cx, sy, cy)
        elif line.startswith("abbaabb_mul1("):
            val = self.getnarg(2)
            self.tmp0 = (val * 0x2f) & 0xff
        elif line.startswith("abbaabbo_xortext1("):
            a1 = self.getnarg(1)
            a4 = self.getnarg(4)
            if a1 == a4:
                self.lineIdx += 1
                return

            a3 = self.getparg(3)
            
            txt = self.text[a3 + a1]
            self.tmp0 ^= txt

        elif line.startswith("abbaabbob_encbyte("):
            self.tmp0 = self.obf(self.tmp0)
        elif line.startswith("abbaabboa("): # immediately after bbob
            a2 = self.getparg(2)
            a0 = self.getnarg(0)
            self.text[a2 + a0] = self.tmp0
        elif line.startswith("abbaabboc_mul2("):
            a4 = self.getnarg(4)
            self.tmp0 = (a4 * 0x33) & 0xff
        elif line.startswith("abbaabboco_xortext2("):
            a2 = self.getparg(2)
            a4 = self.getnarg(4)
            a1 = self.getnarg(1)
            if (a4 - 1 - a1) >= 0:
                self.tmp0 = self.tmp0 ^ self.text[a2 + (a4 - 1 - a1)]
            
        elif line.startswith("abbaabbocoa_setchar("):
            a1 = self.getparg(1)
            a2 = self.getnarg(2)
            a0 = self.getnarg(0)
            if (a2 - 1 - a0) >= 0:
                self.text[a1 + (a2 - 1 - a0)] = self.tmp0
        
        self.lineIdx += 1

sim = SimSim()
sim.loadText(sys.argv[1])

with open("cpsc_debug_output.txt") as file:
    lines = file.readlines()
    lines = [line.rstrip() for line in lines]

sim.start(lines)
print(bytes(sim.text).hex())