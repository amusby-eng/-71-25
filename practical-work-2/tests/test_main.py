import json
import pytest

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from main import (
    read_test_repository,
    dfs,
    find_reverse_dependencies,
    print_ascii_tree,
    create_graph_image
)


# Тест чтения тестового репозитория
def test_read_test_repository(tmp_path):
    file = tmp_path / "repo.json"
    file.write_text('{"A": ["B"], "B": []}', encoding="utf-8")

    result = read_test_repository(file)

    assert result == {"A": ["B"], "B": []}


# Тест построения графа зависимостей
def test_dfs():
    repository = {
        "A": ["B", "C"],
        "B": ["D"],
        "C": ["A"],
        "D": []
    }

    result = dfs("A", repository, True, 3, "")

    assert result == {
        "A": ["B", "C"],
        "C": ["A"],
        "B": ["D"],
        "D": []
    }


# Тест ограничения глубины обхода
def test_dfs_depth():
    repository = {
        "A": ["B"],
        "B": ["C"],
        "C": []
    }

    result = dfs("A", repository, True, 1, "")

    assert result == {
        "A": ["B"],
        "B": []
    }


# Тест исключения пакетов
def test_dfs_exclude():
    repository = {
        "A": ["B", "C"],
        "B": ["D"],
        "C": [],
        "D": []
    }

    result = dfs("A", repository, True, 3, "C")

    assert "C" not in result
    assert result["A"] == ["B"]


# Тест обработки цикла
def test_dfs_cycle():
    repository = {
        "A": ["B"],
        "B": ["A"]
    }

    result = dfs("A", repository, True, 5, "")

    assert result == {
        "A": ["B"],
        "B": ["A"]
    }


# Тест поиска обратных зависимостей
def test_reverse_dependencies():
    graph = {
        "A": ["B", "C"],
        "B": ["D"],
        "C": ["A"],
        "D": []
    }

    result = find_reverse_dependencies(graph, "A")

    assert result == ["C"]


# Тест вывода ASCII-дерева
def test_ascii_tree(capsys):
    graph = {
        "A": ["B"],
        "B": ["C"],
        "C": []
    }

    print_ascii_tree(graph, "A")

    output = capsys.readouterr().out

    assert "A" in output
    assert "B" in output
    assert "C" in output


# Тест создания файла PlantUML и PNG
def test_create_graph_image(tmp_path, monkeypatch):
    graph = {
        "A": ["B"],
        "B": []
    }

    # Заменяем запуск PlantUML, чтобы тесту не требовалась установка программы
    def fake_run(*args, **kwargs):
        return None

    monkeypatch.setattr("src.main.subprocess.run", fake_run)

    output = tmp_path / "graph.png"

    create_graph_image(graph, str(output))

    puml_file = tmp_path / "graph.puml"

    assert puml_file.exists()

    content = puml_file.read_text(encoding="utf-8")

    assert "@startuml" in content
    assert "@enduml" in content
    assert 'component "A" as n0' in content
    assert 'component "B" as n1' in content
    assert "n0 --> n1" in content


# Тест ошибки при чтении отсутствующего файла
def test_missing_file():
    with pytest.raises(FileNotFoundError):
        read_test_repository("missing.json")


# Тест ошибки при чтении неправильного JSON
def test_invalid_json(tmp_path):
    file = tmp_path / "invalid.json"
    file.write_text('{"A": [}', encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        read_test_repository(file)