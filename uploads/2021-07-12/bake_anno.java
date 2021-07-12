package net.redpwn.ctf;

import java.lang.reflect.Method;

public class JavaIsEZ3 {
    private static byte[] araragi = new byte[]{3, 88, 72, 7, 83, 3, 2, 70, 7, 70, 3, 43, 10, 46, 76, 3, 42, 0, 117, 5, 3, 9, 5, 113, 24, 3, 54, 24, 10, 28, 1, 0, 4, 1, 1, 4, 1, 2, 4, 1, 3, 4, 1, 4, 4, 1, 5, 4, 2};
    private static int[] hitagi = new int[]{1, 102, 214, 57, 24, 0, 118, 112, 88, 118, 107, 110, 50, 46, 0, 113, 67, 20, 106, 112, 110, 31, 33, 0, 109, 102, 121, 67, 57, 77, 57, 109, 17, 4, 17, 5, 17, 6, 17, 7, 5, 47, 3, 1, 17, 0, 19, 4, 0, 4, 7, 42, 4, 1, 5, 7, 42, 4, 2, 6, 7, 42, 4, 3, 7, 7, 42, 19};

    public JavaIsEZ3() {
        //redpwnCTF2021 var10000 = (redpwnCTF2021)null;
        super();
    }

    private static boolean oshino(char[][] inp) {
        //redpwnCTF2021 var10000 = (redpwnCTF2021)null;
        char[] inp1 = inp[1];
        String inp1Str = new String(inp1);
        if (inp1Str.hashCode() != 998474623) {
            return false;
        } else {
            int[] reg = new int[6];
            int j = 0;

            for (int i = 0; i < hachikuji(inp1); i += 4) {
                reg[j++] = (
                    inp1[i] << 24 |
                    inp1[i + 1] << 16 |
                    inp1[i + 2] << 8 |
                    inp1[i + 3]
                ) ^ 118818581;
            }

            int pos = 0;
            int[] stack = new int[15];
            int stackPos = 0;
            boolean retValue = true;

            while (true) {
                byte opcode = araragi[pos];
                byte var9;
                int var10;
                int var11;
                switch (opcode) {
                case 0: //pop into reg
                    var9 = araragi[pos + 1];
                    stackPos--;
                    reg[var9] = stack[stackPos];
                    pos += 2;
                    break;
                case 1: //push from reg
                    var9 = araragi[pos + 1];
                    stack[stackPos++] = reg[var9];
                    pos += 2;
                    break;
                case 2: //return
                    return retValue;
                case 3: //push int constant
                    var11 = araragi[pos + 1] << 24 | araragi[pos + 2] << 16 |
                            araragi[pos + 3] << 8 | araragi[pos + 4];
                    stack[stackPos++] = var11;
                    pos += 5;
                    break;
                case 4: //compare top two stack values
                    stackPos--;
                    var11 = stack[stackPos];
                    stackPos--;
                    var10 = stack[stackPos];
                    retValue &= var10 == var11;
                    pos++;
                    break;
                case 5: //push short constant
                    var11 = araragi[pos + 1] << 8 | araragi[pos + 2];
                    stack[stackPos++] = var11;
                    pos += 3;
                    break;
                case 6: //push byte constant
                    var9 = araragi[pos + 1];
                    stack[stackPos++] = var9;
                    pos += 2;
                }
            }
        }
        /*
        pushInt 0x58480753  (3, 88, 72, 7, 83)
        pushInt 0x02460746  (3, 2, 70, 7, 70)
        pushInt 0x2B0A2E4C  (3, 43, 10, 46, 76)
        pushInt 0x2A007505  (3, 42, 0, 117, 5)
        pushInt 0x09057118  (3, 9, 5, 113, 24)
        pushInt 0x36180A1C  (3, 54, 24, 10, 28)
        pushReg 0           (1, 0)
        compareStack        (4)
        pushReg 1           (1, 1)
        compareStack        (4)
        pushReg 2           (1, 2)
        compareStack        (4)
        pushReg 3           (1, 3)
        compareStack        (4)
        pushReg 4           (1, 4)
        compareStack        (4)
        pushReg 5           (1, 5)
        compareStack        (4)
        return              (2)
        */
    }

    private static boolean sengoku(char[][] inp) {
        //redpwnCTF2021 var10000 = (redpwnCTF2021)null;
        char[] inp2 = inp[2];
        long[] reg = new long[15];

        //hachikuji = array length

        int j = 0;
        for(int i = 0; i < inp2.hachikuji(); i += 8) {
            reg[j++] = (
                (long)inp2[i] << 56 | (long)inp2[i + 1] << 48 |
                (long)inp2[i + 2] << 40 | (long)inp2[i + 3] << 32 |
                (long)inp2[i + 4] << 24 | (long)inp2[i + 5] << 16 |
                (long)inp2[i + 6] << 8 | (long)inp2[i + 7]
            ) ^ 216743518893377301L;
        }

        String inp2Str = new String(inp2);
        reg[j] = (long)inp2Str.hashCode();
        int pos = 0;
        long[] stack = new long[15];
        int stackPos = 0;

        while (true) {
            int opcode = hitagi[pos];
            int var8;
            int var9;
            long var10;
            switch (opcode) {
            case 0: //push long constant
                var10 = (long)hitagi[pos + 1] << 56 | (long)hitagi[pos + 2] << 48 |
                        (long)hitagi[pos + 3] << 40 | (long)hitagi[pos + 4] << 32 |
                        (long)hitagi[pos + 5] << 24 | (long)hitagi[pos + 6] << 16 |
                        (long)hitagi[pos + 7] << 8 | (long)hitagi[pos + 8];
                stack[stackPos++] = var10;
                pos += 9;
                break;
            case 1: //push int constant
                var10 = (long)hitagi[pos + 1] << 24 | (long)hitagi[pos + 2] << 16 |
                        (long)hitagi[pos + 3] << 8 | (long)hitagi[pos + 4];
                stack[stackPos++] = var10;
                pos += 5;
                break;
            case 2: //push short constant
                var10 = (long)hitagi[pos + 1] << 8 | (long)hitagi[pos + 2];
                stack[stackPos++] = var10;
                pos += 3;
                break;
            case 3: //push byte constant
                var10 = (long)hitagi[pos + 1];
                stack[stackPos++] = var10;
                pos += 2;
                break;
            case 4: //reg a equals reg b
                var8 = hitagi[pos + 1];
                var9 = hitagi[pos + 2];
                reg[0] = reg[var8] == reg[var9] ? 0L : 1L;
                pos += 3;
                break;
            case 5: //jump
                pos = hitagi[pos + 1];
                break;
            case 6: //jump if eqz
                if (reg[0] == 0L) {
                    pos = hitagi[pos + 1];
                } else {
                    pos += 2;
                }
                break;
            case 7: //jump if neqz
                if (reg[0] != 0L) {
                    pos = hitagi[pos + 1];
                } else {
                    pos += 2;
                }
                break;
            case 8: //xor reg a and reg b
                var8 = hitagi[pos + 1];
                var9 = hitagi[pos + 2];
                reg[var8] ^= reg[var9];
                pos += 3;
                break;
            case 9: //or reg a and reg b
                var8 = hitagi[pos + 1];
                var9 = hitagi[pos + 2];
                reg[var8] |= reg[var9];
                pos += 3;
            case 16: //and reg a and reg b
                var8 = hitagi[pos + 1];
                var9 = hitagi[pos + 2];
                reg[var8] &= reg[var9];
                pos += 3;
                break;
            case 17: //pop into reg
                var8 = hitagi[pos + 1];
                --stackPos;
                reg[var8] = stack[stackPos];
                pos += 2;
                break;
            case 18: //push from reg
                var8 = hitagi[pos + 1];
                stack[stackPos++] = reg[var8];
                pos += 2;
                break;
            case 19: //return
                return reg[0] == 0L;
            default:
                break;
            }
        }
        /*
        pushInt 0x66D63918           (1, 102, 214, 57, 24)
        pushLong 0x767058766B6E322E  (0, 118, 112, 88, 118, 107, 110, 50, 46)
        pushLong 0x7143146A706E1F21  (0, 113, 67, 20, 106, 112, 110, 31, 33)
        pushLong 0x6D667943394D396D  (0, 109, 102, 121, 67, 57, 77, 57, 109)
        popIntoReg 4                 (17, 4)
        popIntoReg 5                 (17, 5)
        popIntoReg 6                 (17, 6)
        popIntoReg 7                 (17, 7)
        jmp label2                   (5, 47)

    label1:
        loadByte 1                   (3, 1)
        popIntoReg 0                 (17, 0)
        return                       (19)

    label2:
        cmp 0, 4                     (4, 0, 4)
        jmpNeq label1                (7, 42)
        cmp 1, 5                     (4, 1, 5)
        jmpNeq label1                (7, 42)
        cmp 2, 6                     (4, 2, 6)
        jmpNeq label1                (7, 42)
        cmp 3, 7                     (4, 3, 7)
        jmpNeq label1                (7, 42)
        return                       (19)
        */
    }

    private static void kanbaru(char[][] var0) {
        //redpwnCTF2021 var10000 = (redpwnCTF2021)null;

        for (int i = 0; i < hachikuji(var0) - 1; i++) {
            char[] var2 = var0[i];
            char[] var3 = var0[i + 1];

            for (int j = 0; j < hachikuji(var2); j++) {
                var3[j] ^= var2[j];
            }
        }

    }

    //get array length?
    public static int hachikuji(Object var0) {
        //redpwnCTF2021 var10000 = (redpwnCTF2021)null;

        try {
            String var4 = "java.lang.reflect.Array";
            Class var1 = var4.a<invokedynamic>(var4, "java.lang.Class", -2913566224361156927L); //forName
            Method var2 = var1.b<invokedynamic>(var1, "getLength", new Class[]{Object.class}, "java.lang.Class", -3289775410440245109L); //getDeclaredMethod
            var2.b<invokedynamic>(var2, true, "java.lang.reflect.Method", -2856230251947868740L); //setAccessible
            Integer var5 = (Integer)var2.b<invokedynamic>(var2, (Object)null, new Object[]{var0}, "java.lang.reflect.Method", -5083925746546271785L); //invoke
            return var5.b<invokedynamic>(var5, "java.lang.Integer", 2388217054567176175L); //intValue
        } catch (Throwable var3) {
            throw new RuntimeException(tetsujou.saisaki("宂棞客僗客梆", -454641250)); //idk never runs
        }
    }

    public static void main(String[] args) {
        redpwnCTF2021 var10000 = (redpwnCTF2021)null;
        if (hachikuji(args) == 0) {
            try {
                JOptionPane.showMessageDialog(null, "Silly-churl, billy-churl, silly-billy hilichurl... Woooh!\n~A certain Wangsheng Funeral Parlor director\n\n(This is not the flag, btw)");
            } catch (Throwable var5) {}
        } else {
            if (args[0].length() != 48) {
                System.out.println("*fanfare* You've been pranked!");
                return;
            }

            String walnut = "WalnutGirlBestGirl_07/15";
			char[] walArr = walnut.toCharArray();
			char[][] thrArr = new char[][]{walArr, null, null};
			int inpStrLen = args[0].length() / 2;

			for (int i = 0; i < 2; i++) {
				String subStr = args[0].substring(i * inpStrLen, (i + 1) * inpStrLen);
				thrArr[i+1] = subStr.toCharArray();
			}

			kanbaru(thrArr);
			if (oshino(thrArr) && sengoku(thrArr) && args[0].hashCode() == 1101317042) {
				System.out.println("Chute.  Now you know my secret");
			} else {
				System.out.println("*fanfare* You've been pranked!");
			}
        }

    }
}
 