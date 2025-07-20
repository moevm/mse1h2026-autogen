from .QuestionBase import QuestionBase, Result
from .utility import CProgramRunner, ExecutionError, CompilationError
import random
import re

class QuestionN4(QuestionBase):
    questionName = 'Индексация многомерного массива и вычисление разницы плоских индексов'

    MIN_DIM_VALUE = 10
    MAX_DIM_VALUE = 100
    MIN_DIM_NUM = 3
    MAX_DIM_NUM = 4
    QUESTIONS_NUM = 2

    def __init__(self, *, seed):
        super().__init__(seed=seed)
        random.seed(self.seed)

        # Генерируем случайные размеры массива (3 или 4 измерения)
        self.arr_dims = [random.randint(self.MIN_DIM_VALUE, self.MAX_DIM_VALUE) for _ in range(random.randint(self.MIN_DIM_NUM, self.MAX_DIM_NUM))]

    def convert_index(self, multiindex: list[int], dims: list[int]) -> int:
        """
        Конвертирует многомерный индекс в плоский (линейный).
        """
        coeff = 1
        result = 0
        for index, d_size in zip(reversed(multiindex), reversed(dims)):
            result += index * coeff
            coeff *= d_size
        return result

    def generateTest(self) -> tuple[str, str]:
        """
        Генерирует входные данные и ответ к задаче.
        """
        questions = []

        for i in range(self.QUESTIONS_NUM):
            # Генерируем два случайных многомерных индекса для массива
            first_mulindex = [random.randint(0, x - 1) for x in self.arr_dims]
            second_mulindex = [random.randint(0, x - 1) for x in self.arr_dims]

            index1 = self.convert_index(first_mulindex, self.arr_dims)
            index2 = self.convert_index(second_mulindex, self.arr_dims)

            # Меняем местами, чтобы индекс1 <= индекс2
            if index1 > index2:
                index1, index2 = index2, index1
                first_mulindex, second_mulindex = second_mulindex, first_mulindex

            questions.append((first_mulindex, second_mulindex, index2 - index1))

        # Формируем строку входных данных
        input_lines = [
            f"Размеры массива: {''.join([f'[{x}]' for x in self.arr_dims])}",
        ]
        for i, (idx1, idx2, _) in enumerate(questions):
            input_lines.append(f"Вопрос {i+1}: arr{''.join([f'[{x}]' for x in idx1])} и arr{''.join([f'[{x}]' for x in idx2])}")

        input_data = '\n'.join(input_lines) + '\n'

        # Формируем ожидаемый вывод (ответы на вопросы)
        answers = [str(q[2]) for q in questions]
        expected_output = '\n'.join(answers) + '\n'

        return input_data, expected_output

    @property
    def questionText(self) -> str:
        """
        Текст задания с пояснениями.
        """
        dims_str = ''.join([f'[{x}]' for x in self.arr_dims])
        return f'''
        Вам дан многомерный массив с размерами {dims_str}.<br>
        Индексация элементов массива ведется по нескольким измерениям.<br>
        Напишите программу на C, которая:<br>
        <ol>
            <li>Для заданных двух многомерных индексов вычисляет соответствующие плоские индексы.</li>
            <li>Находит разницу между этими плоскими индексами.</li>
        </ol>
        Формат входных данных:<br>
        Первая строка содержит размеры массива.<br>
        Далее идут две строки с индексами в формате arr[...][...][...] и arr[...][...][...].<br>
        Формат вывода:<br>
        Одно число — разница плоских индексов.<br><br>
        Пример:<br>
        <pre>
        Размеры массива: {dims_str}
        Вопрос 1: arr[1][2][3] и arr[2][3][4]
        Вопрос 2: arr[0][0][0] и arr[1][1][1]

        Вывод:
        45
        20
        </pre>
        '''

    @property
    def preloadedCode(self) -> str:
        return '\n'.join([
            '#include <stdio.h>',
            '',
            'int main() {',
            '    // Реализуйте чтение входных данных и вычисление',
            '    return 0;',
            '}'
        ])

    def test(self, code: str) -> Result.Ok | Result.Fail:
        # Проверим, что не используется запрещённые библиотеки (если нужно)
        if re.search(r'#include\s*<string\.h>', code):
            raise CompilationError('Использовать <string.h> нельзя')

        program = CProgramRunner(code)

        random.seed(self.seed)
        for _ in range(5):
            programInput, expectedOutput = self.generateTest()
            try:
                result = program.run(programInput)
                if result.strip() != expectedOutput.strip():
                    return Result.Fail(programInput, expectedOutput, result)
            except ExecutionError as e:
                return Result.Fail(programInput, expectedOutput, str(e))

        return Result.Ok()
