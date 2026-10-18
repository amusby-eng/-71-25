import getpass#подключаем модуль, который умеет узнавать имя пользователя
import socket#подключаем модуль, через который можно получить имя компьютера
import csv
import hashlib
import pandas as pd
username = getpass.getuser() #получаем юзернайм
hostname = socket.gethostname()#получает хостнайм компьютера

folders = 'examples/vfs — копия.csv'
reader = pd.read_csv(folders)

while True:
    command = input(f"{username}@{hostname}:~$ ")
    parts = command.split()

    if not parts:
        print("Введите команду")

    elif parts[0] == "ls":
        print(reader)

    elif parts[0] == "cd":
        if len(parts) < 2:
            print("Укажите папку")
        else:
            folder = parts[1]
            print(f"{username}@{hostname}:/usr/local/bin/python3/folders/{folder}$")

    elif parts[0] == "exit":
        print("Выход из программы")
        break

    elif parts[0] == "vfs-info":
        print("Файл VFS:", folders)
        print("SHA-256:", hashlib.sha256(
            open(folders, "rb").read()
        ).hexdigest())

    else:
        print("Неправильный ввод команды")
