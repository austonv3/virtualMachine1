from collections import defaultdict
'''Current Code: PointerTest
push constant 3030
pop pointer 0
push constant 3040
pop pointer 1
push constant 32
pop this 2
push constant 46
pop that 6
push pointer 0
push pointer 1
add
push this 2
sub
push that 6
add'''
filename = ''

def pop(targetRegister):
    output = '@SP\n' \
    'M=M-1\n' \
    'A=M\n'
    if targetRegister == 'A':
        output += 'A=M\n'
    elif targetRegister == 'D':
        output += 'D=M\n'
    else:
        raise Exception('Sorry, the strings "A" and "D" are the only valid inputs')
    return output

def c_pop(segment, index):
    global filename
    output = ''
    memory = '@R13\n'
    temp = '@5\n'
    output += f'@{index}\n' + 'D=A\n'
    match segment:
        case 'argument':
            output += '@ARG\n'
        case 'local':
            output += '@LCL\n'
        case 'this':
            output += '@THIS\n'
        case 'that':
            output += '@THAT\n'
        case 'temp':
            output += temp + 'D=D+A\n' + memory + 'M=D\n' +pop('D') + memory + 'A=M\n' + 'M=D\n'
            return output
        case 'static':
            output = pop('D') + f'@{filename}.{index}\n' + 'M=D\n'
            return output
        case 'pointer':
            if index == '0':
                output = pop('D') + '@THIS\n' + 'M=D\n'
            else:
                output = pop('D') + '@THAT\n' + 'M=D\n'
            return output
    output += 'A=M\n' + 'D=D+A\n' + memory + 'M=D\n' + pop('D') + memory + 'A=M\n' + 'M=D\n'
    return output

def push(segment='None', index='None'):
    global filename
    output = ''
    memory = '@R13\n'
    temp = '@5\n'
    if index != 'None':
        output += f'@{index}\n' + 'D=A\n'
    match segment:
        case 'constant': #think I can just delete this.
            ...
        case 'local':
            output += '@LCL\n' + 'A=D+M\n' + 'D=M\n'
        case 'this':
            output += '@THIS\n' + 'A=D+M\n' + 'D=M\n'
        case 'that':
            output += '@THAT\n' + 'A=D+M\n' + 'D=M\n'
        case 'argument':
            output += '@ARG\n' + 'A=D+M\n' + 'D=M\n'
        case 'temp':
            output += temp + 'A=D+A\n' + 'D=M\n'
        case 'pointer':
            if index == '0':
                output = '@THIS\n' + 'D=M\n'
            elif index == '1':
                output = '@THAT\n' + 'D=M\n'
        case 'static':
            output = f'@{filename}.{index}\n' + 'D=M\n'
    output += '@SP\n' + 'A=M\n' + 'M=D\n' + '@SP\n' +'M=M+1\n'
    return output


def Parser(line):
    commandType = str()
    arg1 = str()
    arg2 = str()
    if len(line) > 1 and line[0] != '/':
        arguments = line[:-1].split(' ')
        if arguments[0] == 'push':
            commandType = 'C_PUSH'
            arg1 = arguments[1]
            arg2 = arguments[2]
        elif arguments[0] == 'pop':
            commandType = 'C_POP'
            arg1 = arguments[1]
            arg2 = arguments[2]
        else:
            commandType = 'C_ARITHMETIC'
            arg1 = arguments[0]

    return commandType, arg1, arg2

def c_arithmetic(command, linecount):
    output = ''
    # sets target ram to 0 if comparison failed or -1 if comparison succeeded
    ramSetStart = '@SP\n' + 'A=M\n'
    ramSetEnd = '@SP\n' + 'M=M+1\n'
    falseValue = 'M=0\n'
    trueValue = 'M=-1\n'
    jumpStatement = f'@FINISH{linecount}\n' + '0;JMP\n'
    jumpTarget = f'(FINISH{linecount})\n'

    comparisonFailed = ramSetStart + falseValue + ramSetEnd + jumpStatement
    comparisonSuccess = ramSetStart + trueValue + ramSetEnd + jumpTarget
    match command:
        case 'add':
            output += pop('D') + pop('A') + 'D=D+A\n' + push()

        case 'sub':
            output += pop('D') + pop('A') + 'D=A-D\n' + push()

        case 'neg':
            output += pop('D') + 'M=-D\n' +'@SP' + '\n' + 'M=M+1' + '\n'

        # comparisons: -1 = true, 0 = false
        case 'eq':
            output += \
                (
                        pop('D') + pop('A') + 'D=A-D\n' + f'@EQ{linecount}\n' + 'D;JEQ\n' +
                        comparisonFailed + f'(EQ{linecount})\n' + comparisonSuccess
                )

        case 'gt':
            output += \
                (
                        pop('D') + pop('A') + 'D=A-D\n' f'@GT{linecount}\n' + 'D;JGT\n' +
                        comparisonFailed + f'(GT{linecount})\n' + comparisonSuccess
                )

        case 'lt':
            output += \
                (
                        pop('D') + pop('A') + 'D=A-D\n' + f'@LT{linecount}\n' + 'D;JLT\n' +
                        comparisonFailed + f'(LT{linecount})\n' + comparisonSuccess
                )

        case 'and':
            output += pop('D') + pop('A') + 'D=D&A\n' + push()

        case 'or':
            output += pop('D') + pop('A') + 'D=D|A\n' + push()

        case 'not':
            output += pop('D') + 'D=!D\n' +'M=D\n' + '@SP\n' + 'M=M+1\n'
    return output

def CodeWriter(command, linecount):

    output = ''

    dispatch_table = defaultdict(list)
    dispatch_table['C_PUSH'].append(push(command[1], command[2]))
    dispatch_table['C_ARITHMETIC'].append(c_arithmetic(command[1], linecount))
    dispatch_table['C_POP'].append(c_pop(command[1], command[2]))

    output = dispatch_table[command[0]]
    return output

def EndCode():
    end = '(END)\n' \
    '@END\n' \
    '0;JMP\n'
    return end

def VMTranslator():
    global filename
    filename = input("Please input file name without extension: ")
    output = ''
    with open(filename + ".vm", 'r') as bytecode:
        with open(filename + ".asm", 'w') as machineCode:
            for lineCount, line in enumerate(bytecode):
                command = Parser(line)
                if command:
                    output = CodeWriter(command, lineCount)
                for item in output:
                    machineCode.write(item)
            end = EndCode()
            machineCode.write(end)
    return

VMTranslator()