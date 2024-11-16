# -*- coding: cp1251 -*-
import unittest
import sys
import coverage

# Запуск покрытия перед загрузкой тестов
cov = coverage.Coverage(branch=True)
cov.start()

# Добавляем путь к модулю
sys.path.append('D:/reposD/Config_Task_3/Config_Task_3')
from Config_Task_3 import convert_to_custom_config

class TestCustomConfigConverter(unittest.TestCase):
    
    def test_simple_global_variable(self):
        file_lines = ["a = 30"]
        expected_output = "(define a 30);"
        output = convert_to_custom_config(file_lines)
        self.assertEqual(output.strip(), expected_output)

    def test_list_variable(self):
        file_lines = ["list_var = [1, 2, 3]"]
        expected_output = "(define list_var list(1, 2, 3));"
        output = convert_to_custom_config(file_lines)
        self.assertEqual(output.strip(), expected_output)

    def test_nested_tables(self):
        file_lines = [
            "[table]",
            "key = 'value'",
            "",
            "[table.nested]",
            "inner_key = 42"
        ]
        expected_output = (
            "(define table {\n"
            "  (define key 'value')\n"
            "  (define nested {\n"
            "    (define inner_key 42)\n"
            "  });\n"
            "});"
        )
        output = convert_to_custom_config(file_lines)
        self.assertEqual(output.strip(), expected_output.strip())

    def test_mixed_globals_and_tables(self):
        file_lines = [
            "global_var = 100",
            "",
            "[main]",
            "name = 'MainTable'",
            "",
            "[main.sub]",
            "enabled = 1",
            "threshold = $[global_var]"
        ]
        expected_output = (
            "(define global_var 100);\n"
            "(define main {\n"
            "  (define name 'MainTable')\n"
            "  (define sub {\n"
            "    (define enabled 1)\n"
            "    (define threshold 100)\n"
            "  });\n"
            "});"
        )
        output = convert_to_custom_config(file_lines)
        self.assertEqual(output.strip(), expected_output.strip())

    def test_variable_substitution(self):
        file_lines = [
            "a = 10",
            "b = $[a]"
        ]
        expected_output = "(define a 10);\n(define b 10);"
        output = convert_to_custom_config(file_lines)
        self.assertEqual(output.strip(), expected_output.strip())

    def test_undefined_variable(self):
        file_lines = ["b = $[undefined_var]"]
        with self.assertRaises(ValueError) as context:
            convert_to_custom_config(file_lines)
        self.assertIn("Undefined variable: undefined_var", str(context.exception))

    def test_empty_file(self):
        file_lines = []
        expected_output = ""
        output = convert_to_custom_config(file_lines)
        self.assertEqual(output.strip(), expected_output.strip())

    def test_list_in_nested_table(self):
        file_lines = [
            "[parent.child]",
            "list = [10, 20, 30]"
        ]
        expected_output = (
            "(define parent {\n"
            "  (define child {\n"
            "    (define list list(10, 20, 30))\n"
            "  });\n"
            "});"
        )
        output = convert_to_custom_config(file_lines)
        self.assertEqual(output.strip(), expected_output.strip())

if __name__ == "__main__":
    try:
        unittest.main()
    finally:
        # Остановить и сохранить данные покрытия
        cov.stop()
        cov.save()
        
        # Показать отчет о покрытии
        print("\nCoverage Report:")
        cov.report()