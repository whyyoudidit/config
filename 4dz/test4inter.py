# -*- coding: cp1251 -*-
import struct
import yaml
import sys

memory = [0] * 1024
stack = []

def bitreverse(val):
    """
    ��������� �������� ����� (32-������ �������������).
    """
    return int('{:032b}'.format(val)[::-1], 2)

def load_const(binary_file, opcode_byte):
    print()
    """
    ��������� ������� LOAD_CONST: ��������� �������� �� ����.
    """
    second_byte = struct.unpack(">B", binary_file.read(1))[0]
    operand = ((second_byte << 8) | opcode_byte) >> 6
    stack.append(operand)
    print(f"��������� �����: {stack}")
    print(f"LOAD_CONST: {operand} ��������� �� ����")

def read_mem(binary_file, opcode_byte):
    print()
    """
    ��������� ������� READ_MEM: ��������� �������� �� ������.
    """
    # ������ ���������� 4 ����� ���������
    addr_bytes = binary_file.read(4)
    if len(addr_bytes) < 4:
        raise ValueError("������������ ������ ��� ������ � READ_MEM")
    
    # ����� ��������� ������
    print(f"READ_MEM: ��������� ����� ������ (� ������� ������): {' '.join(f'{b:02X}' for b in addr_bytes)}")
    
    # �������� ������ �������� ����
    first_significant_byte = addr_bytes[0] & 0xFF  # 8 ��� �� ������� �����
    print(f"������ �������� ����: {first_significant_byte:08b}")

    # ��������� ������� 2 ���� �� opcode_byte
    high_bits = (opcode_byte >> 6) & 0x03  # 2 ������� ���� opcode_byte
    print(f"������� 2 ���� opcode_byte: {high_bits:02b}")

    # ���������� ������ �������� ���� � 2 ���� opcode
    addr = (first_significant_byte << 2) | high_bits
    print(f"������ ����� ����� �����������: {addr} (����������)")

    # �������� ���������
    if addr >= len(memory):
        raise IndexError(f"����� {addr} ������� �� ������� ������")

    stack.append(memory[addr])
    print(f"��������� �����: {stack}")
    print(f"READ_MEM: �������� {memory[addr]} ��������� �� ������ �� ������ {addr}")




    




def write_mem(binary_file, opcode_byte):
    print()
    """
    ��������� ������� WRITE_MEM: ���������� �������� � ������.
    """
    # ������ ���������� 4 ����� ���������
    addr_bytes = binary_file.read(4)
    if len(addr_bytes) < 4:
        raise ValueError("������������ ������ ��� ������ � WRITE_MEM")

    # ����� ��������� ������
    print(f"WRITE_MEM: ��������� ����� ������ (� ������� ������): {' '.join(f'{b:02X}' for b in addr_bytes)}")
    
    # �������� ������ �������� ����
    first_significant_byte = addr_bytes[0] & 0xFF  # 8 ��� �� ������� �����
    print(f"������ �������� ����: {first_significant_byte:08b}")

    # ��������� ������� 2 ���� �� opcode_byte
    high_bits = (opcode_byte >> 6) & 0x03  # 2 ������� ���� opcode_byte
    print(f"������� 2 ���� opcode_byte: {high_bits:02b}")

    # ���������� ������ �������� ���� � 2 ���� opcode
    addr = (first_significant_byte << 2) | high_bits
    print(f"������ ����� ����� �����������: {addr} (����������)")

    # �������� ���������
    if addr >= len(memory):
        raise IndexError(f"����� {addr} ������� �� ������� ������")

    # ��������� �������� � ������� �����
    
    value = stack.pop()
    print(f"��������� �����: {stack}")
    memory[addr] = value
    print(f"WRITE_MEM: �������� {value} �������� � ������ �� ������ {addr}")



def bitreverse_op(_, __):
    print()
    """
    ��������� ������� BITREVERSE: ����������� ��� �������� ���� ����� �� ������� �����.
    """
    value = stack.pop()
    print(f"��������� �����: {stack}")
    # ������������ ����� � �������� ������ ��� ������ �����
    binary_repr = f"{value:b}"  # ������ � �������� �������
    print(f"BITREVERSE: �������� ���� �� ��������: {binary_repr}")

    # ����������� ������ ���
    inverted_binary = ''.join('1' if bit == '0' else '0' for bit in binary_repr)
    print(f"BITREVERSE: �������� ���� ����� ��������: {inverted_binary}")

    # ����������� ������� � �����
    reversed_value = int(inverted_binary, 2)
    stack.append(reversed_value)
    print(f"��������� �����: {stack}")
    print(f"BITREVERSE: {value} -> {reversed_value}")


COMMAND_EXECUTORS = {
    44: load_const,   # LOAD_CONST
    59: read_mem,     # READ_MEM
    48: write_mem,    # WRITE_MEM
    19: bitreverse_op # BITREVERSE
}

def interpret(binary_path, result_path, start, end):
    """
    �������������� ������� �� ��������� �����.
    """
    with open(binary_path, 'rb') as binary_file:
        print("������ �������������:")
     
        while True:
            opcode_byte = binary_file.read(1)
            if not opcode_byte:
                break  # ����� �����
            
            opcode_byte = struct.unpack(">B", opcode_byte)[0]
            opcode = opcode_byte & 0x3F  # ������� 6 ��� ��� opcode
            print()
            print(f"������ opcode: {opcode}")
            
            executor = COMMAND_EXECUTORS.get(opcode)
            if executor:
                executor(binary_file, opcode_byte)
            else:
                raise ValueError(f"����������� ������� � �����: {opcode}")

    with open(result_path, 'w') as result_file:
        yaml.dump({"memory": memory[start:end]}, result_file)
    print()
    print(f"���������� ��������� � {result_path}")

if __name__ == "__main__":
    """
    ������� ������� ���������. ������� ��������� ��������� ������.
    """
    if len(sys.argv) != 5:
        print("�������������: python interpreter.py <binary_path> <result_path> <start> <end>")
        sys.exit(1)
    
    binary_path = sys.argv[1]
    result_path = sys.argv[2]
    start = int(sys.argv[3])
    end = int(sys.argv[4])

    interpret(binary_path, result_path, start, end)
    
