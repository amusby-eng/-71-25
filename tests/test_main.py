
import subprocess
import sys


def test_exit():
    result = subprocess.run(
        [sys.executable, "src/main.py"],
        input="exit\n",
        text=True,
        capture_output=True
    )
    assert "Выход из программы" in result.stdout
