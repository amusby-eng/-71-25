import unittest
import os
import json


class TestProjectFiles(unittest.TestCase):
    """Тесты проверяют, что нужные файлы существуют."""

    def test_readme_exists(self):
        """Проверяем, что README.md есть."""
        path = os.path.join(os.path.dirname(__file__), '..', 'README.md')
        self.assertTrue(os.path.exists(path), "README.md не найден")

    def test_src_folder_exists(self):
        """Проверяем, что папка src есть."""
        path = os.path.join(os.path.dirname(__file__), '..', 'src')
        self.assertTrue(os.path.isdir(path), "Папка src не найдена")

    def test_main_py_exists(self):
        """Проверяем, что main.py есть в src."""
        path = os.path.join(os.path.dirname(__file__), '..', 'src', 'main.py')
        self.assertTrue(os.path.exists(path), "src/main.py не найден")

    def test_examples_json_exists(self):
        """Проверяем, что пример JSON есть."""
        path = os.path.join(os.path.dirname(__file__), '..', 'examples', 'repo.json')
        self.assertTrue(os.path.exists(path), "examples/repo.json не найден")

    def test_json_is_valid(self):
        """Проверяем, что JSON файл можно прочитать."""
        path = os.path.join(os.path.dirname(__file__), '..', 'examples', 'repo.json')
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Проверяем, что данные не пустые
        self.assertIsNotNone(data, "JSON файл пустой")


class TestBasicFunctions(unittest.TestCase):
    """Простые тесты функций программы."""

    def test_import_main(self):
        """Проверяем, что main.py можно импортировать."""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        try:
            import main
            self.assertTrue(True, "main.py импортирован успешно")
        except ImportError:
            self.fail("Не удалось импортировать main.py")


if __name__ == '__main__':
    unittest.main()