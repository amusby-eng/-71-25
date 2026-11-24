import unittest

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