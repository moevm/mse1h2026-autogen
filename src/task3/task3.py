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
        self.operationType = random.choice(['sum', 'product', 'mask_sum'])
        self.maxLength = 15 if self.operationType == 'product' else 100

        self.mask = None
        if self.operationType == 'mask_sum':
            self.mask = random.randint(1, 15)

    def generateTest(self) -> tuple[str, str]:
        length = random.randint(10, self.maxLength)
        borders = {
            'sum': (0, 100_000_000),
            'product': (-100, 100), 
            'mask_sum': (0, 100_000_000)
        }[self.operationType]

        numbers = [random.randint(*borders) for _ in range(length)]
        targetNumbers = numbers[(1 if self.elementType == 'odd' else 0)::2]

        if self.operationType == 'mask_sum':
            programInput = ' '.join([str(x) for x in [length, self.mask] + numbers])
        else:
            programInput = ' '.join([str(x) for x in [length] + numbers])

        match self.operationType:
            case 'sum':
                expectedOutput = sum(targetNumbers)
            case 'product':
                expectedOutput = reduce(lambda x,y: x*y, targetNumbers, 1)
            case 'mask_sum':
                expectedOutput = sum(x for x in targetNumbers if (x & self.mask) == self.mask)


        return programInput, str(expectedOutput)

    @property
    def questionText(self) -> str:
        operation = {
            'sum': 'сумму',
            'product': 'произведение',
            'mask_sum': 'сумму элементов массива, у которых установлены все биты, заданные маской M'
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
        
        extra = ''
        if self.operationType == 'mask_sum':
            extra = '<br><b>M</b> - битовая маска.'

        return f'''
            Напишите программу, на вход которой подаётся сначало число <b>N</b> (<={self.maxLength}), а после - {'<b>M</b> и ' if self.operationType == 'mask_sum' else ''}<b>N</b> целых чисел.
            {extra}
            Требуется сохранить числа в статический массив, найти и вывести на экран {operation} элементов массива с {element} индексом.<br><br>
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
