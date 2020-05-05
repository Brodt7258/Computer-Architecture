"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.registers = [0] * 8
        self.registers[7] = 0xF4

        self.memory = [0] * 256

        self.PC = 0
        self.FL = 0b00000000

    def load(self, filename):
        """Load a program into memory."""
        try:
            address = 0
            with open(filename) as file:
                for line in file:
                    comment_split = line.split("#")
                    number_string = comment_split[0].strip()

                    if number_string == '':
                        continue

                    instruction = int(number_string, 2)
                    self.memory[address] = instruction
                    address += 1

        except FileNotFoundError:
            print(f"{sys.argv[0]}: could not find {sys.argv[1]}")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.registers[reg_a] += self.registers[reg_b]
        # elif op == "SUB": etc
        elif op == 'MUL':
            self.registers[reg_a] *= self.registers[reg_b]
        elif op == 'CMP':
            self.FL = self.FL & 0b11111000
            if self.registers[reg_a] == self.registers[reg_b]:
                self.FL = self.FL | 0b00000001
            elif self.registers[reg_a] > self.registers[reg_b]:
                self.FL = self.FL | 0b00000010
            else:
                self.FL = self.FL | 0b00000100
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, address):
        return self.memory[address]

    def ram_write(self, address, value):
        self.memory[address] = value

    def run(self):
        """Run the CPU."""
        running = True

        while running:
            IR = self.ram_read(self.PC)

            if IR == HLT:
                running = False

            elif IR == LDI:
                self.registers[self.memory[self.PC + 1]] = self.memory[self.PC + 2]
                self.PC += 3

            elif IR == PRN:
                print(self.registers[self.memory[self.PC + 1]])
                self.PC += 2

            elif IR == MUL:
                self.alu('MUL', self.memory[self.PC + 1], self.memory[self.PC + 2])
                self.PC += 3

            elif IR == ADD:
                self.alu('ADD', self.memory[self.PC + 1], self.memory[self.PC + 2])
                self.PC += 3

            elif IR == PUSH:
                self.registers[7] -= 1
                self.memory[self.registers[7]] = self.registers[self.memory[self.PC + 1]]
                self.PC += 2

            elif IR == POP:
                self.registers[self.memory[self.PC + 1]] = self.memory[self.registers[7]]
                self.registers[7] += 1
                self.PC += 2

            elif IR == CALL:
                return_address = self.PC + 2
                self.registers[7] -= 1
                self.memory[self.registers[7]] = return_address

                self.PC = self.registers[self.memory[self.PC + 1]]

            elif IR == RET:
                self.PC = self.memory[self.registers[7]]
                self.registers[7] += 1

            elif IR == CMP:
                self.alu('CMP', self.memory[self.PC + 1], self.memory[self.PC + 2])
                self.PC += 3

            elif IR == JMP:
                self.PC = self.registers[self.memory[self.PC + 1]]

            elif IR == JEQ:
                if self.FL == 0b00000001:
                    self.PC = self.registers[self.memory[self.PC + 1]]
                else:
                    self.PC += 2

            elif IR == JNE:
                if self.FL != 0b00000001:
                    self.PC = self.registers[self.memory[self.PC + 1]]
                else:
                    self.PC += 2

            else:
                print(f'Unimplemented Command: {IR}')
                print(f'PC = {self.PC}')
                running = False
