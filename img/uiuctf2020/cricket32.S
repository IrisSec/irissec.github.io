// gcc -m32 cricket32.S -o cricket32

.text
str_usage: .string "Usage: ./cricket32 flag\nFlag is ascii with form uiuctf{...}\n"
str_yes:   .string "Flag is correct! Good job!\n"
str_nope:  .string "Flag is not correct.\n"

.global main
main:
mov $str_usage, %ebx
xor %esi, %esi
xor %edi, %edi
mov $2, %ecx
sub $0x10, (%esp, %ecx, 2)

push %ebp
mov %esp, %ebp
not %ebp
mov 12(%esp), %ecx
cmp $'W, (%ebx, %esi, 8)
xor %ebp, %ebp
rclb %cl, %dh
add $14, 8(%esp)
jnz 1f
aaa
aaa
aaa
decl %ebp
and $-1, %al
mov 4(%ecx), %esi
incl %ebp
mov (%esi, %ebp, 1), %al
xchgl %eax, %eax
mov $0x6cb4001b, %ebx
add %al, %al
jne .-12
jmp .+10

mov (%ecx, %ebx, 8), %esi
mov (%ebx, %ecx, 4), %esi
div %ah
sub $26, %ebp
mov %esp, %ebx
xlat
xlat
sahf
dec %ebp
mov %ah, %dh
jge .+15
orw $-1, %ax
lea (%edx, %ebp, 4), %ebp
jns .-7
lea (%eax), %eax
jl .+14
mov $8, %ecx
mov $.-'Z, %ebx
loop .+9
mov $str_nope, %ebx
jmp 1f

mov (%ebx), %dx
bswap %edx
mov 4(%ebx), %dx
xchg %dh, %dl
add $13, %ebx
crc32l (%esi), %edx
xor (%esi), %edx
or %edx, %edi
lahf
add $4, %esi
loop .-27
btc $14, %eax
mov $str_yes, %ebx
jnc .-'A;1:
pop %ebp
mov %ebx, 4(%esp)
jmp printf
