import argparse #проверяет наличие обязательных параметров и определяет ошибки
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--test-repo", action="store_true")
    parser.add_argument("--output", default="graph.png")
    parser.add_argument("--ascii", action="store_true")
    args = parser.parse_args()

    print("Имя пакета:", args.package)
    print("Репозиторий:", args.repository)
    print("Тестовый режим:", args.test_repo)
    print("Изображение:", args.output)
    print("ASCII-дерево:", args.ascii)

    dependencies = get_dependencies(args.package, args.repository, args.test_repo)
    print("\nПрямые зависимости:")
    for dependency in dependencies:
        print(dependency)


if __name__ == "__main__":
    main()