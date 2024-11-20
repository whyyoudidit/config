# -*- coding: cp1251 -*-
import struct
import yaml
import sys

memory = [0] * 1024
stack = []

def bitreverse(val):
    """
    Побитовая инверсия числа (32-битное представление).
    """
    return int('{:032b}'.format(val)[::-1], 2)

def load_const(binary_file, opcode_byte):
    print()
    """
    Выполняет команду LOAD_CONST: добавляет значение на стек.
    """
    second_byte = struct.unpack(">B", binary_file.read(1))[0]
    operand = ((second_byte << 8) | opcode_byte) >> 6
    stack.append(operand)
    print(f"Состояние стека: {stack}")
    print(f"LOAD_CONST: {operand} добавлено на стек")

def read_mem(binary_file, opcode_byte):
    print()
    """
    Выполняет команду READ_MEM: считывает значение из памяти.
    """
    # Читаем оставшиеся 4 байта аргумента
    addr_bytes = binary_file.read(4)
    if len(addr_bytes) < 4:
        raise ValueError("Недостаточно байтов для адреса в READ_MEM")
    
    # Вывод считанных байтов
    print(f"READ_MEM: считанные байты адреса (в порядке записи): {' '.join(f'{b:02X}' for b in addr_bytes)}")
    
    # Получаем первый значащий байт
    first_significant_byte = addr_bytes[0] & 0xFF  # 8 бит из первого байта
    print(f"Первый значащий байт: {first_significant_byte:08b}")

    # Извлекаем старшие 2 бита из opcode_byte
    high_bits = (opcode_byte >> 6) & 0x03  # 2 старших бита opcode_byte
    print(f"Старшие 2 бита opcode_byte: {high_bits:02b}")

    # Объединяем первый значащий байт и 2 бита opcode
    addr = (first_significant_byte << 2) | high_bits
    print(f"Полный адрес после объединения: {addr} (десятичный)")

    # Проверка диапазона
    if addr >= len(memory):
        raise IndexError(f"Адрес {addr} выходит за пределы памяти")

    stack.append(memory[addr])
    print(f"Состояние стека: {stack}")
    print(f"READ_MEM: значение {memory[addr]} прочитано из памяти по адресу {addr}")




    




def write_mem(binary_file, opcode_byte):
    print()
    """
    Выполняет команду WRITE_MEM: записывает значение в память.
    """
    # Читаем оставшиеся 4 байта аргумента
    addr_bytes = binary_file.read(4)
    if len(addr_bytes) < 4:
        raise ValueError("Недостаточно байтов для адреса в WRITE_MEM")

    # Вывод считанных байтов
    print(f"WRITE_MEM: считанные байты адреса (в порядке записи): {' '.join(f'{b:02X}' for b in addr_bytes)}")
    
    # Получаем первый значащий байт
    first_significant_byte = addr_bytes[0] & 0xFF  # 8 бит из первого байта
    print(f"Первый значащий байт: {first_significant_byte:08b}")

    # Извлекаем старшие 2 бита из opcode_byte
    high_bits = (opcode_byte >> 6) & 0x03  # 2 старших бита opcode_byte
    print(f"Старшие 2 бита opcode_byte: {high_bits:02b}")

    # Объединяем первый значащий байт и 2 бита opcode
    addr = (first_significant_byte << 2) | high_bits
    print(f"Полный адрес после объединения: {addr} (десятичный)")

    # Проверка диапазона
    if addr >= len(memory):
        raise IndexError(f"Адрес {addr} выходит за пределы памяти")

    # Извлекаем значение с вершины стека
    
    value = stack.pop()
    print(f"Состояние стека: {stack}")
    memory[addr] = value
    print(f"WRITE_MEM: значение {value} записано в память по адресу {addr}")



def bitreverse_op(_, __):
    print()
    """
    Выполняет команду BITREVERSE: инвертирует все значащие биты числа на вершине стека.
    """
    value = stack.pop()
    print(f"Состояние стека: {stack}")
    # Представляем число в двоичной строке без лишних нулей
    binary_repr = f"{value:b}"  # Строка с двоичной записью
    print(f"BITREVERSE: Значащие биты до инверсии: {binary_repr}")

    # Инвертируем каждый бит
    inverted_binary = ''.join('1' if bit == '0' else '0' for bit in binary_repr)
    print(f"BITREVERSE: Значащие биты после инверсии: {inverted_binary}")

    # Преобразуем обратно в число
    reversed_value = int(inverted_binary, 2)
    stack.append(reversed_value)
    print(f"Состояние стека: {stack}")
    print(f"BITREVERSE: {value} -> {reversed_value}")


COMMAND_EXECUTORS = {
    44: load_const,   # LOAD_CONST
    59: read_mem,     # READ_MEM
    48: write_mem,    # WRITE_MEM
    19: bitreverse_op # BITREVERSE
}

def interpret(binary_path, result_path, start, end):
    """
    Интерпретирует команды из бинарного файла.
    """
    with open(binary_path, 'rb') as binary_file:
        print("Начало интерпретации:")
     
        while True:
            opcode_byte = binary_file.read(1)
            if not opcode_byte:
                break  # Конец файла
            
            opcode_byte = struct.unpack(">B", opcode_byte)[0]
            opcode = opcode_byte & 0x3F  # Младшие 6 бит для opcode
            print()
            print(f"Считан opcode: {opcode}")
            
            executor = COMMAND_EXECUTORS.get(opcode)
            if executor:
                executor(binary_file, opcode_byte)
            else:
                raise ValueError(f"Неизвестная команда с кодом: {opcode}")

    with open(result_path, 'w') as result_file:
        yaml.dump({"memory": memory[start:end]}, result_file)
    print()
    print(f"Результаты сохранены в {result_path}")

if __name__ == "__main__":
    """
    Главная функция программы. Ожидает аргументы командной строки.
    """
    if len(sys.argv) != 5:
        print("Использование: python interpreter.py <binary_path> <result_path> <start> <end>")
        sys.exit(1)
    
    binary_path = sys.argv[1]
    result_path = sys.argv[2]
    start = int(sys.argv[3])
    end = int(sys.argv[4])

    interpret(binary_path, result_path, start, end)
    
