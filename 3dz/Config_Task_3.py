# -*- coding: cp1251 -*-
import argparse
import re
import sys

def convert_to_custom_config(file_lines):
    result = []
    hierarchy = {}  # ��� �������� ��������� ������
    constants = {}  # ��� �������� ���������� ����������
    output_order = []  # ���������� ������� ������ (������� � ���������� ����������)

    current_table = None  # ������� �������
    all_variables = {}  # ��� �������� ���� ���������� � �� ����������

    def process_value(value):
        """��������� �������� ��� ����������������� ����� � ���������� ����������� ����������"""
        if isinstance(value, int) or isinstance(value, float):
            return str(value)
        elif isinstance(value, list):
            # �������������� �������� � list(��������1, ��������2)
            return "list(" + ", ".join(process_value(v) for v in value) + ")"
        elif value.startswith("$[") and value.endswith("]"):
            # ����������� ����������
            var_name = value[2:-1]
            if var_name in all_variables:
                return process_value(all_variables[var_name])
            else:
                raise ValueError(f"Undefined variable: {var_name}")
        else:
            return f"'{value}'"

    def set_nested_dict(hierarchy, keys, value):
        """����������� ���������� ��������� ������"""
        current = hierarchy
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
        # ���������� ������ ���������� ��� �����������
        full_var_name = '.'.join(keys)
        all_variables[full_var_name] = value
        if len(keys) == 1:  # ���������� ����������
            all_variables[keys[0]] = value

    def process_nested_table(name, table, depth=0):
        """����������� ��������� ��������� ������"""
        indent = "  " * depth
        result.append(f"{indent}(define {name} {{")
        for key, value in table.items():
            if isinstance(value, dict):
                process_nested_table(key, value, depth + 1)
            else:
                processed_value = process_value(value)
                result.append(f"{indent}  (define {key} {processed_value})")
        result.append(f"{indent}}});")

    def finalize_table():
        """�������������� ������� �������"""
        nonlocal current_table
        if current_table:
            output_order.append(('table', current_table))
            current_table = None

    for line in file_lines:
        line = line.strip()

        if not line:
            finalize_table()
            continue

        if line.startswith("[") and line.endswith("]"):
            finalize_table()
            current_table = line[1:-1]
            if current_table not in hierarchy:
                set_nested_dict(hierarchy, current_table.split("."), {})
            continue

        key, value = map(str.strip, line.split("=", 1))

        # �������� � ���������� ��������
        try:
            parsed_value = eval(value) if value.startswith("[") else value
        except (SyntaxError, NameError):
            parsed_value = value

        if isinstance(parsed_value, str) and parsed_value.startswith("$[") and parsed_value.endswith("]"):
            parsed_value = parsed_value
        elif isinstance(parsed_value, str) and parsed_value.isdigit():
            parsed_value = int(parsed_value)
        elif isinstance(parsed_value, str):
            parsed_value = parsed_value.strip("'")

        if current_table:
            set_nested_dict(hierarchy, current_table.split(".") + [key], parsed_value)
        else:
            constants[key] = parsed_value
            all_variables[key] = parsed_value
            output_order.append(('global', key))

    finalize_table()

    # ��������� �������� ������
    already_processed = set()
    for item_type, name in output_order:
        if item_type == 'global':
            result.append(f"(define {name} {process_value(constants[name])});")
        elif item_type == 'table' and name.split(".")[0] not in already_processed:
            top_level_name = name.split(".")[0]
            already_processed.add(top_level_name)
            process_nested_table(top_level_name, hierarchy[top_level_name])

    return "\n".join(result)

def main():
    parser = argparse.ArgumentParser(description="TOML to Custom Config Converter")
    parser.add_argument('--path', required=True, help="Path to the TOML input file")
    args = parser.parse_args()

    try:
        with open(args.path, 'r') as file:
            file_lines = file.readlines()
            converted_text = convert_to_custom_config(file_lines)
            print(converted_text)
    except (ValueError, KeyError, TypeError) as e:
        sys.stderr.write(f"Error processing TOML file: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
