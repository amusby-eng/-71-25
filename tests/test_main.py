
import subprocess #модуль для запуска других программ изнутри Python. Запустим main
import sys #дает доступ к переменным, которые использует сам интерпретатор Python. 


def test_exit():
    result = subprocess.run(
        [sys.executable,#это путь к тому python, который сейчас исполняет тест
          "src/main.py"],
        input="exit\n",
        text=True,
        capture_output=True
    )
    assert "Выход из программы" in result.stdout

def test_ls():
    result = subprocess.run(
        [sys.executable, "src/main.py"],
        input="ls\n",
        text=True,
        capture_output=True
    )

    assert "Desktop" in result.stdout
    assert "Documents" in result.stdout
    assert "Downloads" in result.stdout

def test_cd():
    result = subprocess.run(
       [sys.executable, "src/main.py"],
       input = "cd Documents",
       text = True,
        capture_output = True
    )
    assert "/usr/local/bin/python3/folders/Documents$" in result.stdout
