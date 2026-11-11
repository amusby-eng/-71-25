
import argparse #помогает принимать аргументы из командной строки
import json 
import urllib.request #скачивание фэйла из инета 
import urllib.error
import zipfile
import subprocess
from pathlib import Path
from io import BytesIO
import xml.etree.ElementTree as ET #чтение XML


# ЭТАП 2. Получение зависимостей из NuGet

def read_test_repository(filename):
    # Читаем тестовый репозиторий из JSON
    with open(filename, "r", encoding="utf-8") as file:
        graph = json.load(file)
    return graph


def get_dependencies(package, repository):
    # Пакет для NuGet указываем так: ИмяПакета:Версия
    name, version = package.split(":")

    # Формируем ссылку на архив пакета
    url = (
        repository.rstrip("/")
        + "/"
        + name.lower()
        + "/"
        + version.lower()
        + "/"
        + name.lower()
        + "."
        + version.lower()
        + ".nupkg"
    )

    # Скачиваем архив
    response = urllib.request.urlopen(url, timeout=15)
    data = response.read()


    archive = zipfile.ZipFile(BytesIO(data))#открываем архив

    nuspec_name = None

    for filename in archive.namelist():
        if filename.endswith(".nuspec"):
            nuspec_name = filename
            break

    if nuspec_name is None:
        return []

    # Читаем XML
    xml_data = archive.read(nuspec_name)
    root = ET.fromstring(xml_data)#преобразует в структуру элементов питон

    dependencies = []
    dependency_list = root.find(".//{*}dependencies")

    if dependency_list is None:
        return dependencies

    # Получаем названия зависимостей и их версии
    for dependency in dependency_list.findall(".//{*}dependency"):
        dep_name = dependency.get("id")
        dep_version = dependency.get("version")

        if dep_name is None or dep_version is None:
            continue

        # Например, из диапазона [1.2.0, 2.0.0)
        # берём нижнюю границу 1.2.0
        dep_version = dep_version.strip("[]()")
        dep_version = dep_version.split(",")[0].strip()

        if dep_version != "":
            dependencies.append(dep_name + ":" + dep_version)

    return dependencies


# ЭТАП 3. Построение графа с помощью DFS без рекурсии

def dfs(package, repository, test_mode, depth, exclude):
    graph = {}
    visited = set()

    # В стеке храним пакет и глубину
    stack = [(package, 0)]

    while len(stack) > 0:
        current, level = stack.pop()

        # Если пакет уже встречался, пропускаем его
        if current in visited:
            continue

        # Исключаем пакеты, содержащие заданную подстроку
        if exclude != "" and exclude.lower() in current.lower():
            continue

        visited.add(current)
        graph[current] = []

        # Если достигли максимальной глубины, дальше не идём
        if level >= depth:
            continue

        # Получаем зависимости
        if test_mode:
            dependencies = repository.get(current, [])
        else:
            dependencies = get_dependencies(current, repository)

        for dependency in dependencies:
            if exclude != "" and exclude.lower() in dependency.lower():
                continue

            graph[current].append(dependency)

            if dependency not in visited:
                stack.append((dependency, level + 1))

    return graph


# ЭТАП 4. Поиск обратных зависимостей

def find_reverse_dependencies(graph, package):
    reverse_graph = {}

    # Переворачиваем все связи графа
    for current in graph:
        reverse_graph[current] = []

    for current in graph:
        for dependency in graph[current]:
            if dependency not in reverse_graph:
                reverse_graph[dependency] = []

            reverse_graph[dependency].append(current)

    # Теперь ищем пакеты, которые зависят от заданного
    result = []
    visited = set()
    stack = [package]

    while stack:
        current = stack.pop()

        if current in visited:
            continue

        visited.add(current)

        for dependency in reverse_graph.get(current, []):
            if dependency not in visited:
                result.append(dependency)
                stack.append(dependency)

    return result


# ЭТАП 5. Вывод ASCII-дерева

def print_ascii_tree(graph, package):
    print("\nASCII-дерево:")
    print(package)

    stack = []

    for dependency in reversed(graph.get(package, [])):
        stack.append((dependency, "    "))

    visited = {package}

    while stack:
        current, prefix = stack.pop()

        print(prefix + "|-- " + current)

        # Не раскрываем пакет повторно, чтобы не зациклиться
        if current in visited:
            continue

        visited.add(current)

        for dependency in reversed(graph.get(current, [])):
            stack.append((dependency, prefix + "    "))


# ЭТАП 5. Создание файла PlantUML и изображения PNG

def create_graph_image(graph, output):
    # Получаем все пакеты из графа
    packages = list(graph.keys())

    # Добавляем пакеты, которые встречаются только в зависимостях
    for dependencies in graph.values():
        for dependency in dependencies:
            if dependency not in packages:
                packages.append(dependency)

    # Создаём короткие имена для пакетов: n0, n1, n2...
    names = {}

    for i in range(len(packages)):
        names[packages[i]] = "n" + str(i)

    # Начинаем формировать PlantUML-диаграмму
    lines = []
    lines.append("@startuml")
    lines.append("left to right direction")

    # Добавляем вершины
    for package in packages:
        lines.append('component "' + package + '" as ' + names[package])

    # Добавляем связи
    for package in graph:
        for dependency in graph[package]:
            lines.append(names[package] + " --> " + names[dependency])

    # Завершаем диаграмму
    lines.append("@enduml")

    # Формируем имя текстового файла с расширением .puml
    puml_file = str(Path(output).with_suffix(".puml"))

    # Сохраняем PlantUML-код в файл
    with open(puml_file, "w", encoding="utf-8") as file:
        file.write("\n".join(lines))

    print("\nФайл PlantUML сохранён:", puml_file)

    # Преобразуем PlantUML в PNG
    try:
        subprocess.run(
            ["plantuml", "-tpng", puml_file],
            check=True
        )

        png_file = str(Path(puml_file).with_suffix(".png"))
        print("Изображение сохранено:", png_file)

    except FileNotFoundError:
        print("PlantUML не установлен. Установи его командой: brew install plantuml")

    except subprocess.CalledProcessError:
        print("Не удалось создать PNG. Проверь файл PlantUML.")


# ЭТАП 1. Настройки программы и запуск

def main():
    parser = argparse.ArgumentParser( #принимает аргументы и разбирает их
        description="Визуализатор графа зависимостей пакетов"
    )

    parser.add_argument("--package", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--test-repo", action="store_true")
    parser.add_argument("--output", default="graph.png")
    parser.add_argument("--ascii", action="store_true")
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--exclude", default="")
    parser.add_argument("--reverse", default="")

    args = parser.parse_args()#хранит в себе наши значение

    # Выводим все значения
    print("Параметры программы:")
    print("package =", args.package)
    print("repository =", args.repository)
    print("test_repo =", args.test_repo)
    print("output =", args.output)
    print("ascii =", args.ascii)
    print("depth =", args.depth)
    print("exclude =", args.exclude)
    print("reverse =", args.reverse)

    #обработка ошибок
    if args.depth < 0:
        parser.error("Глубина не может быть отрицательной")

    if args.package.strip() == "":
        parser.error("Не указано имя пакета")

    if args.repository == "":
        parser.error("Не указан репозиторий")

    try:
        repository = args.repository

        # Если выбран тестовый режим, читаем JSON
        if args.test_repo:
            repository = read_test_repository(args.repository)

            if args.package not in repository:
                print("Ошибка: такого пакета нет в тестовом репозитории")
                return

        # Строим граф
        graph = dfs(
            args.package,
            repository,
            args.test_repo,
            args.depth,
            args.exclude
        )

        print("\nГраф зависимостей:")

        for package in graph:
            print(package, "->", graph[package])

        # Этап 2: выводим прямые зависимости корневого пакета
        print("\nПрямые зависимости:")
        for dependency in graph.get(args.package, []):
            print(dependency)

        # Этап 4: выводим обратные зависимости
        reverse_package = args.reverse

        if reverse_package == "":
            reverse_package = args.package

        reverse = find_reverse_dependencies(graph, reverse_package)

        print("\nОбратные зависимости пакета", reverse_package, ":")

        if len(reverse) == 0:
            print("Не найдены")
        else:
            for dependency in reverse:
                print(dependency)

        # Этап 5: ASCII-дерево
        if args.ascii:
            print_ascii_tree(graph, args.package)

        # ЭТАП 5. Создание файла PlantUML и изображения PNG
        create_graph_image(graph, args.output)

    except FileNotFoundError:
        print("Ошибка: файл не найден")

    except json.JSONDecodeError:
        print("Ошибка: неправильный формат JSON")

    except urllib.error.URLError:
        print("Ошибка: не удалось получить пакет из репозитория")

    except zipfile.BadZipFile:
        print("Ошибка: скачанный файл пакета повреждён")

    except ET.ParseError:
        print("Ошибка: не удалось прочитать XML")


if __name__ == "__main__":
    main()
