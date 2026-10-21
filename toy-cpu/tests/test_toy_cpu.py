import pytest
from toy_cpu import CPU, WHILE_LOOP, Instruction, assemble


def run_while_loop() -> tuple[CPU, list]:
    cpu = CPU(program=assemble(WHILE_LOOP), pc=0x20)
    return cpu, cpu.run()


def test_assembler_places_instructions_four_bytes_apart():
    program = assemble(WHILE_LOOP)
    assert sorted(program) == list(range(0x20, 0x44, 4))
    assert program[0x2C] == Instruction("jge", "0x3c")


def test_while_loop_matches_the_c_program():
    # Same as running the C code: x goes 3 -> 4 -> 5, y goes 2 -> 6 -> 11.
    cpu, _ = run_while_loop()
    assert cpu.memory == {0x100: 5, 0x104: 11}


def test_loop_body_runs_twice():
    _, trace = run_while_loop()
    body = [s for s in trace if s.instruction.opcode == "add" and s.instruction.dst == "rax"]
    assert len(body) == 2
    # 2 setup + 2 iterations x 5 instructions + final cmp/jge + 2 stores
    assert len(trace) == 2 + 2 * 5 + 2 + 2


def test_pc_advances_by_four_unless_a_jump_is_taken():
    _, trace = run_while_loop()
    for step in trace:
        if step.instruction.opcode in {"jmp", "jge"} and step.next_pc != step.pc + 4:
            assert step.next_pc in {0x28, 0x3C}
        else:
            assert step.next_pc == step.pc + 4


def test_mov_copies_instead_of_moving():
    cpu = CPU(program=assemble("mov rax, 7\nmov rdi, rax"), pc=0x20)
    cpu.run()
    assert cpu.registers == {"rax": 7, "rdi": 7}


def test_unknown_opcode_is_rejected():
    cpu = CPU(program=assemble("nop rax"), pc=0x20)
    with pytest.raises(ValueError, match="unknown opcode"):
        cpu.run()


def test_infinite_loop_hits_step_limit():
    cpu = CPU(program=assemble("jmp 0x20"), pc=0x20)
    with pytest.raises(RuntimeError, match="step limit"):
        cpu.run(max_steps=50)
