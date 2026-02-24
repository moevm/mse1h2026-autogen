from .QuestionBase import QuestionBase, Result
from .utility import CProgramRunner, ExecutionError
import random
import re
import string

DIGITS = '0123456789'
SYMBOLS_LOWER = 'abcdefghijklmnopqrstuvwxyz'
SYMBOLS_UPPER = SYMBOLS_LOWER.upper()

class QuestionN2(QuestionBase):
    questionName = 'Модификация строки'

    def __init__(self, *, seed, maxInputSize: int = 100):
        super().__init__(seed=seed, maxInputSize=maxInputSize)
        self.maxInputSize = maxInputSize

        random.seed(self.seed)

        self.operation = random.choice(['delete', 'shift'])

        if self.operation == 'delete':
            self.targetType = random.choice(['digits', 'upper', 'lower'])

        else:  # shift
            self.targetType = random.choice(['upper', 'lower'])
            self.direction = random.choice(['left', 'right'])
            self.shift = random.randint(1, 10)

    def process_delete(self, s: str) -> str:
        replaceRegex = {
            'digits': r'\d',
            'upper': r'[A-Z]',
            'lower': r'[a-z]'
        }[self.targetType]

        return re.sub(replaceRegex, '', s)

    def shift_char(self, ch: str) -> str:
        alphabet = SYMBOLS_LOWER if self.targetType == 'lower' else SYMBOLS_UPPER

        if ch not in alphabet:
            return ch

        index = alphabet.index(ch)

        if self.direction == 'right':
            new_index = (index + self.shift) % 26
        else:
            new_index = (index - self.shift) % 26

        return alphabet[new_index]

    def process_shift(self, s: str) -> str:
        return ''.join(self.shift_char(c) for c in s)

    def process(self, s: str) -> str:
        if self.operation == 'delete':
            return self.process_delete(s)
        else:
            return self.process_shift(s)

    def generateGoodTest(self) -> tuple[str, str]:
        length = random.randint(1, self.maxInputSize - 1)

        programInput = ''.join(random.choice(
            random.choice([
                DIGITS,
                SYMBOLS_LOWER,
                SYMBOLS_UPPER
            ])
        ) for _ in range(length))

        expectedOutput = self.process(programInput)

        return programInput, expectedOutput

    def generateBadTest(self) -> tuple[str, str]:
        length = random.randint(1, self.maxInputSize - 1)

        if self.operation == 'delete':
            groups = {
                'digits': DIGITS,
                'upper': SYMBOLS_UPPER,
                'lower': SYMBOLS_LOWER
            }
            groups.pop(self.targetType)

            pool = ''.join(groups.values())
            programInput = ''.join(random.choice(pool) for _ in range(length))
            return programInput, programInput

        else:  # shift
            if self.targetType == 'lower':
                pool = SYMBOLS_UPPER + DIGITS
            else:
                pool = SYMBOLS_LOWER + DIGITS

            programInput = ''.join(random.choice(pool) for _ in range(length))
            return programInput, programInput

    @property
    def questionText(self) -> str:
        random.seed(self.seed)
        goodTest = self.generateGoodTest()

        random.seed(self.seed + 1)
        badTest = self.generateBadTest()

        if self.operation == 'delete':
            target = {
                'digits': 'все цифры',
                'upper': 'все символы верхнего регистра',
                'lower': 'все символы нижнего регистра'
            }[self.targetType]

            description = f'удаляет <b>{target}</b>'
        else:
            directionText = 'вправо' if self.direction == 'right' else 'влево'
            targetText = 'нижнего регистра' if self.targetType == 'lower' else 'верхнего регистра'

            description = (
                f'выполняет циклический сдвиг символов '
                f'<b>{targetText}</b> на <b>{self.shift}</b> позиций '
                f'<b>{directionText}</b>'
            )

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
            Напишите программу, которая принимает строку длины 
            <b>не более {self.maxInputSize} символов</b> 
            (последним символом всегда является '\\n') и {description}.<br><br>
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
            programInput, expectedOutput = self.generateGoodTest()

            try:
                result = program.run(programInput + '\n')
                if result != expectedOutput:
                    return Result.Fail(programInput, expectedOutput, result)
            except ExecutionError as e:
                return Result.Fail(programInput, expectedOutput, str(e))

        random.seed(self.seed + 1)
        for _ in range(5):
            programInput, expectedOutput = self.generateBadTest()

            try:
                result = program.run(programInput + '\n')
                if result != expectedOutput:
                    return Result.Fail(programInput, expectedOutput, result)
            except ExecutionError as e:
                return Result.Fail(programInput, expectedOutput, str(e))


        return Result.Ok()


