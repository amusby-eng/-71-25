
"""Тесты интерпретатора виртуальной машины."""

import csv
import tempfile
import unittest
from pathlib import Path

from src.assembler import assemble_lines, encode_program
from src.interpreter import (
    decode_instruction,
    decode_program,
    execute_program,
    save_memory_dump,
)


INSTRUCTION_SIZE = 5


class TestInterpreter(unittest.TestCase):
    """Проверяет работу интерпретатора."""

    def test_decode_load_const(self):
        data = bytes([0xAC, 0x79, 0x00, 0x00, 0x00])
        result = decode_instruction(data)

        self.assertEqual(
            result,
            {"A": 44, "B": 6, "C": 15}
        )

    def test_decode_read(self):
        data = bytes([0x21, 0x45, 0x00, 0x00, 0x00])
        result = decode_instruction(data)

        self.assertEqual(
            result,
            {"A": 33, "B": 20, "C": 8}
        )

    def test_decode_write(self):
        data = bytes([0xC7, 0x40, 0x00, 0x00, 0x00])
        result = decode_instruction(data)

        self.assertEqual(
            result,
            {"A": 7, "B": 3, "C": 8}
        )

    def test_decode_abs(self):
        data = bytes([0xD4, 0xDD, 0x14, 0xE8, 0x00])
        result = decode_instruction(data)

        self.assertEqual(
            result,
            {"A": 20, "B": 23, "C": 667, "D": 29}
        )

    def test_invalid_instruction_size(self):
        with self.assertRaises(ValueError):
            decode_instruction(bytes([1, 2, 3]))

    def test_invalid_program_size(self):
        with self.assertRaises(ValueError):
            decode_program(bytes([1, 2, 3]))

    def test_copy_array(self):
        lines = [
            "load_const r20, 30",
            "read r20, r8",
            "load_const r21, 40",
            "write r8, r21",
        ]

        program = assemble_lines(lines)
        machine_code = encode_program(program)

        memory = list(machine_code)
        memory.extend([0] * 100)

        memory[30] = 123

        execute_program(machine_code, memory)

        self.assertEqual(memory[40], 123)

    def test_save_memory_dump(self):
        memory = [10, 20, 30, 40, 50]

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "memory.csv"

            save_memory_dump(
                memory,
                str(path),
                1,
                3
            )

            with path.open(
                encoding="utf-8",
                newline=""
            ) as file:
                rows = list(csv.reader(file))

        self.assertEqual(
            rows,
            [
                ["address", "value"],
                ["1", "20"],
                ["2", "30"],
                ["3", "40"],
            ]
        )


if __name__ == "__main__":
    unittest.main()
