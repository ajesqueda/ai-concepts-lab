"""A toy CPU that runs a tiny x86-flavored assembly program one step at a time.

The point is to make the fetch-decode-execute cycle visible:

    fetch   - read the instruction at the address in the program counter (PC)
    decode  - split it into an opcode and its operands
    execute - change a register, a memory cell, or the PC itself

Run it to watch a C `while` loop execute as machine instructions:

    python toy_cpu.py
"""

from __future__ import annotations

from dataclasses import dataclass, field

INSTRUCTION_SIZE = 4  # every instruction takes 4 bytes, so the PC moves by 4


@dataclass(frozen=True)
class Instruction:
    opcode: str
    dst: str
    src: str | None = None

    def __str__(self) -> str:
        return f"{self.opcode} {self.dst}" + (f", {self.src}" if self.src else "")


@dataclass
class Step:
    """A snapshot taken after one instruction finished, for printing a trace."""

    pc: int
    instruction: Instruction
    registers: dict[str, int]
    next_pc: int


@dataclass
class CPU:
    program: dict[int, Instruction]
    pc: int
    registers: dict[str, int] = field(default_factory=lambda: {"rax": 0, "rdi": 0})
    memory: dict[int, int] = field(default_factory=dict)
    # Result of the last `cmp`: negative, zero or positive (dst - src).
    # Real CPUs keep this as individual flag bits; one number is enough here.
    compare_result: int = 0

    def read(self, operand: str) -> int:
        """Resolve an operand to a value: a register name or an immediate number."""
        if operand in self.registers:
            return self.registers[operand]
        return int(operand, 0)  # base 0 accepts both "3" and "0x3c"

    def step(self) -> Step:
        start_pc = self.pc

        # Fetch: the PC is just an address; whatever sits there is the next instruction.
        instruction = self.program[self.pc]
        # The PC advances *before* execute. Jumps then simply overwrite it.
        self.pc += INSTRUCTION_SIZE

        # Decode + execute. Decoding is trivial here because the instruction
        # is already split into opcode/dst/src; a real CPU decodes bit fields.
        op, dst, src = instruction.opcode, instruction.dst, instruction.src
        if op == "mov":
            if dst.startswith("["):
                # `mov [0x100], rax` stores a register into memory.
                self.memory[int(dst.strip("[]"), 0)] = self.read(src)
            else:
                # `mov` copies; the source keeps its value.
                self.registers[dst] = self.read(src)
        elif op == "add":
            self.registers[dst] += self.read(src)  # the ALU's job
        elif op == "cmp":
            self.compare_result = self.read(dst) - self.read(src)
        elif op == "jge":
            if self.compare_result >= 0:
                self.pc = int(dst, 0)
        elif op == "jmp":
            self.pc = int(dst, 0)
        else:
            raise ValueError(f"unknown opcode: {op}")

        return Step(start_pc, instruction, dict(self.registers), self.pc)

    def run(self, max_steps: int = 1_000) -> list[Step]:
        """Run until the PC walks off the end of the program."""
        trace: list[Step] = []
        while self.pc in self.program:
            if len(trace) >= max_steps:
                raise RuntimeError("step limit reached; is there an infinite loop?")
            trace.append(self.step())
        return trace


def assemble(source: str, origin: int = 0x20) -> dict[int, Instruction]:
    """Turn assembly text into {address: Instruction}, 4 bytes per instruction."""
    program: dict[int, Instruction] = {}
    address = origin
    for raw in source.splitlines():
        line = raw.split(";")[0].strip()  # drop comments
        if not line:
            continue
        opcode, _, rest = line.partition(" ")
        operands = [part.strip() for part in rest.split(",")]
        program[address] = Instruction(opcode, *operands)
        address += INSTRUCTION_SIZE
    return program


# The compiled form of:
#     int x = 3; int y = 2;
#     while (x < 5) { x++; y += x; }
# There is no `while` in machine code; the loop is a compare plus two jumps.
WHILE_LOOP = """
mov rax, 3        ; x = 3
mov rdi, 2        ; y = 2
cmp rax, 5        ; 0x28: compare x with 5
jge 0x3c          ; leave the loop once x >= 5
add rax, 1        ; x++
add rdi, rax      ; y += x
jmp 0x28          ; back to the check
mov [0x100], rax  ; 0x3c: store x
mov [0x104], rdi  ; store y
"""


def main() -> None:
    cpu = CPU(program=assemble(WHILE_LOOP), pc=0x20)
    print(f"{'PC':>5}  {'instruction':<18} {'rax':>4} {'rdi':>4}  next PC")
    for step in cpu.run():
        print(
            f"{step.pc:#05x}  {str(step.instruction):<18} "
            f"{step.registers['rax']:>4} {step.registers['rdi']:>4}  {step.next_pc:#05x}"
        )
    print(f"\nmemory: x = {cpu.memory[0x100]}, y = {cpu.memory[0x104]}")


if __name__ == "__main__":
    main()
