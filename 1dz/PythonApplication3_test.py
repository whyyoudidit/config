# -*- coding: cp1251 -*-
import sys
sys.path.append('D:/reposD/PythonApplication3/PythonApplication3')
from PythonApplication3 import initialize_globals, cd, ls, touch, whoami, vshell
import unittest
import tarfile
import os
import io
from contextlib import redirect_stdout


class TestLinuxShellEmulator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Указываем путь к существующему архиву
        cls.test_archive_name = 'D:/reposD/PythonApplication3/PythonApplication3_test/PythonApplication3_test/test_filesystem.tar'

    def setUp(self):
        initialize_globals(self.test_archive_name)

    def test_cd(self):
        # Переход в существующую директорию
        cd('cd dir1')
        from PythonApplication3 import path
        self.assertEqual(path, 'dir1')

        # Возврат на уровень вверх
        cd('cd /dir1')
        self.assertEqual(path, 'dir1')

        # Переход в несуществующую директорию
        cd('cd nonexistent')
        self.assertEqual(path, "dir1")

    def test_ls(self):
        # Листинг в корне
        with redirect_stdout(io.StringIO()) as stdout:
            ls('')
        output = stdout.getvalue().strip()
        self.assertIn('file1.txt', output)
        self.assertIn('dir1', output)

        # Листинг содержимого директории
        cd('cd dir1')
        with redirect_stdout(io.StringIO()) as stdout:
            ls('dir1')
        output = stdout.getvalue().strip()
        self.assertIn('file2.txt', output)

    def test_touch(self):
        # Создание нового файла
        touch('newfile.txt')
        with tarfile.open(self.test_archive_name) as tar:
            self.assertIn('newfile.txt', tar.getnames())

        # Создание файла в папке
        touch('dir1/newfile.txt')
        with tarfile.open(self.test_archive_name) as tar:
            self.assertIn('dir1/newfile.txt', tar.getnames())

    def test_whoami(self):
        with redirect_stdout(io.StringIO()) as stdout:
            whoami()
        output = stdout.getvalue().strip()
        self.assertEqual(output, 'vladislav')

if __name__ == '__main__':
    unittest.main()
