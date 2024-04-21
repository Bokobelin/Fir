import sys
import time
import subprocess
from math import *
import ast
from sympy import sympify
import os

class FirInterpreter:
    def __init__(self):
        self.stack = []
        self.memory = {}
        self.included_files = set()

    def execute_file(self, file_path):
        if file_path in self.included_files:
            print(f"File '{file_path}' has already been included. Skipping.")
            return
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    execute_command(line.strip(), self, line_count)
            self.included_files.add(file_path)
        except FileNotFoundError:
            print(f"File '{file_path}' not found.")

    def push(self, value):
        if isinstance(value, float):
            self.stack.append(value)
        elif isinstance(value, int):
            self.stack.append(int(value))
        else:
            raise ValueError("Invalid value type. Value must be an integer or a float.")

    def pop(self):
        if len(self.stack) > 0:
            return self.stack.pop()
        else:
            raise ValueError("Stack underflow")

    def add(self):
        if len(self.stack) > 1:
            b = float(self.pop())
            a = float(self.pop())
            result = a + b
            if result.is_integer():
                result = int(result)  # Convert to integer if result is an integer
            self.push(result)
        else:
            raise ValueError("Not enough operands for addition")

    def sub(self):
        if len(self.stack) > 1:
            b = float(self.pop())
            a = float(self.pop())
            result = a - b
            if result.is_integer():
                result = int(result)  # Convert to integer if result is an integer
            self.push(result)
        else:
            raise ValueError("Not enough operands for subtraction")
        
    def push(self, value):
        self.stack.append(value)

    def print_message(self, message):
        if message.startswith("$"):
            mem_address = message[1:]  # Extract memory address from the message
            try:
                value = self.memory[mem_address]
                if value == int(value):
                    print(int(value))  # Print integers without decimal places
                else:
                    print(value)
            except KeyError:
                print(f"Memory address {mem_address} does not contain a value!")
        else:
            print(message)

    
    def dump(self):
        print("Stack contents:")
        for line in self.stack:
            if isinstance(line, int):
                self.print_message(str(int(line)))
            else:
                self.print_message(str(line))
    
    def str(self, mem_address, value):
        try:
            result = sympify(value.replace('^', '**')).evalf()  # Replace ^ with ** for power operation
            
            # Check if the result is an integer
            if isinstance(result, int):
                self.memory[mem_address] = int(result)
            else:
                self.memory[mem_address] = result  # Otherwise, store it as float
        except Exception as e:
            print(f"Error evaluating expression: {e}")

    def assign(self, dest_address, src_address):
        try:
            value = self.memory[src_address]
            self.memory[dest_address] = value
        except KeyError:
            print(f"Memory address {src_address} does not contain a value!")

    #DEPRECATED, use print($<mem_adress>) instead ! 
    def printr(self, mem_adress):
        print("Printr is deprecated and unsupported. Please use print($<mem_adress>) instead.")
        try:
            print(self.memory[mem_adress])
        except Exception:
            print(f"Memory adress {mem_adress} does not contain a value !")

    def execute_command(self, command):
        try:
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")

    # Add more operations as needed

line_count = 0

def main():
    if len(sys.argv) != 2:
        print("Usage: python fir.py <file_name>")
        return

    file_name = sys.argv[1]

    interpreter = FirInterpreter()

    line_count = 0

    try:
        with open(file_name, 'r') as file:
            for line in file:
                line_count += 1
                execute_command(line.strip(), interpreter, line_count)
    except FileNotFoundError:
        print(f"File '{file_name}' not found.")

def execute_command(command, interpreter, line_count):
    command = command.strip()  # Remove leading and trailing whitespace
    if not command:  # Check if the command is empty
        return  # Skip empty lines
    
    command_mapping = {
        "push": interpreter.push,
        "add": interpreter.add,
        "sub": interpreter.sub,
        "dump": interpreter.dump,
        "print": interpreter.print_message,
        "str": interpreter.str,
        "printr": interpreter.printr,
        "exec": interpreter.execute_command,
        "equ": interpreter.assign,
    }

    parts = command.split("(")  # Split the command at the "(" character
    command_name = parts[0].strip()  # Extract the command name

    if command_name in command_mapping:
        if command_name == "print":
            if len(parts) != 2 or not parts[1].endswith(")"):  # Check if the format is correct
                print("Invalid print command format:", command, "at line: ", line_count)
                return
            message = parts[1][:-1]  # Remove the trailing ")" from the message
            interpreter.print_message(message)
        else:
            if len(parts) == 1:
                # If the command has no arguments, simply execute it
                command_mapping[command_name]()
            elif len(parts) == 2:
                # Split the argument string on comma
                args = [arg.strip() for arg in parts[1].rstrip(")").split(',')]
                # Check if any argument is empty
                if any(arg == "" for arg in args):
                    print(f"Invalid {command_name} command format:", command, "at line: ", line_count)
                else:
                    command_mapping[command_name](*args)  # Unpack the args list and pass as arguments
            else:
                print(f"Invalid {command_name} command format:", command, "at line: ", line_count)
    elif command_name.startswith("using"):
        main_dir = os.path.dirname(sys.argv[1])
        file_path = command_name.split(" ")[1].strip()
        include_file_path = os.path.join(main_dir, file_path)
        interpreter.execute_file(include_file_path)
    else:
        print(f"Unknown command: {command}", "at line: ", line_count)

if __name__ == "__main__":
    start_time = time.perf_counter()  # Record the start time
    main()
    end_time = time.perf_counter()  # Record the end time
    
    # Calculate the execution time
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time} seconds")