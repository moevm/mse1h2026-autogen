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
    questionName = 'Сумма чисел в различных системах счисления'

    def __init__(self, *, seed, inputSize: int = 2):
        super().__init__(seed=seed, inputSize=inputSize)
        self.inputSize = inputSize

        random.seed(self.seed)
        self.inputBase = random.choice([8, 10, 16])
        self.outputBase = random.choice([x for x in [8, 10, 16] if x != self.inputBase])
        self.inputFormat = random.choice(['spaces', 'brackets', 'letters'])

    def toInput(self, x: int) -> str:
        match self.inputBase:
            case 8: return oct(x)[2:]
            case 10: return str(x)
            case 16: return hex(x)[2:]

    def toOutput(self, x: int) -> str:
        match self.outputBase:
            case 8: return oct(x)[2:]
            case 10: return str(x)
            case 16: return hex(x)[2:]

    def formatInput(self, arr: list[str]) -> str:
        match self.inputFormat:
            case 'spaces': return ' '.join(arr)
            case 'brackets': return f"({';'.join(arr)})"
            case 'letters':
                parts = [f"num{i+1}: {val}" for i, val in enumerate(arr)]
                return ', '.join(parts)

    def generateGoodTest(self) -> tuple[str, str, list[int]]:
        numbers = [random.randint(1, 500) for _ in range(self.inputSize)]
        programInput = self.formatInput([self.toInput(x) for x in numbers])
        expectedOutput = self.toOutput(sum(numbers))

        return programInput, expectedOutput, numbers

    def generateBadTest(self) -> tuple[str, str]:
        numbersCount = random.randint(0, self.inputSize-1)
        numbers = [self.toInput(random.randint(1, 500)) for _ in range(numbersCount)] + [random.choice(BAD_NUMBERS) for _ in range(self.inputSize - numbersCount)]
        programInput = self.formatInput(numbers)
        expectedOutput = f'error: {numbersCount}'

        return programInput, expectedOutput

    @property
    def questionText(self) -> str:
        baseDict = {
            8: 'восьмеричной',
            10: 'десятичной',
            16: 'шестнадцатиричной'
        }

        formatSentence = {
            'spaces': 'Все входные числа разделены <b>пробелом</b>.',
            'brackets': "Все входные числа передаются в <b>круглых</b> скобках через символ <b>';'</b>.",
            'letters': 'Перед каждым числом находится текст формата <b>numN: </b>, где N - порядковый номер. Числа разделены запятой. Например: <i>num1: 18, num2: 50</i>'
        }[self.inputFormat]

        random.seed(self.seed)
        goodTest = self.generateGoodTest()

        random.seed(self.seed+1)
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
            Напишите программу, которая принимает на вход {self.inputSize} целых чисел в <b>{baseDict[self.inputBase]}</b>
            системе счисления и выводит на экран их сумму в <b>{baseDict[self.outputBase]}</b> системе счисления. {formatSentence}<br><br>
            Если хотя бы одно из чисел не удалось считать, программа должна вывести <i>'error: #'</i>,
            где # - количество чисел, которые считать удалось.<br><br>
            Все числа положительные.<br><br>
            <b>Hint:</b> используйте значение, возвращаемое функцией <b>scanf</b>.<br><br>
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
                result = program.run(programInput)
                if int(result, self.outputBase) != sum(numbers):
                    return Result.Fail(programInput, expectedOutput, result)
            except ValueError:
                return Result.Fail(programInput, expectedOutput, result)
            except ExecutionError as e:
                return Result.Fail(programInput, expectedOutput, str(e))

        random.seed(self.seed+1)
        for _ in range(5):
            programInput, expectedOutput = self.generateBadTest()

            try:
                result = program.run(programInput)
                if result != expectedOutput:
                    return Result.Fail(programInput, expectedOutput, result)
            except ExecutionError as e:
                return Result.Fail(programInput, expectedOutput, str(e))

        return Result.Ok()