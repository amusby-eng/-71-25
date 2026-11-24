"""Точка входа в интерпретатор виртуальной машины."""

import argparse
from pathlib import Path

from src.interpreter import execute_program, save_memory_dump


def main() -> None:
    """Запускает интерпретатор из командной строки."""
    parser = argparse.ArgumentParser(
        description="Интерпретатор учебной виртуальной машины"
    )
    parser.add_argument("input", help="Путь к бинарному файлу")
    parser.add_argument("output", help="Путь к CSV-файлу")
    parser.add_argument(
        "--start",
        type=int,
        required=True,
        help="Начальный адрес дампа"
    )
    parser.add_argument(
        "--end",
        type=int,
        required=True,
        help="Конечный адрес дампа"
    )

    args = parser.parse_args()

    try:
        machine_code = Path(args.input).read_bytes()

        memory = list(machine_code)
        memory.extend([0] * 1024)

        execute_program(machine_code, memory)

        save_memory_dump(
            memory,
            args.output,
            args.start,
            args.end
        )

    except (OSError, ValueError, IndexError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()

