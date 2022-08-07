import gdb

#gdbpy start
offAddress = 0

def setBreakEvent(callback, addr, inst=None):
    class GdbBreakpoint(gdb.Breakpoint):
        def __init__(self, callback, addr, inst):
            global offAddress
            super(GdbBreakpoint, self).__init__("*" + hex(addr + offAddress), type=gdb.BP_BREAKPOINT, internal=False)
            self.callback = callback
            self.inst = inst
            
        def stop(self):
            pos = readReg("rip")
            res = None
            if inst == None:
                res = self.callback(pos)
            else:
                res = self.callback(inst, pos)
            
            if res == True:
                return res
            else:
                return False
            
    GdbBreakpoint(callback, addr, inst)

def getEntryPoint():
    ENTRY_POINT_STR = "\tEntry point: "
    fileInfo = gdb.execute("info file", to_string=True)
    infoLines = fileInfo.splitlines()
    for line in infoLines:
        if line.startswith(ENTRY_POINT_STR):
            entryPoint = int(line[len(ENTRY_POINT_STR):],0)
            return entryPoint
    
    return None

def readReg(reg):
    gdbValue = gdb.selected_frame().read_register(reg)
    return int(gdbValue.cast(gdb.lookup_type("long")))

def readRegMem(reg, type, off=0):
    gdbValue = gdb.selected_frame().read_register(reg)
    pointer = gdbValue.cast(gdb.lookup_type("long"))
    gdbValue = gdb.Value(pointer + off)
    return int(gdbValue.cast(gdb.lookup_type(type).pointer()).referenced_value())

def readRegMem1(reg, off=0):
    return readRegMem(reg, "unsigned char", off)

def readRegMem4(reg, off=0):
    return readRegMem(reg, "int", off)

def readRegMem8(reg, off=0):
    return readRegMem(reg, "long", off)

def readRegStr(reg):
    gdbValue = gdb.selected_frame().read_register(reg)
    gdbValue = gdbValue.cast(gdb.lookup_type("char").pointer())
    return gdbValue.string()
    
def writeReg(reg, value):
    gdb.execute("set $" + reg + "=" + str(value))
#gdbpy end

dataStart = 0

def setDataStart(addr):
    global dataStart
    dataStart = readReg("rbx")

def logABB(addr):
    global dataStart
    arg0 = readRegMem8('rdx') - dataStart
    arg1 = readRegMem8('rdx', 0x8)
    arg2 = readRegMem4('rdx', 0x10)
    print(f"abb(data[{arg0}], {arg1}, {arg2})")

def logCall(info, addr):
    global dataStart
    name = info[0]
    reg = info[1]
    argValues = []
    for i in range(len(info) - 2):
        if info[i+2] == 0: # data pointer
            argValue = readRegMem8(reg, i * 8)
            if argValue != 0:
                arg = f"data[{argValue - dataStart}]"
            else:
                arg = f"{argValue}"
            
            argValues.append(arg)
        elif info[i+2] == 8: # qword
            arg = f"{readRegMem8(reg, i * 8)}"
            argValues.append(arg)
        elif info[i+2] == 4: # dword
            arg = f"{readRegMem4(reg, i * 8)}"
            argValues.append(arg)
        elif info[i+2] == 1: # byte
            arg = f"{readRegMem1(reg, i * 8)}"
            argValues.append(arg)
    
    res = name + "(" + ", ".join(argValues) + ")"
    print(res)

    return False

gdb.execute("set print addr off")
gdb.execute("set pagination off")
gdb.execute("set disassembly-flavor intel")

gdb.execute(f"file cpsc", False)
fileAddress = getEntryPoint()
gdb.execute("starti")
offAddress = getEntryPoint() - fileAddress

setBreakEvent(setDataStart, 0x26b7)

setBreakEvent(logCall, 0x2d3b, ["a", "rdx", 0,8,8,8,0])
setBreakEvent(logCall, 0x2892, ["aa", "rax", 0,8,8,8,0])
setBreakEvent(logCall, 0x2e9a, ["ab", "rdx", 0,8,8])
setBreakEvent(logCall, 0x2970, ["aba", ""])
setBreakEvent(logCall, 0x34b3, ["abb", "rdx", 0,8,4])
setBreakEvent(logCall, 0x2fc9, ["abba", "rdx", 8,8,8,0,4])
setBreakEvent(logCall, 0x313c, ["abbaa", "rdx", 8,8,8,0,4])
setBreakEvent(logCall, 0x2980, ["abbaaa", ""])
setBreakEvent(logCall, 0x3299, ["abbaab_mix", "rax", 0,0,8,0,8,8,4])
setBreakEvent(logCall, 0x2940, ["abbaaba", ""])
setBreakEvent(logCall, 0x2a8c, ["abbaabb_mul1", "rcx", 0,8,4])
setBreakEvent(logCall, 0x364c, ["abbaabbo_xortext1", "rdx", 1,8,8,0,8,0,4])
setBreakEvent(logCall, 0x2c44, ["abbaabboa", "rdx", 1,8,0,8,8,0,4])
setBreakEvent(logCall, 0x283c, ["abbaabbob_encbyte", ""])
setBreakEvent(logCall, 0x29b8, ["abbaabboc_mul2", "rdx", 8,8,0,8,8])
setBreakEvent(logCall, 0x3878, ["abbaabboco_xortext2", "rdx", 8,8,0,8,8])
setBreakEvent(logCall, 0x2b62, ["abbaabbocoa_setchar", "rdx", 8,0,8,8,1])
setBreakEvent(logCall, 0x2860, ["abbaabbococ", ""])

gdb.execute("c")