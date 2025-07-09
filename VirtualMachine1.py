''' Current code: StackTest
// Executes a sequence of arithmetic and logical operations on the stack.

push constant 17
push constant 17
eq
push constant 17
push constant 16
eq
push constant 16
push constant 17
eq
push constant 892
push constant 891
lt
push constant 891
push constant 892
lt
push constant 891
push constant 891
lt
push constant 32767
push constant 32766
gt
push constant 32766
push constant 32767
gt
push constant 32766
push constant 32766
gt
push constant 57
push constant 31
push constant 53
add
push constant 112
sub
neg
and
push constant 82
or
not
'''

lineCount = 0
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

def CodeWriter(command):

    output = ''
    global lineCount

    if command[0] == 'C_PUSH':
        segment = command[1] #doesn't actually need to do anything when using the constant segment. Might need some extra logic for that in the future...
        index = command[2]
        output += '@%s\n' \
        'D=A\n' \
        '@SP\n' \
        'A=M\n' \
        'M=D\n' \
        '@SP\n' \
        'M=M+1\n' % index
        return output

    match command[1]:
        case 'add':
            output += '@SP\n' \
            'M=M-1\n' \
            'A=M\n' \
            'D=M\n' \
            '@SP\n' \
            'M=M-1\n' \
            'A=M\n' \
            'A=M\n' \
            'D=D+A\n' \
            '@SP\n' \
            'A=M\n' \
            'M=D\n' \
            '@SP\n' \
            'M=M+1\n'

        case 'sub':
            output += '@SP\n' \
            'M=M-1\n' \
            'A=M\n' \
            'D=M\n' \
            '@SP\n' \
            'M=M-1\n' \
            'A=M\n' \
            'A=M\n' \
            'D=A-D\n' \
            '@SP\n' \
            'A=M\n' \
            'M=D\n' \
            '@SP\n' \
            'M=M+1\n'

        case 'neg':
            output += '@SP' + '\n' \
            'M=M-1' + '\n' \
            'A=M' + '\n' \
            'M=-M' + '\n' \
            '@SP' + '\n' \
            'M=M+1' + '\n'

        #comparisons: -1 = true, 0 = false
        case 'eq':
            global lineCount
            output += '@SP\n' \
              'M=M-1\n' \
              'A=M\n' \
              'D=M\n' \
              '@SP\n' \
              'M=M-1\n' \
              'A=M\n' \
              'A=M\n' \
              'D=A-D\n' \
              f'@EQ{lineCount}\n' \
              'D;JEQ\n' \
              '@SP\n' \
              'A=M\n' \
              'M=0\n' \
              '@SP\n' \
              'M=M+1\n' \
              f'@FINISH{lineCount}\n' \
              f'(EQ{lineCount})\n' \
              '@SP\n' \
              'A=M\n' \
              'M=-1\n' \
              '@SP\n' \
              'M=M+1\n' \
              f'(FINISH{lineCount})'

        case 'gt':
            global lineCount
            output += '@SP\n' \
                      'M=M-1\n' \
                      'A=M\n' \
                      'D=M\n' \
                      '@SP\n' \
                      'M=M-1\n' \
                      'A=M\n' \
                      'A=M\n' \
                      'D=A-D\n' \
                      f'@GT{lineCount}\n' \
                      'D;JGT\n' \
                      '@SP\n' \
                      'A=M\n' \
                      'M=0\n' \
                      '@SP\n' \
                      'M=M+1\n' \
                      f'@FINISH{lineCount}\n' \
                      f'(GT{lineCount})\n' \
                      '@SP\n' \
                      'A=M\n' \
                      'M=-1\n' \
                      '@SP\n' \
                      'M=M+1\n' \
                      f'(FINISH{lineCount})'

        case 'lt':
            global lineCount
            output += '@SP\n' \
                      'M=M-1\n' \
                      'A=M\n' \
                      'D=M\n' \
                      '@SP\n' \
                      'M=M-1\n' \
                      'A=M\n' \
                      'A=M\n' \
                      'D=A-D\n' \
                      f'@LT{lineCount}\n' \
                      'D;JLT\n' \
                      '@SP\n' \
                      'A=M\n' \
                      'M=0\n' \
                      '@SP\n' \
                      'M=M+1\n' \
                      f'@FINISH{lineCount}\n' \
                      f'(LT{lineCount})\n' \
                      '@SP\n' \
                      'A=M\n' \
                      'M=-1\n' \
                      '@SP\n' \
                      'M=M+1\n' \
                      f'(FINISH{lineCount})'

        case 'and':
            ...

        case 'or':
            ...

        case 'not':
            ...

    '''if command[0] == 'C_ARITHMETIC': #I think this one here is right.
        output += '@SP\n' \
        'M=M-1\n' \
        'A=M\n' \
        'D=M\n' \
        '@SP\n' \
        'M=M-1\n' \
        'A=M\n' \
        'A=M\n' \
        'D=D+A\n' \
        '@SP\n' \
        'A=M\n' \
        'M=D\n' \
        '@SP\n' \
        'M=M+1\n'
        '''

    return output

def EndCode():
    end = '(END)\n' \
    '@END\n' \
    '0;JMP\n'
    return end

def VMTranslator():
    filename = input("Please input file name without extension: ")
    output = ''
    global lineCount
    with open(filename + ".vm", 'r') as bytecode:
        with open(filename + ".asm", 'w') as machineCode:
            for lineCount, line in enumerate(bytecode):
                command = Parser(line)
                if command:
                    output = CodeWriter(command)
                if output:
                    machineCode.write(output)
            end = EndCode()
            machineCode.write(end)
    return

VMTranslator()
