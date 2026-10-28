import argparse #проверяет наличие обязательных параметров и определяет ошибки

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


