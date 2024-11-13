# -*- coding: cp1251 -*-
import os
import tarfile
import re
import io
import argparse

arc = ""
path = ""
prev = ""

def initialize_globals(archive_path):
    """Функция для инициализации глобальных переменных."""
    global arc, path, prev
    arc = archive_path
    path = ""
    prev = ""

def cd(cur_dir):
    global path
    global prev
    with tarfile.open(arc) as tarf:
        res_comm = cur_dir.strip()[3:]

        if ".txt" in res_comm:
            print(f"sh: cd: can't cd to {res_comm}: Not a directory")
            return

        if res_comm.startswith('/'):
            if res_comm[1:] in tarf.getnames():
                prev = path
                path = res_comm[1:]
                return
        else:
            if res_comm == "~":
                prev = path
                path = ""
                return
            if res_comm == "..":
                prev = path
                if path == "" or path.count("/") == 0:
                    path = ""
                else:
                    path = os.path.dirname(path.rstrip('/'))
                return
            if res_comm == "-":
                print(f"/{prev or 'root'}")
                prev, path = path, prev
                return

            full_path = os.path.join(path, res_comm)
            # Проверка для директорий
            if full_path in tarf.getnames() or full_path + '/' in tarf.getnames():
                prev = path
                path = full_path
                return

        print(f"sh: cd: can't cd to {res_comm}: No such file or directory")



def ls(cur_dir):
    with tarfile.open(arc) as tarf:
        entries = [name for name in tarf.getnames() if os.path.dirname(name) == cur_dir or name.startswith(cur_dir) and cur_dir == ""]
        if entries:
            # Убираем завершающий '/' для директорий
            output = " ".join(os.path.basename(entry.rstrip('/')) for entry in entries if entry != cur_dir)
            print(output)
        else:
            print("")


def whoami():
    print("vladislav")

def touch(file):
    n = b''
    with tarfile.open(arc, 'a') as tarf:
        full_path = os.path.join(path, file)
        if full_path in tarf.getnames():
            return
        tarinfo = tarfile.TarInfo(name=full_path)
        tarinfo.size = len(n)
        tarf.addfile(tarinfo, io.BytesIO(n))

def vshell(cur_dir, listik=[]):
    global path
    if not listik:
        while True:
            command = input(f"vladislav@localhost:{path or '~'}# ")
            handle_command(command)
    else:
        for command in listik:
            handle_command(command)
        vshell("")

def handle_command(command):
    if command == "ls":
        ls(path)
    elif command.startswith("cd "):
        cd(command)
    elif command == "whoami":
        whoami()
    elif command.startswith("touch "):
        touch(command[6:])
    elif command == "exit":
        raise SystemExit
    else:
        print(f"sh: {command}: not found")

class VM:
    def __init__(self, filesystem_archive: str):
        self.currentpath = ""
        self.filesystem = tarfile.TarFile(filesystem_archive)

    def start(self):
        vshell(path)

    def run_script(self, script_file: str):
        try:
            with open(script_file, 'r') as file:
                listik = [line.strip() for line in file]
                vshell(path, listik)
        except FileNotFoundError:
            print(f"Script file '{script_file}' not found.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive', type=str, required=True, help="Путь к архиву файловой системы")
    parser.add_argument('--script', type=str, required=True, help="Путь к скрипту с командами")
    args = parser.parse_args()

    initialize_globals(args.archive)

    vm = VM(args.archive)

    if args.script:
        vm.run_script(args.script)
    
    vshell("")
