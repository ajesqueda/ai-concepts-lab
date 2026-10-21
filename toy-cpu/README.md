# Toy CPU: the fetch-decode-execute cycle

A ~100-line Python CPU that runs a C `while` loop as machine instructions and prints
every step. It makes visible what a processor does billions of times a second.

> Concept from BU CX651 (Computer Systems), Week 1.

## The idea

```c
int x = 3, y = 2;
while (x < 5) { x++; y += x; }
```

compiles to instructions sitting in memory, 4 bytes apart. The CPU keeps one special
register, the **program counter (PC)**, which holds the address of the next instruction.
Every cycle:

1. **Fetch:** read the instruction at the PC, then move the PC forward 4 bytes.
2. **Decode:** split it into an opcode and operands (`OPC dst, src`).
3. **Execute:** update a register, write memory, or overwrite the PC with a jump.

Machine code has no `while`. The loop is just `cmp` followed by a conditional jump
(`jge`) and an unconditional jump (`jmp`) that set the PC back to the check.

## Run it

```bash
python toy-cpu/toy_cpu.py
```

```
   PC  instruction         rax  rdi  next PC
0x020  mov rax, 3            3    0  0x024
0x024  mov rdi, 2            3    2  0x028
0x028  cmp rax, 5            3    2  0x02c
0x02c  jge 0x3c              3    2  0x030
0x030  add rax, 1            4    2  0x034
0x034  add rdi, rax          4    6  0x038
0x038  jmp 0x28              4    6  0x028   <- the loop is a jump back
...
0x02c  jge 0x3c              5   11  0x03c   <- x >= 5, exit the loop
0x03c  mov [0x100], rax      5   11  0x040
0x040  mov [0x104], rdi      5   11  0x044

memory: x = 5, y = 11
```

## Things worth noticing

- `mov` **copies**. The source register keeps its value.
- The PC moves forward *before* execute, so a jump only has to overwrite it.
- `rax` and `rdi` are just two of the CPU's ~16 general-purpose registers. ARM chips
  such as Apple's M series call theirs `x0`, `x1` and so on.

## Tests

```bash
pytest toy-cpu
```

The tests check that the result matches the C program (x = 5, y = 11), that the loop
body runs exactly twice, that the PC moves by 4 except on taken jumps, and that a
runaway loop is caught.
