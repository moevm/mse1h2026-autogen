from .QuestionBase import QuestionBase, Result
from .utility import CProgramRunner, ExecutionError
import random
from functools import reduce

class QuestionN3(QuestionBase):
    questionName = 'Работа с массивом целых чисел'

    def __init__(self, *, seed):
        super().__init__(seed=seed)

        random.seed(self.seed)
        self.elementType = random.choice(['odd', 'even'])
        self.operationType = random.choice(['sum', 'product', 'bit_and', 'bit_or', 'bit_xor', 'bit_not', 'shift_left', 'shift_right'])
        self.maxLength = 15 if self.operationType == 'product' else 100
        self.intTypes = ['int', 'long', 'short']
        self.floatTypes = ['float', 'double']

        if self.operationType in ['sum', 'product']:
            self.dataType = random.choice(self.intTypes + self.floatTypes)
        else:
            self.dataType = random.choice(self.intTypes)

        if self.operationType in ['shift_left', 'shift_right']:
            self.shiftValue = 1

    def generateTest(self) -> tuple[str, str]:
        length = random.randint(10, self.maxLength)
        match self.dataType:
            case 'int':
                borders = (-100_000_000, 100_000_000)
            case 'short':
                borders = (-32_768, 32_767)
            case 'long':
                borders = (-1_000_000_000, 1_000_000_000)
            case 'float' | 'double':
                borders = (-1_000_000, 1_000_000)
        
        if self.operationType in ['shift_left','shift_right']:
            borders = (0, borders[1])

        if self.operationType == 'product':
            borders = (-100, 100)

        if self.dataType in ['int', 'short', 'long']:
            numbers = [random.randint(*borders) for _ in range(length)]
        else:
            numbers = [round(random.uniform(*borders), 3) for _ in range(length)]
        
        targetNumbers = numbers[(1 if self.elementType == 'odd' else 0)::2]

        programInput = ' '.join([str(x) for x in [length] + numbers])

        match self.operationType:
            case 'sum':
                expectedOutput = sum(targetNumbers)
            case 'product':
                expectedOutput = reduce(lambda x,y: x*y, targetNumbers, 1)
            case 'bit_and':
                if not targetNumbers:
                    expectedOutput = 0
                else:
                    expectedOutput = targetNumbers[0]
                    for num in targetNumbers[1:]:
                        expectedOutput &= num
            case 'bit_or':
                if not targetNumbers:
                    expectedOutput = 0
                else:
                    expectedOutput = targetNumbers[0]
                    for num in targetNumbers[1:]:
                        expectedOutput |= num
            case 'bit_xor':
                if not targetNumbers:
                    expectedOutput = 0
                else:
                    expectedOutput = targetNumbers[0]
                    for num in targetNumbers[1:]:
                        expectedOutput ^= num
            case 'shift_left':
                shifted = [x << self.shiftValue for x in targetNumbers]
                expectedOutput = sum(shifted)
            case 'shift_right':
                shifted = [x >> self.shiftValue for x in targetNumbers]
                expectedOutput = sum(shifted)
            case 'bit_not':
                noted = [~x for x in targetNumbers]
                expectedOutput = sum(noted)
        
        if self.dataType in self.floatTypes:
            expectedOutput = f'{expectedOutput:.6f}'
        else:
            expectedOutput = str(expectedOutput)

        return programInput, expectedOutput

    @property
    def questionText(self) -> str:
        operation = {
            'sum': 'сумму',
            'product': 'произведение',
            'bit_and': 'результат побитового И (AND)',
            'bit_or': 'результат побитового ИЛИ (OR)',
            'bit_xor': 'результат побитового исключащего ИЛИ (XOR)',
            'bit_not': 'сумму результатов побитового НЕТ (NOT)',
            'shift_left': 'сумму результатов сдвига влево на 1',
            'shift_right': 'сумму результатов сдвига вправо на 1',
        }[self.operationType]

        element = {
            'odd': 'нечётным',
            'even': 'чётным'
        }[self.elementType]

        random.seed(self.seed)
        test = self.generateTest()

        exampleTable = f'''
            <table border>
                <tr>
                    <th>Входные данные</th><th>Результат</th>
                </tr>
                <tr>
                    <td>{test[0]}</td><td>{test[1]}</td>
                </tr>
            </table>
            '''
        
        special_notes = []
        if self.operationType == 'bit_and':
            special_notes.append(f'''<li>Для пустого массива операция AND возвращает 0</li>''')
        if self.operationType in ['shift_left', 'shift_right']:
            special_notes.append(f'''<li>Сдвиг выполняется на константу {self.shiftValue}</li>''')
            special_notes.append(f'''<li>После сдвига каждого элемента результаты суммируются</li>''')
        if self.operationType == 'bit_not':
            special_notes.append(f'''<li>После применения NOT к каждому элементу результаты суммируются</li>''')

        special_cases = ''
        if special_notes:
            special_cases = f'''
            <br>
            Особые случаи:
                <ul>
                    {''.join(special_notes)}
                </ul>
            '''

        return f'''
            Напишите программу, на вход которой подаётся сначала число <b>N</b> (<={self.maxLength}), а после - <b>N</b> чисел типа <code>{self.dataType}</code>.
            Требуется сохранить числа в статический массив, найти и вывести на экран {operation} элементов массива с {element} индексом.<br><br>
            {special_cases}
            <br>
            Пример:
            {exampleTable}
        '''

    @property
    def preloadedCode(self) -> str:
        return '\n'.join([
            '#include <stdio.h>',
            '',
            'int main() {',
            '',
            '    return 0;',
            '}'
        ])

    def test(self, code: str) -> Result.Ok | Result.Fail:
        program = CProgramRunner(code)

        random.seed(self.seed)
        for _ in range(5):
            programInput, expectedOutput = self.generateTest()

            try:
                result = program.run(programInput)
                if result != expectedOutput:
                    return Result.Fail(programInput, expectedOutput, result)
            except ExecutionError as e:
                return Result.Fail(programInput, expectedOutput, str(e))

        return Result.Ok()
