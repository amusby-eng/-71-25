# Dependency Graph Visualizer

## Установка

```bash
python3 -m venv .venv
source .venv/bin/activate
brew install plantuml
```

## Запуск

Из корневой папки `practical-work-2`:

```bash
python3 src/main.py --package A --repository examples/repo.json --test-repo
```

С ASCII-деревом:

```bash
python3 src/main.py --package A --repository examples/repo.json --test-repo --ascii
```

## Дополнительные параметры

- `--depth 3` — глубина обхода.
- `--exclude C` — исключить пакеты, содержащие `C`.
- `--reverse B` — найти обратные зависимости пакета `B`.
- `--output graph.png` — имя выходного изображения.

## Пример

```bash
python3 src/main.py --package A --repository examples/repo.json --test-repo --ascii --depth 3 --output graph.png
```

Результат: файлы `graph.puml` и `graph.png`.

### 1. Отрицательная глубина обхода
```bash
python3 src/main.py --package A --repository examples/repo.json --test-repo --depth -1
```

### 2. Пустое имя пакета
```bash
python3 src/main.py --package "" --repository examples/repo.json --test-repo
```

### 3. Несуществующий пакет
```bash
python3 src/main.py --package X --repository examples/repo.json --test-repo
```

### 4. Несуществующий файл репозитория
```bash
python3 src/main.py --package A --repository examples/missing.json --test-repo
```

### 5. Некорректный JSON
```bash
python3 src/main.py --package A --repository examples/invalid.json --test-repo
```

Для проверки создай файл `examples/invalid.json` с содержимым:

```json
{
    "A": ["B",
}
```

### 6. Ошибка получения пакета из репозитория
```bash
python3 src/main.py --package Newtonsoft.Json:13.0.1 --repository https://invalid.example.com
```

### 7. Пустой адрес репозитория
```bash
python3 src/main.py --package A --repository ""
```