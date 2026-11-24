"""Интерпретатор учебной виртуальной машины."""

import csv


INSTRUCTION_SIZE = 5

LOAD_CONST_OPCODE = 44
READ_OPCODE = 33
WRITE_OPCODE = 7
ABS_OPCODE = 20

VALID_OPCODES = (
    LOAD_CONST_OPCODE,
    READ_OPCODE,
    WRITE_OPCODE,
    ABS_OPCODE,
)

OPCODE_BITS = 6
REGISTER_BITS = 5
CONSTANT_BITS = 28
OFFSET_BITS = 16

C_SHIFT = OPCODE_BITS + REGISTER_BITS
D_SHIFT = C_SHIFT + OFFSET_BITS

OPCODE_MASK = (1 << OPCODE_BITS) - 1
REGISTER_MASK = (1 << REGISTER_BITS) - 1
CONSTANT_MASK = (1 << CONSTANT_BITS) - 1
OFFSET_MASK = (1 << OFFSET_BITS) - 1


def decode_instruction(data: bytes) -> dict[str, int]:
    """Декодирует одну пятибайтовую инструкцию."""
    if len(data) != INSTRUCTION_SIZE:
        raise ValueError("Неверный размер инструкции")

    value = int.from_bytes(data, byteorder="little")

    opcode = value & OPCODE_MASK

    if opcode not in VALID_OPCODES:
        raise ValueError(f"Неизвестная команда: {opcode}")

    register_b = (value >> OPCODE_BITS) & REGISTER_MASK
    field_c = (value >> C_SHIFT) & CONSTANT_MASK

    instruction = {
        "A": opcode,
        "B": register_b,
        "C": field_c,
    }

    if opcode == ABS_OPCODE:
        instruction["C"] &= OFFSET_MASK
        instruction["D"] = (value >> D_SHIFT) & REGISTER_MASK

    elif opcode in (READ_OPCODE, WRITE_OPCODE):
        instruction["C"] &= REGISTER_MASK

    return instruction


def decode_program(machine_code: bytes) -> list[dict[str, int]]:
    """Декодирует машинный код в список инструкций."""
    if len(machine_code) % INSTRUCTION_SIZE != 0:
        raise ValueError("Размер программы не кратен 5 байтам")

    program = []

    for index in range(0, len(machine_code), INSTRUCTION_SIZE):
        data = machine_code[index:index + INSTRUCTION_SIZE]
        program.append(decode_instruction(data))

    return program


def execute_program(
    machine_code: bytes,
    memory: list[int]
) -> None:
    """Выполняет команды виртуальной машины."""
    program = decode_program(machine_code)

    for instruction in program:
        opcode = instruction["A"]
        register_b = instruction["B"]
        field_c = instruction["C"]

        if opcode == LOAD_CONST_OPCODE:
            memory[register_b] = field_c

        elif opcode == READ_OPCODE:
            address = memory[register_b]
            memory[field_c] = memory[address]

        elif opcode == WRITE_OPCODE:
            address = memory[field_c]
            memory[address] = memory[register_b]


def save_memory_dump(
    memory: list[int],
    output_path: str,
    start: int,
    end: int
) -> None:
    """Сохраняет указанный диапазон памяти в CSV."""
    if start < 0 or end < start or end >= len(memory):
        raise ValueError("Некорректный диапазон памяти")

    with open(output_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["address", "value"])

        for address in range(start, end + 1):
            writer.writerow([address, memory[address]])

