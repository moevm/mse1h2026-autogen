from .QuestionBase import QuestionBase, Result
from .utility import CProgramRunner
import random
import time

BAD_NUMBERS = [
    'qww',
    'wolf',
    'owl',
    'xor'
]

# Const value for safe tests (less than actual max int value in C)
INT_MAX = 2_000_000_000

class QuestionN1(QuestionBase):
    questionName = 'Задание 1, Операции с числами в различных системах счисления'

    def __init__(self, *, seed, inputSize: int = None):
        super().__init__(seed=seed, inputSize=inputSize)

        random.seed(self.seed)

        self.inputSize = inputSize if inputSize else random.randint(3, 5)
        # C printf/scanf do not support binary conversion, so we exclude base 2 from input
        self.inputBase = random.choice([8, 10, 16])
        self.outputBase = random.choice([x for x in [2, 8, 10, 16] if x != self.inputBase])
        self.inputFormat = random.choice(['spaces', 'brackets', 'delimiter', 'squares', 'noise'])
        self.delimiter = random.choice([';', ',', '|'])
        self.outputFormat = random.choice(['plain', 'brackets', 'prefix', 'labelled'])
        self.operation = random.choice(['sum', 'sub', 'mul', 'div', 'mod', 'max', 'min', 'avg', 'pow'])
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
            case 'noise': return ' '.join(self.addNoise(t) for t in arr)

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
            case 'pow':
                result = nums[0]
                for x in nums[1:]:
                    result **= x 
                return result

    def addNoise(self, token: str) -> str:
        if self.inputBase == 16:
            noise_chars = "!@#$%^&*ghijklmnopqrstuvwxyz"
        else: 
            noise_chars = "!@#$%^&*abcdefghijklmnopqrstuvwxyz"
        prefix = "".join(random.choices(noise_chars, k=random.randint(0, 4)))
        suffix = "".join(random.choices(noise_chars, k=random.randint(0, 4)))
        return f"{prefix}{token}{suffix}"

    def generateTest(self, is_good: bool = True, random_bad_numbers: bool = False) -> tuple[str, str, list[int]]:
        count = self.inputSize if is_good else random.randint(0, self.inputSize - 1)

        while True:
            if self.operation == 'pow':
                numbers = [random.randint(1, 5)] + [random.randint(1, 2) for _ in range(count - 1)] if count > 0 else []
            elif self.operation == 'mul':
                numbers = [random.randint(1, 15) for _ in range(count)]
            elif self.operation == 'sub':
                # Protection from mistakes with negative nums
                numbers = [random.randint(1, 100) for _ in range(count)]
                if count > 0:
                    numbers[0] = sum(numbers[1:]) + random.randint(1, 50)
            else:
                numbers = [random.randint(1, 100) for _ in range(count)]

            if count == 0 or self.operate(numbers) <= INT_MAX:
                break

        valid = [self.toInput(x) for x in numbers]

        if is_good:
            programInput = self.formatInput(valid)
            expectedOutput = self.toOutput(self.operate(numbers))
            return programInput, expectedOutput, numbers
        
        else:
            if random_bad_numbers:
                # Generating text without [a,b,c,d,e,f] to avoid mistakes in hex
                invalid = ["".join(random.choices("ghijklmnopqrstuvwxyz", k=random.randint(2, 5))) for _ in range(self.inputSize - count)]
            else:
                invalid = [random.choice(BAD_NUMBERS) for _ in range(self.inputSize - count)]
            all_inputs = valid + invalid
            random.shuffle(all_inputs)

            programInput = self.formatInput(all_inputs)
            for i in range(self.inputSize):
                if all_inputs[i] in invalid:
                    break
            else:
                i = 0
            expectedOutput = f'error: {i}'
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
            'avg': 'среднее арифметическое, округлённое вниз',
            'pow': 'возведение в степень (первое число последовательно возводится в степень последующих чисел)'
        }[self.operation]

        inputFormatDescription = {
            'spaces': 'разделены пробелами',
            'brackets': f'в круглых скобках через символ <b>{self.delimiter}</b>',
            'delimiter': f'разделены символом <b>{self.delimiter}</b>',
            'squares': f'в квадратных скобках через символ <b>{self.delimiter}</b>',
            'noise': f'вперемешку с посторонними символами, разделены пробелами'
        }[self.inputFormat]

        outputFormatDescription = {
            'plain': 'без префиксов или скобок',
            'brackets': 'в квадратных скобках',
            'prefix': f'с префиксом ({self.prefixes.get(self.outputBase, "")})',
            'labelled': f'в виде "Result: {self.prefixes.get(self.outputBase, "")}число"'
        }[self.outputFormat]

        random.seed(self.seed)
        goodTest = self.generateTest()
        random.seed(self.seed + 1)
        badTest = self.generateTest(is_good=False)

        # Formatting table with task
        exampleTable = f'''
            <table class="coderunnerexamples">
                <thead>
                    <tr>
                        <th class="header c0" style="" scope="col">Входные данные</th>
                        <th class="header c2 lastcol" style="" scope="col">Результат</th>
                    </tr>
                </thead>
                <tbody>
                    <tr class="r0 lastrow">
                            <td class="cell  c1" style=""><pre class="tablecell">{goodTest[0]}</pre></td>
                        <td class="cell  c1" style=""><pre class="tablecell">{goodTest[1]}</pre></td>
                    </tr>
                    <tr class="r0 lastrow">
                            <td class="cell  c1" style=""><pre class="tablecell">{badTest[0]}</pre></td>
                        <td class="cell  c1" style=""><pre class="tablecell">{badTest[1]}</pre></td>
                    </tr>
                </tbody>
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

        static_tests = 3
        random_tests = 20
        random.seed(self.seed)
        for _ in range(static_tests):
            programInput, expectedOutput, _ = self.generateTest()
            try:
                result = program.run(programInput).strip()
                if result != expectedOutput:
                    return Result.Fail(programInput, expectedOutput, result)
            except Exception as e:
                return Result.Fail(programInput, expectedOutput, str(e))

        random.seed(self.seed + 1)
        for _ in range(static_tests):
            programInput, expectedOutput = self.generateTest(is_good=False)
            try:
                result = program.run(programInput).strip()
                if result != expectedOutput:
                    return Result.Fail(programInput, expectedOutput, result)
            except Exception as e:
                return Result.Fail(programInput, expectedOutput, str(e))

        random.seed(int(time.time()))
        for _ in range(random_tests):
            if random.random() < 0.5:
                programInput, expectedOutput, _ = self.generateTest()
            else:
                programInput, expectedOutput = self.generateTest(is_good=False, random_bad_numbers=True)
            try:
                result = program.run(programInput).strip()
                if result != expectedOutput:
                    return Result.Fail(programInput, expectedOutput, result)
            except Exception as e:
                return Result.Fail(programInput, expectedOutput, str(e))

        return Result.Ok()
