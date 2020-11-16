print('Input a Number Below to guess how many bells Tom Nook has :)')
guess = None
try:
  guess = int(input())
except:
  print("No silly that is wrong, you need a number.")
  exit()
try:
    for tax3 in range(0,1234):
        guess -= 1337 + tax3
    guess = str(hex(int(guess)))[2:]; guess = str(guess[4:8]) + str(guess[0:4])
    guess = int(guess,16)
    for tax4 in range(18,30,2):
        guess = int((str(hex(guess)[2:])[::-1]),16) - tax4 * 1000
    for tax5 in range(0,1000,5):
        for tax4 in range(10,40,10):
            guess -= tax5 * tax4
    guess = str(hex(guess)[2:])
    guess = [int(guess[i:i+2],16) for i in range(0,len(guess),2)];guess[1] /= 2
    guess[0] *= 3;guess[1] -= 18;guess[3] -= 30
    guess[0] += int((ord('j') - ord('J')) / (ord('E') - ord('e')));guess[2] += ord('b')
    guess[0] += int((ord('g') - ord('G')) / (ord('z') - ord('Z')) * ord('c') - ord('a'))
    guess = [hex(int(g)) for g in guess][::-1]
    guess[3] = hex(int(guess[3],16) + 32)


    final = ''
    for i in range(len(guess)):
        final += chr(int(guess[i],16))


    if final == 'Lmao':
        print("Nice you got it, your flag is the value you initally got in the form 'uiuctf{NUMBER_YOU_GOT}'")
    else:
        print("Good try but your ending value was " + final + " try again <3")
        print("\n")
except:
    print("Your guess was so wrong you broke the guessing machine. Good try, but try again <3")
