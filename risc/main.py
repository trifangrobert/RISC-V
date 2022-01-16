only_ones = (2 ** 32) - 1
filename = "./tests/rv32um-v-rem.mc"
def instructionFetch():
    global programCounter
    currentInstruction = instructions[getIndex(programCounter)][1]
    # print(len(currentInstruction))
    programCounter += 4
    return currentInstruction

def twoComplement(x):
    return x - 2 ** 32 * (x >> 31)

def R_format(currentInstruction):
    opcode = currentInstruction[-7:]
    rd = int(currentInstruction[-12:-7], 2)
    funct3 = int(currentInstruction[-15:-12], 2)
    rs1 = int(currentInstruction[-20:-15], 2)
    rs2 = int(currentInstruction[-25:-20], 2)
    funct7 = int(currentInstruction[-32:-25], 2)
    # print(currentInstruction, funct7, rs2, rs1, funct3, rd, opcode)
    if opcode == '0110011':
        if funct3 == 5 and funct7 == 0: #SRL
            value = (2 ** 5) - 1
            value = (value & registers[rs2])
            registers[rd] = registers[rs1] // (2 ** value)
        elif funct3 == 4 and funct7 == 0: #XOR
            registers[rd] = (registers[rs1] ^ registers[rs2])
        elif funct3 == 6 and funct7 == 1: #REM
            # registers[rd] = (registers[rs1] % registers[rs2])
            if registers[rs2] == 0:
                registers[rd] = registers[rs1]
            else:
                valrs1 = twoComplement(registers[rs1])
                valrs2 = twoComplement(registers[rs2])
                print(valrs1, valrs2)
                sign = 0
                if valrs1 < 0:
                    valrs1 *= -1
                    sign += 1
                if valrs2 < 0:
                    valrs2 *= -1
                registers[rd] = (valrs1 % valrs2)
                if sign % 2 == 1:
                    registers[rd] *= -1
                registers[rd] = registers[rd] & only_ones
                # print(registers[rs1], registers[rs2], registers[rd])


def I_format(currentInstruction):
    global running
    global only_ones
    opcode = currentInstruction[-7:]
    rd = int(currentInstruction[-12:-7], 2)
    funct3 = int(currentInstruction[-15:-12], 2)
    rs1 = int(currentInstruction[-20:-15], 2)
    imm = int(currentInstruction[-31:-20], 2)
    shamt = int(currentInstruction[-32:-20], 2)
    if currentInstruction[0] == '1':
        imm -= 2 ** 11
    # print(imm, rs1, funct3, rd, opcode)
    if opcode == '0010011':
        if funct3 == 0: #ADDI
            registers[rd] = ((registers[rs1] + imm) & only_ones)
        elif funct3 == 6: # ORI
            registers[rd] = ((registers[rs1] | imm) & only_ones)
        elif funct3 == 1: #SLLI
            registers[rd] = (registers[rs1] * (2 ** shamt)) & only_ones
    elif opcode == '1110011':
        if funct3 == 0: #ECALL
            running = False
    elif opcode == '0000011':
        if funct3 == 2:
            if registers[rs1] + imm not in variables:
                print('ce ai facut sefu')
            else:
                registers[rd] = variables[registers[rs1] + imm]


def S_format(currentInstruction):
    opcode = currentInstruction[-7:]
    funct3 = int(currentInstruction[-15:-12], 2)
    rs1 = int(currentInstruction[-20:-15], 2)
    rs2 = int(currentInstruction[-25:-20], 2)
    imm = int(currentInstruction[-31:-25] + currentInstruction[-12:-7], 2)
    if currentInstruction[0] == '1':
        imm -= 2 ** 11
    if opcode == '0100011': # SW
        if funct3 == 2:
            variables[registers[rs1] + imm] = registers[rs2]


def B_format(currentInstruction):
    global programCounter
    opcode = currentInstruction[-7:]
    funct3 = int(currentInstruction[-15:-12], 2)
    rs1 = int(currentInstruction[-20:-15], 2)
    rs2 = int(currentInstruction[-25:-20], 2)
    # print(currentInstruction[-8:-7], currentInstruction[-31:-25], currentInstruction[-12:-8])
    imm = int(currentInstruction[-8:-7] + currentInstruction[-31:-25] + currentInstruction[-12:-8], 2)
    if currentInstruction[:1] == '1':
        imm -= 2 ** 11
    imm *= 2
    if opcode == '1100011':
        if funct3 == 1: # BNE
            if registers[rs1] != registers[rs2]:
                programCounter = programCounter + imm - 4
        elif funct3 == 0: #BEQ
            if registers[rs1] == registers[rs2]:
                programCounter = programCounter + imm - 4
    # print(imm)


def U_format(currentInstruction):
    global only_ones
    opcode = currentInstruction[-7:]
    rd = int(currentInstruction[-12:-7], 2)
    imm = int(currentInstruction[-31:-12], 2)
    if currentInstruction[:1] == '1':
        imm -= 2 ** 19
    # print(imm)
    if opcode == '0110111': # LUI
        registers[rd] = 0
        registers[rd] = ((imm * (2 ** 12)) & only_ones)
    elif opcode == '0010111': #AUIPC
        registers[rd] = 0
        jump = (imm * (2 ** 12)) & only_ones
        registers[rd] = programCounter + jump - 4
        # print('AUIPC')


def J_format(currentInstruction):
    return True



def instructionDecode(currentInstruction):
    R_opcodes = ['0110011', '0101111', '1000011', '1000111', '1001111', '1010011']
    I_opcodes = ['1100111', '0000011', '0010011', '0001111', '1110011', '0000111']
    S_opcodes = ['0100011', '0100111']
    B_opcodes = ['1100011']
    U_opcodes = ['0110111', '0010111']
    J_opcodes = ['1101111']
    opcode = currentInstruction[-7:]
    # print(opcode)
    if opcode in R_opcodes:
        R_format(currentInstruction)
    elif opcode in I_opcodes:
        I_format(currentInstruction)
    elif opcode in S_opcodes:
        S_format(currentInstruction)
    elif opcode in B_opcodes:
        B_format(currentInstruction)
    elif opcode in U_opcodes:
        U_format(currentInstruction)
    elif opcode in J_opcodes:
        J_format(currentInstruction)


def getIndex(index):
    offset = 10720
    return (index - offset) // 4


input_file = open(filename, "r")
lines = input_file.readlines()
lines = lines[1:]
# print(lines)
instructions = [x.split() for x in lines if x[9] != '<']
readingData = False
variables = {} # sunt un dictionar jmecher
for x in instructions:
    # print(x)
    if '.data:' in x:
        readingData = True
        continue
    x[0] = x[0][:-1]
    x[0] = int(x[0], 16) - 8 * 16 ** 7
    x[1] = bin(int(x[1], 16))
    x[1] = x[1][2:]
    x[1] = ('0' * (32 - len(x[1]))) + x[1]
    # print(x)
    if readingData == True:
        if x[0] % 4 == 0:
            variables[int(x[0])] = int(x[1], 2)
        else:
            variables[int(x[0]) - 2] = variables[int(x[0]) - 2] * (2 ** 16) + int(x[1], 2)
    # print(x[1])




# am sarit peste primele 31 de instructiuni pentru ca era initializarea registrilor cu 0
# si apoi sarea dintr-un motiv misterios peste adrese de memorie
registers = [0] * 31
instructions = instructions[32:]
programCounter = 10720


running = True
steps = 100000
while running == True and steps > 0:
    print(registers)
    print(programCounter)
    currentInstruction = instructionFetch()
    instructionDecode(currentInstruction)
    steps -= 1

if steps == 0: #infinite loop
    print('failed')
else:
    print('passed')
#print(registers)