import unittest
from src.assembler import assemble_lines, encode_program

from src.assembler import assemble_lines


class TestAssembler(unittest.TestCase):
    def test_load_const(self):
        result = assemble_lines(["load_const r6, 15"])

        self.assertEqual(
            result,
            [{"A": 44, "B": 6, "C": 15}]
        )

    def test_read(self):
        result = assemble_lines(["read r20, r8"])

        self.assertEqual(
            result,
            [{"A": 33, "B": 20, "C": 8}]
        )

    def test_write(self):
        result = assemble_lines(["write r3, r8"])

        self.assertEqual(
            result,
            [{"A": 7, "B": 3, "C": 8}]
        )

    def test_abs(self):
        result = assemble_lines(["abs r23, 667, r29"])

        self.assertEqual(
            result,
            [{"A": 20, "B": 23, "C": 667, "D": 29}]
        )

    def test_encode_load_const(self):
        program = assemble_lines(["load_const r6, 15"])

        result = encode_program(program)

        self.assertEqual(
            result,
            bytes([0xAC, 0x79, 0x00, 0x00, 0x00])
        )

    def test_encode_read(self):
        program = assemble_lines(["read r20, r8"])

        result = encode_program(program)

        self.assertEqual(
            result,
            bytes([0x21, 0x45, 0x00, 0x00, 0x00])
        )

    def test_encode_write(self):
        program = assemble_lines(["write r3, r8"])

        result = encode_program(program)

        self.assertEqual(
            result,
            bytes([0xC7, 0x40, 0x00, 0x00, 0x00])
        )

    def test_encode_abs(self):
        program = assemble_lines(["abs r23, 667, r29"])

        result = encode_program(program)

        self.assertEqual(
            result,
            bytes([0xD4, 0xDD, 0x14, 0xE8, 0x00])
        )

    def test_unknown_command(self):
        with self.assertRaises(ValueError):
            assemble_lines(["unknown r1, 5"])

    def test_invalid_register(self):
        with self.assertRaises(ValueError):
            assemble_lines(["load_const r32, 15"])

    def test_missing_operands(self):
        with self.assertRaises(ValueError):
            assemble_lines(["load_const"])

    def test_empty_lines(self):
        result = assemble_lines(["", "; comment"])

        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()