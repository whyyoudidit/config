# -*- coding: cp1251 -*-
import struct
import yaml
import os
import sys
import unittest
import coverage
from unittest.mock import patch
from io import StringIO

sys.path.append('D:/reposD/test4assem/test4assem')
from test4assem import parse_instruction, encode_instruction, assemble, hex_dump

class TestAssembler(unittest.TestCase):

    def test_parse_instruction(self):
        # Проверка стандартных команд
        self.assertEqual(parse_instruction("LOAD_CONST 297"), ("LOAD_CONST", [297]))
        self.assertEqual(parse_instruction("READ_MEM 29"), ("READ_MEM", [29]))
        self.assertEqual(parse_instruction("WRITE_MEM 497"), ("WRITE_MEM", [497]))
        self.assertEqual(parse_instruction("BITREVERSE"), ("BITREVERSE", []))

        # Проверка пустой строки и комментариев
        self.assertEqual(parse_instruction("# комментарий"), (None, None))
        self.assertEqual(parse_instruction(""), (None, None))

        # Проверка строки с неизвестной командой
        self.assertEqual(parse_instruction("UNKNOWN_COMMAND 123"), ("UNKNOWN_COMMAND", [123]))

    def test_encode_instruction(self): 
        # Проверка правильного кодирования инструкций
        self.assertEqual(encode_instruction("LOAD_CONST", [297]), struct.pack(">BB", 0x6C, 0x4A))
        self.assertEqual(encode_instruction("READ_MEM", [29]), struct.pack(">B", 0x7B) + struct.pack(">I", 0x07)[::-1])
        self.assertEqual(encode_instruction("WRITE_MEM", [497]), struct.pack(">B", 0x70) + struct.pack(">I", 0x7C)[::-1])
        self.assertEqual(encode_instruction("BITREVERSE", []), struct.pack(">B", 0x13))

    def test_encode_instruction_invalid_args(self):
        # Проверка вызова функции с отсутствующими аргументами
        with self.assertRaises(ValueError):
            encode_instruction("LOAD_CONST", [])
        with self.assertRaises(ValueError):
            encode_instruction("READ_MEM", [])
        with self.assertRaises(ValueError):
            encode_instruction("WRITE_MEM", [])
        with self.assertRaises(ValueError):
            encode_instruction("BITREVERSE", [123])

    def test_encode_instruction_unknown_command(self):
        # Проверка вызова функции с неизвестной командой
        with self.assertRaises(ValueError):
            encode_instruction("INVALID_COMMAND", [0])

    def test_assemble(self):
        # Создаём тестовый файл с программой и проверяем корректность бинарного файла и логов
        source_path = "test_program.txt"
        binary_path = "test_program.bin"
        log_path = "test_log.yaml"

        with open(source_path, "w") as f:
            f.write("LOAD_CONST 297\nREAD_MEM 29\nWRITE_MEM 497\nBITREVERSE\n")

        assemble(source_path, binary_path, log_path)

        # Проверка бинарного файла
        with open(binary_path, "rb") as f:
            binary_data = f.read()
            expected_data = struct.pack(">BB", 0x6C, 0x4A) + \
                            struct.pack(">B", 0x7B) + struct.pack(">I", 0x07)[::-1] + \
                            struct.pack(">B", 0x70) + struct.pack(">I", 0x7C)[::-1] + \
                            struct.pack(">B", 0x13)
            self.assertEqual(binary_data, expected_data)

        # Проверка лога
        with open(log_path, "r") as f:
            log_data = yaml.safe_load(f)
            expected_log = [
                {"command": "LOAD_CONST", "args": [297], "hex": "6C 4A"},
                {"command": "READ_MEM", "args": [29], "hex": "7B 07 00 00 00"},
                {"command": "WRITE_MEM", "args": [497], "hex": "70 7C 00 00 00"},
                {"command": "BITREVERSE", "args": [], "hex": "13"}
            ]
            self.assertEqual(log_data, expected_log)

        # Удаление временных файлов после теста
        os.remove(source_path)
        os.remove(binary_path)
        os.remove(log_path)

    def test_empty_source_file(self):
        # Тест на случай пустого исходного файла
        source_path = "empty_program.txt"
        binary_path = "empty_program.bin"
        log_path = "empty_log.yaml"

        with open(source_path, "w") as f:
            f.write("")  # Пустой файл

        assemble(source_path, binary_path, log_path)

        # Проверка, что бинарный файл пуст
        with open(binary_path, "rb") as f:
            binary_data = f.read()
            self.assertEqual(binary_data, b'')

        # Проверка, что лог-файл пуст
        with open(log_path, "r") as f:
            log_data = yaml.safe_load(f)
            self.assertEqual(log_data, [])

        # Удаление временных файлов после теста
        os.remove(source_path)
        os.remove(binary_path)
        os.remove(log_path)

    def test_invalid_instruction_format(self):
        # Проверка строки с некорректным форматом
        source_path = "invalid_format_program.txt"
        binary_path = "invalid_program.bin"
        log_path = "invalid_log.yaml"

        with open(source_path, "w") as f:
            f.write("LOAD_CONST")  # Отсутствует аргумент

        with self.assertRaises(ValueError):
            assemble(source_path, binary_path, log_path)

        # Удаление временного файла
        os.remove(source_path)

    def test_hex_dump(self):
        # Тестирование функции hex_dump
        binary_path = "test_program.bin"

        with open(binary_path, "wb") as f:
            f.write(struct.pack(">BB", 0x6C, 0x4A))  # Записываем тестовые данные

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            hex_dump(binary_path)
            self.assertIn("Байты в program.bin:", mock_stdout.getvalue())
            self.assertIn("6C 4A", mock_stdout.getvalue())

        os.remove(binary_path)

# Запуск покрытия кода coverage
cov = coverage.Coverage()
cov.start()

try:
    unittest.main()
finally:
    cov.stop()
    cov.save()
    cov.report(show_missing=True)
