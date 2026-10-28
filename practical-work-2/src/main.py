import argparse #проверяет наличие обязательных параметров и определяет ошибки
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
import json

def get_dependencies(package, repository, test_mode):
    if test_mode:
        data = Path(repository).read_bytes()
    else:
        group, name, version = package.split(":")
        group = group.replace(".", "/")
        url = f"{repository.rstrip('/')}/{group}/{name}/{version}/"
        url += f"{name}-{version}.pom"
        data = urllib.request.urlopen(url, timeout=10).read()

    root = ET.fromstring(data)
    dependencies = root.find("{*}dependencies")

    if dependencies is None:
        return []

    result = []
    for dep in dependencies.findall("{*}dependency"):
        group = dep.findtext("{*}groupId", default="?")
        name = dep.findtext("{*}artifactId", default="?")
        version = dep.findtext("{*}version", default="не указана")
        result.append(f"{group}:{name}:{version}")

    return result

#обход в ширину
def bfs(package,graph,depth,exclude):
    queue = [(package, 0)]
    visited = set()
    result = {}

    while queue:
        current,level = queue.pop(0)

        if current in visited:
            continue
        if exclude and exclude in current:
            continue
        visited.add(current)
        result[current] = []

        if level>=depth:
            continue

        for dependency in graph.get(current,[]):
            if exclude and exclude in dependency:
                continue

            result[current].append(dependency)

            if dependency not in visited:
                queue.append((dependency,level+1))
    return result










def read_test_repository(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--test-repo", action="store_true")
    parser.add_argument("--output", default="graph.png")
    parser.add_argument("--ascii", action="store_true")
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--exclude", default="")
    args = parser.parse_args()

    print("Имя пакета:", args.package)
    print("Репозиторий:", args.repository)
    print("Тестовый режим:", args.test_repo)
    print("Изображение:", args.output)
    print("ASCII-дерево:", args.ascii)

    if args.test_repo:
        graph = read_test_repository(args.repository)

        result = bfs(args.package, graph, args.depth, args.exclude)

        print("Граф зависимостей:")
        for package, dependencies in result.items():
            print(package, "->", dependencies)

    else:
        dependencies = get_dependencies(args.package, args.repository, False)
        print("Прямые зависимости:")
        for dependency in dependencies:
            print(dependency)


if __name__ == "__main__":
    main()