import getpass#подключаем модуль, который умеет узнавать имя пользователя
import socket#подключаем модуль, через который можно получить имя компьютера
import csv
import hashlib
import pandas as pd
username = getpass.getuser() #получаем юзернайм
hostname = socket.gethostname()#получает хостнайм компьютера
command = input(f"{username}@{hostname}:~$")
folders = '/Users/user/Desktop/VScodePro/vfs.csv'
reader = pd.read_csv(folders)
parts = command. split()
if command =='ls':
    print (reader)
elif parts [0] == "cd":
    folder = parts[1]
    print(f"{username}@{hostname}:/usr/local/bin/python3/folders/{folder}$")
elif command == "exit":
    print("Выход из программы")
elif command == "vfs-info":
    print("Файл VFS:", folders, "\n","SHA-256:", hashlib.sha256(open(folders, "rb").read()).hexdigest()) #open(folders, "rb") - открывает файл в 2 коде,hexdigest() - превращает хэш в строку 
    
else:
    print("Неправильный ввод команды")