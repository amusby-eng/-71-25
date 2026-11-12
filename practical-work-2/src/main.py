"""Визуализатор графа зависимостей
пакетов."""


import argparse
import json
import subprocess
import urllib.error
import urllib.request
import zipfile
from io import BytesIO
from pathlib import Path
import xml.etree.ElementTree as et


def read_test_repository(filename):

    """Загружает тестовый репозиторий
    из JSON-файла."""
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)


def create_package_url(package, repository):

    """Формирует URL для загрузки NuGet-пакета."""
    name, version = package.split(":")
    name = name.lower()
    version = version.lower()

    return (
        f"{repository.rstrip('/')}/{name}/{version}/"
        f"{name}.{version}.nupkg"
    )


def find_nuspec(archive):

    """Находит файл спецификации nuspec
    в архиве."""
    for filename in archive.namelist():
        if filename.endswith(".nuspec"):
            return filename
    return None


def parse_dependency_version(version):

    """Извлекает версию из диапазона версий."""
    return version.strip("[]()").split(",")[0].strip()


def parse_dependencies(xml_data):

    """Извлекает зависимости из
    XML-спецификации."""
    root = et.fromstring(xml_data)
    dependency_list = root.find(".//{*}dependencies")

    if dependency_list is None:
        return []

    dependencies = []
    for dependency in dependency_list.findall(".//{*}dependency"):
        dep_name = dependency.get("id")
        dep_version = dependency.get("version")

        if not dep_name or not dep_version:
            continue

        dep_version = parse_dependency_version(dep_version)
        if dep_version:
            dependencies.append(f"{dep_name}:{dep_version}")

    return dependencies


def get_dependencies(package, repository):

    """Загружает пакет и получает
    его зависимости."""
    url = create_package_url(package, repository)

    with urllib.request.urlopen(url, timeout=15) as response:
        data = response.read()

    with zipfile.ZipFile(BytesIO(data)) as archive:
        nuspec_name = find_nuspec(archive)
        if nuspec_name is None:
            return []

        xml_data = archive.read(nuspec_name)

    return parse_dependencies(xml_data)


def is_excluded(package, exclude):

    """Проверяет, соответствует ли
    пакет исключению."""
    return bool(exclude) and exclude.lower() in package.lower()


def get_package_dependencies(current, repository, test_mode):

    """Получает зависимости из тестового
    или удалённого репозитория."""
    if test_mode:
        return repository.get(current, [])
    return get_dependencies(current, repository)


def dfs(package, repository, test_mode, depth, exclude):

    """Строит граф зависимостей
    обходом в глубину."""
    graph = {}
    visited = set()
    stack = [(package, 0)]

    while stack:
        current, level = stack.pop()

        if current in visited or is_excluded(current, exclude):
            continue

        visited.add(current)
        graph[current] = []

        if level >= depth:
            continue

        dependencies = get_package_dependencies(
            current, repository, test_mode
        )

        for dependency in dependencies:
            if is_excluded(dependency, exclude):
                continue

            graph[current].append(dependency)
            if dependency not in visited:
                stack.append((dependency, level + 1))

    return graph


def build_reverse_graph(graph):

    """Строит граф обратных зависимостей."""
    reverse_graph = {package: [] for package in graph}

    for current, dependencies in graph.items():
        for dependency in dependencies:
            reverse_graph.setdefault(dependency, []).append(current)

    return reverse_graph


def find_reverse_dependencies(graph, package):

    """Находит все обратные зависимости
    пакета."""
    reverse_graph = build_reverse_graph(graph)
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


def print_ascii_tree(graph, package):

    """Выводит граф зависимостей
    в виде ASCII-дерева."""
    print("\nASCII-дерево:")
    print(package)

    stack = [
        (dependency, "    ")
        for dependency in reversed(graph.get(package, []))
    ]
    visited = {package}

    while stack:
        current, prefix = stack.pop()
        print(prefix + "|-- " + current)

        if current in visited:
            continue

        visited.add(current)
        for dependency in reversed(graph.get(current, [])):
            stack.append((dependency, prefix + "    "))


def collect_packages(graph):

    """Собирает все пакеты из графа
    и его зависимостей."""
    packages = list(graph)

    for dependencies in graph.values():
        for dependency in dependencies:
            if dependency not in packages:
                packages.append(dependency)

    return packages


def create_package_names(packages):

    """Создаёт имена узлов для
    диаграммы PlantUML."""
    return {
        package: f"n{index}"
        for index, package in enumerate(packages)
    }


def create_plantuml_lines(graph, packages, names):

    """Формирует строки диаграммы PlantUML."""
    lines = ["@startuml", "left to right direction"]

    for package in packages:
        lines.append(
            f'component "{package}" as {names[package]}'
        )

    for package, dependencies in graph.items():
        for dependency in dependencies:
            lines.append(
                f"{names[package]} --> {names[dependency]}"
            )

    lines.append("@enduml")
    return lines


def save_plantuml(lines, output):

    """Сохраняет диаграмму PlantUML в файл."""
    puml_file = str(Path(output).with_suffix(".puml"))

    with open(puml_file, "w", encoding="utf-8") as file:
        file.write("\n".join(lines))

    print("\nФайл PlantUML сохранён:", puml_file)
    return puml_file


def convert_to_png(puml_file):

    """Преобразует файл PlantUML
    в изображение PNG."""
    try:
        subprocess.run(
            ["plantuml", "-tpng", puml_file],
            check=True
        )
        png_file = str(Path(puml_file).with_suffix(".png"))
        print("Изображение сохранено:", png_file)
    except FileNotFoundError:
        print(
            "PlantUML не установлен. "
            "Установи его командой: brew install plantuml"
        )
    except subprocess.CalledProcessError:
        print("Не удалось создать PNG")


def create_graph_image(graph, output):

    """Создаёт изображение графа
    зависимостей."""
    packages = collect_packages(graph)
    names = create_package_names(packages)
    lines = create_plantuml_lines(graph, packages, names)
    puml_file = save_plantuml(lines, output)
    convert_to_png(puml_file)


def create_parser():

    """Создаёт парсер аргументов
    командной строки."""
    parser = argparse.ArgumentParser(
        description="Визуализатор графа"
    )
    parser.add_argument("--package", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--test-repo", action="store_true")
    parser.add_argument("--output", default="graph.png")
    parser.add_argument("--ascii", action="store_true")
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--exclude", default="")
    parser.add_argument("--reverse", default="")
    return parser


def validate_arguments(parser, args):

    """Проверяет корректность
    аргументов программы."""
    if args.depth < 0:
        parser.error("Глубина не может быть отриц")

    if not args.package.strip():
        parser.error("Не указано имя пакета")

    if not args.repository.strip():
        parser.error("Не указан репозиторий")


def print_arguments(args):

    """Выводит переданные параметры
    программы."""
    print("Параметры программы:")
    print("package =", args.package)
    print("repository =", args.repository)
    print("test_repo =", args.test_repo)
    print("output =", args.output)
    print("ascii =", args.ascii)
    print("depth =", args.depth)
    print("exclude =", args.exclude)
    print("reverse =", args.reverse)


def print_dependency_graph(graph):

    """Выводит граф и прямые зависимости."""
    print("\nГраф зависимостей:")
    for package, dependencies in graph.items():
        print(package, "->", dependencies)

    print("\nПрямые зависимости:")
    for dependency in graph.get(ROOT_PACKAGE, []):
        print(dependency)


ROOT_PACKAGE = ""


def print_reverse_dependencies(graph, package):

    """Выводит обратные зависимости
    указанного пакета."""
    reverse = find_reverse_dependencies(graph, package)

    print("\nОбратные зависимости", package, ":")

    if not reverse:
        print("Не найдены")
        return

    for dependency in reverse:
        print(dependency)


def load_repository(args):

    """Загружает выбранный репозиторий
    пакетов."""
    if not args.test_repo:
        return args.repository

    repository = read_test_repository(args.repository)

    if args.package not in repository:
        print("Ошибка: такого пакета нет")
        return None

    return repository


def handle_errors(error):

    """Выводит сообщение для
    перехваченной ошибки."""
    messages = {
        FileNotFoundError: "Ошибка: файл не найден",
        json.JSONDecodeError: "неправильный формат JSON",
        urllib.error.URLError:
            "не удалось получить пакет",
        zipfile.BadZipFile: "скачанный файл повреждён",
        et.ParseError: "не удалось прочитать XML",
    }
    print(messages[type(error)])


def run_program(args):

    """Выполняет основной сценарий
    визуализации зависимостей."""
    global ROOT_PACKAGE
    ROOT_PACKAGE = args.package

    repository = load_repository(args)
    if repository is None:
        return

    graph = dfs(
        args.package,
        repository,
        args.test_repo,
        args.depth,
        args.exclude
    )

    print_dependency_graph(graph)

    reverse_package = args.reverse or args.package
    print_reverse_dependencies(graph, reverse_package)

    if args.ascii:
        print_ascii_tree(graph, args.package)

    create_graph_image(graph, args.output)


def main():

    """Запускает программу и
    обрабатывает ошибки."""
    parser = create_parser()
    args = parser.parse_args()
    validate_arguments(parser, args)
    print_arguments(args)

    try:
        run_program(args)
    except (
        FileNotFoundError,
        json.JSONDecodeError,
        urllib.error.URLError,
        zipfile.BadZipFile,
        et.ParseError,
    ) as error:
        handle_errors(error)


if __name__ == "__main__":
    main()
