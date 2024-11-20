# -*- coding: cp1251 -*-
import struct
import yaml
import sys
COMMANDS = {
    'LOAD_CONST': 44,  # 0x2C
    'READ_MEM': 59,    # 0x3B
    'WRITE_MEM': 48,   # 0x30
    'BITREVERSE': 19   # 0x13
}
def parse_instruction(line):
    """
    Разбирает строку исходного кода на команду и аргументы.
    """
    line = line.split('#', 1)[0].strip()
    if not line:
        return None, None

    parts = line.split()
    command = parts[0]
    args = [int(part) for part in parts[1:]]
    return command, args
def encode_instruction(command, args): # pragma: no cover
    """
    Кодирует команду в бинарный формат и возвращает бинарные данные.
    """
    opcode = COMMANDS.get(command)
    if opcode is None: 
        raise ValueError(f"Неизвестная команда: {command}")

    if command == 'LOAD_CONST' and len(args) == 1:
        combined = (args[0] << 6) | opcode
        low_byte = combined & 0xFF
        high_byte = (combined >> 8) & 0xFF
        return struct.pack(">BB", low_byte, high_byte)

    elif command in {'READ_MEM', 'WRITE_MEM'} and len(args) == 1:
        # 6 бит opcode + 32 бит аргумента
        low_opcode = opcode | ((args[0] & 0x03) << 6)
        remaining = (args[0] >> 2) & 0xFFFFFF
        # Поменяем порядок байтов аргумента
        return struct.pack(">B", low_opcode) + struct.pack(">I", remaining)[::-1]

    elif command == 'BITREVERSE' and len(args) == 0:
        return struct.pack(">B", opcode)

    raise ValueError(f"Неверные аргументы для команды {command}: {args}")
def assemble(source_path, binary_path, log_path): # pragma: no cover
    """
    Считывает исходный файл, создаёт бинарный файл и логирует инструкции в правильном формате.
    """
    log_data = []
    with open(source_path, 'r') as source_file, open(binary_path, 'wb') as binary_file:
        for line in source_file:
            command, args = parse_instruction(line)
            if command:
                binary_instruction = encode_instruction(command, args)
                binary_file.write(binary_instruction)
                
                # Логируем бинарные данные в правильном порядке
                log_data.append({
                    "command": command,
                    "args": args,
                    "hex": " ".join(f"{byte:02X}" for byte in binary_instruction)
                })

    with open(log_path, 'w') as log_file:
        yaml.dump(log_data, log_file, default_flow_style=False, sort_keys=False)  
def hex_dump(file_path):  # pragma: no cover
    with open(file_path, "rb") as f: 
        data = f.read() 
        print("Байты в program.bin:") 
        print(" ".join(f"{byte:02X}" for byte in data)) 
        print("Работа ассемблера успешно завершена") 
if __name__ == "__main__":
    source_path = sys.argv[1] 
    binary_path = sys.argv[2] 
    log_path = sys.argv[3]
    assemble(source_path, binary_path, log_path) 
    binary_path = "program.bin" 
    hex_dump(binary_path) 