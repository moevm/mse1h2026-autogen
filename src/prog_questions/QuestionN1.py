from .QuestionBase import QuestionBase, Result
from .utility import CProgramRunner, ExecutionError
import random

BAD_NUMBERS = [
    'eww',
    'wolf',
    'owl',
    'xor'
]

class QuestionN1(QuestionBase):
    questionName = 'Операции с числами в различных системах счисления'

    def __init__(self, *, seed, inputSize: int = None):
        super().__init__(seed=seed, inputSize=inputSize)

        random.seed(self.seed)

        self.inputSize = inputSize if inputSize else random.randint(2, 4)

        self.inputBase = random.choice([2, 8, 10, 16])
        self.outputBase = random.choice([x for x in [2, 8, 10, 16] if x != self.inputBase])
        self.inputFormat = random.choice(['spaces', 'brackets', 'delimiter', 'squares'])
        self.delimiter = random.choice([';', ',', '|'])
        self.outputFormat = random.choice(['plain', 'brackets', 'prefix', 'labelled'])
        self.operation = random.choice(['sum', 'sub', 'mul', 'div', 'mod', 'max', 'min', 'avg'])
        self.prefixes = {2: '0b', 8: '0o', 16: '0x'}

    def toInput(self, x: int) -> str:
        match self.inputBase:
            case 2: return bin(x)[2:]
            case 8: return oct(x)[2:]
            case 10: return str(x)
            case 16: return hex(x)[2:]

    def toOutput(self, x: int) -> str:
        raw = {
            2: bin(x)[2:],
            8: oct(x)[2:],
            10: str(x),
            16: hex(x)[2:]
        }[self.outputBase]

        match self.outputFormat:
            case 'plain': return raw
            case 'brackets': return f'[{raw}]'
            case 'prefix': return f'{self.prefixes.get(self.outputBase, "")}{raw}'
            case 'labelled': return f'Result: {self.prefixes.get(self.outputBase, "")}{raw}'

    def formatInput(self, arr: list[str]) -> str:
        match self.inputFormat:
            case 'spaces': return ' '.join(arr)
            case 'brackets': return f"({self.delimiter.join(arr)})"
            case 'delimiter': return self.delimiter.join(arr)
            case 'squares': return f"[{self.delimiter.join(arr)}]"

    def operate(self, nums: list[int]) -> int:
        match self.operation:
            case 'sum':
                return sum(nums)
            case 'sub':
                result = nums[0]
                for x in nums[1:]:
                    result -= x
                return result
            case 'mul':
                result = 1
                for x in nums:
                    result *= x
                return result
            case 'div':
                result = nums[0]
                for x in nums[1:]:
                    result //= max(x, 1)
                return result
            case 'mod':
                result = nums[0]
                for x in nums[1:]:
                    result %= max(x, 1)
                return result
            case 'max':
                return max(nums)
            case 'min':
                return min(nums)
            case 'avg':
                return sum(nums) // len(nums)

    def generateGoodTest(self) -> tuple[str, str, list[int]]:
        numbers = [random.randint(1, 100) for _ in range(self.inputSize)]
        programInput = self.formatInput([self.toInput(x) for x in numbers])
        expectedOutput = self.toOutput(self.operate(numbers))
        return programInput, expectedOutput, numbers

    def generateBadTest(self) -> tuple[str, str]:
        validCount = random.randint(0, self.inputSize - 1)
        valid = [self.toInput(random.randint(1, 100)) for _ in range(validCount)]
        invalid = [random.choice(BAD_NUMBERS) for _ in range(self.inputSize - validCount)]
        all_inputs = valid + invalid
        random.shuffle(all_inputs)

        programInput = self.formatInput(all_inputs)
        expectedOutput = f'error: {validCount}'
        return programInput, expectedOutput

    @property
    def questionText(self) -> str:
        baseDict = {2: 'двоичной', 8: 'восьмеричной', 10: 'десятичной', 16: 'шестнадцатеричной'}
        operationText = {
            'sum': 'сумму',
            'sub': 'разность (от первого числа последовательно вычитаются остальные)',
            'mul': 'произведение',
            'div': 'целочисленное деление (первое число делится на остальные по порядку)',
            'mod': 'остаток от деления (первое число поочередно делится на остальные)',
            'max': 'максимум из чисел',
            'min': 'минимум из чисел',
            'avg': 'среднее арифметическое, округлённое вниз'
        }[self.operation]

        inputFormatDescription = {
            'spaces': 'разделены пробелами',
            'brackets': f'в круглых скобках через символ <b>{self.delimiter}</b>',
            'delimiter': f'разделены символом <b>{self.delimiter}</b>',
            'squares': f'в квадратных скобках через символ <b>{self.delimiter}</b>'
        }[self.inputFormat]

        outputFormatDescription = {
            'plain': 'без префиксов или скобок',
            'brackets': 'в квадратных скобках',
            'prefix': f'с префиксом ({self.prefixes.get(self.outputBase, "")})',
            'labelled': f'в виде "Result: {self.prefixes.get(self.outputBase, "")}число"'
        }[self.outputFormat]

        random.seed(self.seed)
        goodTest = self.generateGoodTest()
        random.seed(self.seed + 1)
        badTest = self.generateBadTest()

        exampleTable = f'''
            <table border>
                <tr>
                    <th>Входные данные</th><th>Результат</th>
                </tr>
                <tr>
                    <td>{goodTest[0]}</td><td>{goodTest[1]}</td>
                </tr>
                <tr>
                    <td>{badTest[0]}</td><td>{badTest[1]}</td>
                </tr>
            </table>
        '''

        return f'''
            Напишите программу, которая получает на вход {self.inputSize} числа в <b>{baseDict[self.inputBase]}</b> системе счисления,
            {inputFormatDescription}, и вычисляет их <b>{operationText}</b>.<br>
            Результат нужно вывести в <b>{baseDict[self.outputBase]}</b> системе счисления, {outputFormatDescription}.<br><br>
            Если хотя бы одно число не удалось считать, выведите <i>'error: #'</i>, где # — количество успешно считанных чисел.<br><br>
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
            programInput, expectedOutput, numbers = self.generateGoodTest()
            try:
                result = program.run(programInput).strip()
                if result != expectedOutput:
                    return Result.Fail(programInput, expectedOutput, result)
            except Exception as e:
                return Result.Fail(programInput, expectedOutput, str(e))

        random.seed(self.seed + 1)
        for _ in range(5):
            programInput, expectedOutput = self.generateBadTest()
            try:
                result = program.run(programInput).strip()
                if result != expectedOutput:
                    return Result.Fail(programInput, expectedOutput, result)
            except Exception as e:
                return Result.Fail(programInput, expectedOutput, str(e))

        return Result.Ok()
