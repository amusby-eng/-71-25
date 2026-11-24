
"""Ассемблер учебной виртуальной машины."""

import argparse
from pathlib import Path


LOAD_CONST_OPCODE = 44
READ_OPCODE = 33
WRITE_OPCODE = 7
ABS_OPCODE = 20

INSTRUCTION_SIZE = 5
REGISTER_COUNT = 32

OPCODE_BITS = 6
REGISTER_BITS = 5
CONSTANT_BITS = 28
OFFSET_BITS = 16

C_SHIFT = OPCODE_BITS + REGISTER_BITS
D_SHIFT = C_SHIFT + OFFSET_BITS

LOAD_OPERANDS_COUNT = 2
MEMORY_OPERANDS_COUNT = 2
ABS_OPERANDS_COUNT = 3

MIN_VALUE = 0

INSTRUCTIONS = {
    "load_const": LOAD_CONST_OPCODE,
    "read": READ_OPCODE,
    "write": WRITE_OPCODE,
    "abs": ABS_OPCODE,
}


def parse_register(value: str) -> int:
    """Проверяет регистр."""
    if not value.startswith("r") or not value[1:].isdigit():
        raise ValueError(f"Некорректный регистр: {value}")

    register = int(value[1:])

    if register >= REGISTER_COUNT:
        raise ValueError(
            f"Регистр вне диапазона: {value}"
        )

    return register


def parse_number(value: str, max_bits: int) -> int:
    """Проверяет разрядность числа."""
    try:
        number = int(value, 0)
    except ValueError:
        raise ValueError(
            f"Некорректное число: {value}"
        ) from None

    if number < MIN_VALUE or number >= 2 ** max_bits:
        raise ValueError(
            f"Вне допустимого диапазона: {value}"
        )

    return number


def parse_load_const(operands: list[str]) -> dict[str, int]:
    """Разбирает команду загрузки константы."""
    if len(operands) != LOAD_OPERANDS_COUNT:
        raise ValueError(
    "load_const требует 2 операнда"
)

    return {
        "A": LOAD_CONST_OPCODE,
        "B": parse_register(operands[0]),
        "C": parse_number(operands[1], CONSTANT_BITS),
    }


def parse_memory_command(
    command: str,
    operands: list[str]
) -> dict[str, int]:
    """Разбирает команды работы с памятью."""
    if len(operands) != MEMORY_OPERANDS_COUNT:
        raise ValueError(f"{command} требует 2 операнда")

    return {
        "A": INSTRUCTIONS[command],
        "B": parse_register(operands[0]),
        "C": parse_register(operands[1]),
    }


def parse_abs(operands: list[str]) -> dict[str, int]:
    """Разбирает команду abs."""
    if len(operands) != ABS_OPERANDS_COUNT:
        raise ValueError("abs требует 3 операнда")

    return {
        "A": ABS_OPCODE,
        "B": parse_register(operands[0]),
        "C": parse_number(operands[1], OFFSET_BITS),
        "D": parse_register(operands[2]),
    }


def parse_instruction(line: str) -> dict[str, int]:
    """Преобразует строку в поля команды."""
    line = line.split(";", maxsplit=1)[0].strip()

    if not line:
        return {}

    parts = line.split(maxsplit=1)
    command = parts[0]

    if command not in INSTRUCTIONS:
        raise ValueError(f"Неизвестная команда: {command}")

    if len(parts) != 2:
        raise ValueError(f"Отсутствуют операнды: {command}")

    operands = [item.strip() for item in parts[1].split(",")]

    parsers = {
        "load_const": parse_load_const,
        "read": lambda values: parse_memory_command(
            "read", values
        ),
        "write": lambda values: parse_memory_command(
            "write", values
        ),
        "abs": parse_abs,
    }

    return parsers[command](operands)


def assemble_lines(lines: list[str]) -> list[dict[str, int]]:
    """Создает промежуточное представление."""
    program = []

    for line_number, line in enumerate(lines, start=1):
        try:
            instruction = parse_instruction(line)
        except ValueError as error:
            raise ValueError(
                f"Ошибка в строке {line_number}: {error}"
            ) from None

        if instruction:
            program.append(instruction)

    return program


def encode_instruction(instruction: dict[str, int]) -> bytes:
    """Кодирует команду в пять байтов."""
    value = instruction["A"]
    value |= instruction["B"] << OPCODE_BITS
    value |= instruction["C"] << C_SHIFT

    if "D" in instruction:
        value |= instruction["D"] << D_SHIFT

    return value.to_bytes(
        INSTRUCTION_SIZE,
        byteorder="little"
    )


def encode_program(program: list[dict[str, int]]) -> bytes:
    """Кодирует программу в байты."""
    machine_code = bytearray()

    for instruction in program:
        machine_code.extend(encode_instruction(instruction))

    return bytes(machine_code)


def print_ir(program: list[dict[str, int]]) -> None:
    """Выводит промежуточное представление."""
    print("Промежуточное представление:")

    for instruction in program:
        print(instruction)


def print_machine_code(machine_code: bytes) -> None:
    """Выводит машинный код в формате hex."""
    print("Машинный код:")

    for index in range(0, len(machine_code), INSTRUCTION_SIZE):
        instruction = machine_code[
            index:index + INSTRUCTION_SIZE
        ]
        formatted = ", ".join(
            f"0x{byte:02X}" for byte in instruction
        )
        print(formatted)


def main() -> None:
    """Запускает ассемблер."""
    parser = argparse.ArgumentParser(
        description="Ассемблер виртуальной машины"
    )
    parser.add_argument(
        "input",
        help="Путь к исходной программе"
    )
    parser.add_argument(
        "output",
        help="Путь к бинарному файлу"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Вывести IR и машинный код"
    )

    args = parser.parse_args()

    try:
        lines = Path(args.input).read_text(
            encoding="utf-8"
        ).splitlines()
        program = assemble_lines(lines)
        machine_code = encode_program(program)

        Path(args.output).write_bytes(machine_code)

    except (OSError, ValueError) as error:
        parser.error(str(error))

    print_ir(program)

    if args.test:
        print_machine_code(machine_code)

    print(
    f"Размер машинного кода: {len(machine_code)} байт"
)


if __name__ == "__main__":
    main()
