class SimSim:
    def start(self, lines):
        self.lines = lines
        self.lineIdx = 0
        self.tmp0 = 0
        self.indmap = {}
        self.text_indices = [i for i in range(43)]

        for i in range(43):
            print(f"text{i}_0 = self.text[{i}]")

        while True:
            self.step()
            if self.lineIdx >= len(self.lines):
                break
        
        # uncomment this to generate reorder_table
        #print(self.text_indices)

        print("newarr = [")
        for i in range(43):
            print(f"    {self.getvar('text' + str(i))},")
        
        print("]")
    
    def scramble_indices(self, startx, countx, starty, county):
        potato = []
        actualStartx = startx
        actualCountx = countx
        actualCounty = county
        while True:
            if county > 0:
                potato.append(self.text_indices[starty])
                starty += 1
                county -= 1
            
            if countx > 0:
                potato.append(self.text_indices[startx])
                startx += 1
                countx -= 1
                
            if countx == 0 and county == 0:
                break
        
        potato.reverse()
        
        for i in range(0, actualCountx+actualCounty):
            self.text_indices[i+actualStartx] = potato[i]
    
    # get nth argument (regular number)
    def getnarg(self, idx):
        line = self.lines[self.lineIdx]
        inText = line[line.find("(")+1:line.find(")")]
        inTextSpl = inText.split(",")[idx]
        return int(inTextSpl)
    
    # get nth pointer argument (data[XXX])
    def getparg(self, idx):
        line = self.lines[self.lineIdx]
        inText = line[line.find("(")+1:line.find(")")].replace(" ", "")
        inTextSpl = inText.split(",")[idx]
        return int(inTextSpl[5:-1])

    def getnextvar(self, name):
        if name in self.indmap:
            return name + "_" + str(self.indmap[name] + 1)
        else:
            self.indmap[name] = 0
            return name + "_1"

    def getvar(self, name):
        if name in self.indmap:
            return name + "_" + str(self.indmap[name])
        else:
            self.indmap[name] = 0
            return name + "_0"

    def incvar(self, name):
        if name in self.indmap:
            self.indmap[name] += 1
        else:
            self.indmap[name] = 1
    
    def step(self):
        line = self.lines[self.lineIdx]
        if line.startswith("abbaab_mix("):
            cx = self.getnarg(2)
            cy = self.getnarg(4)
            sx = self.getparg(1)
            sy = self.getparg(3)
            self.scramble_indices(sx, cx, sy, cy)
        elif line.startswith("abbaabb_mul1("):
            val = self.getnarg(2)

            value = (val * 0x2f) & 0xff
            print(f"{self.getnextvar('tmp0')} = {value}")
            self.incvar('tmp0')
            
        elif line.startswith("abbaabbo_xortext1("):
            a1 = self.getnarg(1)
            a4 = self.getnarg(4)
            if a1 == a4:
                self.lineIdx += 1
                return

            a3 = self.getparg(3)
            
            index = self.text_indices[a3+a1]
            print(f"{self.getnextvar('tmp0')} = {self.getvar('tmp0')} ^ {self.getvar('text' + str(index))}")
            self.incvar('tmp0')

        elif line.startswith("abbaabbob_encbyte("):
            print(f"{self.getnextvar('tmp0')} = self.encrypt({self.getvar('tmp0')})")
            self.incvar('tmp0')
            
        elif line.startswith("abbaabboa("):
            a2 = self.getparg(2)
            a0 = self.getnarg(0)

            index = self.text_indices[a2 + a0]
            print(f"{self.getnextvar('text' + str(index))} = {self.getvar('tmp0')}")
            self.incvar('text' + str(index))
            
        elif line.startswith("abbaabboc_mul2("):
            a4 = self.getnarg(4)

            value = (a4 * 0x33) & 0xff
            print(f"{self.getnextvar('tmp0')} = {value}")
            self.incvar('tmp0')
            
        elif line.startswith("abbaabboco_xortext2("):
            a2 = self.getparg(2)
            a4 = self.getnarg(4)
            a1 = self.getnarg(1)
            
            idk = a4 - 1 - a1
            # any -1 result here will be discarded anyway, let's not confuse z3
            if idk >= 0:
                index = self.text_indices[a2 + idk]
                print(f"{self.getnextvar('tmp0')} = {self.getvar('tmp0')} ^ {self.getvar('text' + str(index))}")
                self.incvar('tmp0')
            
        elif line.startswith("abbaabbocoa_setchar("):
            a1 = self.getparg(1)
            a2 = self.getnarg(2)
            a0 = self.getnarg(0)

            idk = a2 - 1 - a0
            # any -1 result here will be discarded anyway, let's not confuse z3
            if idk >= 0:
                index = self.text_indices[a1 + idk]
                print(f"{self.getnextvar('text' + str(index))} = {self.getvar('tmp0')}")
                self.incvar('text' + str(index))
        
        self.lineIdx += 1

sim = SimSim()

with open("cpsc_debug_output.txt") as file:
    lines = file.readlines()
    lines = [line.rstrip() for line in lines]


sim.start(lines)