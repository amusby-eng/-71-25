
"""Модуль ассемблера учебной виртуальной машины."""

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

LOAD_OPERANDS_COUNT = 2
MEMORY_OPERANDS_COUNT = 2
ABS_OPERANDS_COUNT = 3

INSTRUCTIONS = {
    "load_const": LOAD_CONST_OPCODE,
    "read": READ_OPCODE,
    "write": WRITE_OPCODE,
    "abs": ABS_OPCODE,
}


def parse_register(value: str) -> int:
    """Проверяет запись регистра и возвращает его номер."""
    if not value.startswith("r") or not value[1:].isdigit():
        raise ValueError(f"Некорректный регистр: {value}")

    register = int(value[1:])

    if register >= REGISTER_COUNT:
        raise ValueError(f"Регистр вне диапазона: {value}")

    return register


def parse_number(value: str, max_bits: int) -> int:
    """Проверяет число на соответствие заданной разрядности."""
    try:
        number = int(value, 0)
    except ValueError:
        raise ValueError(f"Некорректное число: {value}") from None

    if number < 0 or number >= 2 ** max_bits:
        raise ValueError(f"Число вне допустимого диапазона: {value}")

    return number


def parse_instruction(line: str) -> dict:
    """Преобразует строку ассемблера в набор полей команды."""
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

    if command == "load_const":
        if len(operands) != LOAD_OPERANDS_COUNT:
            raise ValueError("load_const требует 2 операнда")

        return {
            "A": LOAD_CONST_OPCODE,
            "B": parse_register(operands[0]),
            "C": parse_number(operands[1], CONSTANT_BITS),
        }

    if command in ("read", "write"):
        if len(operands) != MEMORY_OPERANDS_COUNT:
            raise ValueError(f"{command} требует 2 операнда")

        return {
            "A": INSTRUCTIONS[command],
            "B": parse_register(operands[0]),
            "C": parse_register(operands[1]),
        }

    if command == "abs":
        if len(operands) != ABS_OPERANDS_COUNT:
            raise ValueError("abs требует 3 операнда")

        return {
            "A": ABS_OPCODE,
            "B": parse_register(operands[0]),
            "C": parse_number(operands[1], OFFSET_BITS),
            "D": parse_register(operands[2]),
        }

    raise ValueError(f"Неизвестная команда: {command}")

def assemble_lines(lines: list[str]) -> list[dict[str, int]]:
    """Преобразует список строк в промежуточное представление."""
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
import argparse
from pathlib import Path


def main():
    """Запускает ассемблер из командной строки."""
    parser = argparse.ArgumentParser(
        description="Ассемблер учебной виртуальной машины"
    )
    parser.add_argument("input", help="Путь к исходной программе")
    parser.add_argument("output", help="Путь к выходному бинарному файлу")
    parser.add_argument(
        "--test",
        action="store_true",
        help="Вывести промежуточное представление"
    )

    args = parser.parse_args()

    try:
        lines = Path(args.input).read_text(encoding="utf-8").splitlines()
        program = assemble_lines(lines)
    except (OSError, ValueError) as error:
        parser.error(str(error))

    if args.test:
        for instruction in program:
            print(instruction)
    else:
        print("Промежуточное представление:")
        for instruction in program:
            print(instruction)


if __name__ == "__main__":
    main()