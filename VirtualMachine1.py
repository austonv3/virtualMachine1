'''Current Code: BasicTest
push constant 10
pop local 0
push constant 21
push constant 22
pop argument 2
pop argument 1
push constant 36
pop this 6
push constant 42
push constant 45
pop that 5
pop that 2
push constant 510
pop temp 6
push local 0
push that 5
add
push argument 1
sub
push this 6
push this 6
add
sub
push temp 6
add'''

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

def push(segment='None', index='None'):
    output = ''
    if segment == 'constant':
        output += '@%s\n' \
        'D=A\n' % index
    output += '@SP\n' \
    'A=M\n' \
    'M=D\n' \
    '@SP\n' \
    'M=M+1\n'
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
        else:
            commandType = 'C_ARITHMETIC'
            arg1 = arguments[0]

    return commandType, arg1, arg2

def CodeWriter(command, linecount):

    output = ''

    if command[0] == 'C_PUSH':
        output += push(command[1], command[2])
        return output

    match command[1]:
        case 'add':
            output += pop('D') + pop('A') + 'D=D+A\n' + push()

        case 'sub':
            output += pop('D') + pop('A') + 'D=A-D\n' + push()

        case 'neg':
            output += pop('D') + 'M=-D\n' \
            '@SP' + '\n' \
            'M=M+1' + '\n'

        #comparisons: -1 = true, 0 = false
        case 'eq':
            output += pop('D') + pop('A') + 'D=A-D\n' \
              f'@EQ{linecount}\n' \
              'D;JEQ\n' \
              '@SP\n' \
              'A=M\n' \
              'M=0\n' \
              '@SP\n' \
              'M=M+1\n' \
              f'@FINISH{linecount}\n' \
              '0;JMP\n' \
              f'(EQ{linecount})\n' \
              '@SP\n' \
              'A=M\n' \
              'M=-1\n' \
              '@SP\n' \
              'M=M+1\n' \
              f'(FINISH{linecount})\n'

        case 'gt':
            output += pop('D') + pop('A') + 'D=A-D\n' \
                      f'@GT{linecount}\n' \
                      'D;JGT\n' \
                      '@SP\n' \
                      'A=M\n' \
                      'M=0\n' \
                      '@SP\n' \
                      'M=M+1\n' \
                      f'@FINISH{linecount}\n' \
                      '0;JMP\n' \
                      f'(GT{linecount})\n' \
                      '@SP\n' \
                      'A=M\n' \
                      'M=-1\n' \
                      '@SP\n' \
                      'M=M+1\n' \
                      f'(FINISH{linecount})\n'

        case 'lt':
            output += pop('D') + pop('A') + 'D=A-D\n' \
                      f'@LT{linecount}\n' \
                      'D;JLT\n' \
                      '@SP\n' \
                      'A=M\n' \
                      'M=0\n' \
                      '@SP\n' \
                      'M=M+1\n' \
                      f'@FINISH{linecount}\n' \
                      '0;JMP\n' \
                      f'(LT{linecount})\n' \
                      '@SP\n' \
                      'A=M\n' \
                      'M=-1\n' \
                      '@SP\n' \
                      'M=M+1\n' \
                      f'(FINISH{linecount})\n'

        case 'and':
            output += pop('D') + pop('A') + 'D=D&A\n' \
            '@SP\n' \
            'A=M\n' \
            'M=D\n' \
            '@SP\n' \
            'M=M+1\n'''

        case 'or':
            output += pop('D') + pop('A') + 'D=D|A\n' \
              '@SP\n' \
              'A=M\n' \
              'M=D\n' \
              '@SP\n' \
              'M=M+1\n'

        case 'not':
            output += pop('D') + 'D=!D\n' \
            'M=D\n' \
            '@SP\n' \
            'M=M+1\n'

    return output

def EndCode():
    end = '(END)\n' \
    '@END\n' \
    '0;JMP\n'
    return end

def VMTranslator():
    filename = input("Please input file name without extension: ")
    output = ''
    with open(filename + ".vm", 'r') as bytecode:
        with open(filename + ".asm", 'w') as machineCode:
            for lineCount, line in enumerate(bytecode):
                command = Parser(line)
                if command:
                    output = CodeWriter(command, lineCount)
                if output:
                    machineCode.write(output)
            end = EndCode()
            machineCode.write(end)
    return

VMTranslator()
