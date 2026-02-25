from .QuestionBase import QuestionBase, Result
from .utility import CProgramRunner, ExecutionError
import random


# определить список типов и их размеров в байтах
TYPES = [
    # ('тип', размер_в_байтах),
]


class QuestionN4(QuestionBase):
    questionName = 'Разница в байтах между элементами массива'

    def __init__(self, *, seed, arraySize: int = 5):
        super().__init__(seed=seed, arraySize=arraySize)
        self.arraySize = arraySize

        random.seed(self.seed)
        # выбрать случайный тип из TYPES
        self.typeName = 'int'
        self.typeSize = 0
        # выбрать два случайных индекса indexA < indexB
        self.indexA = 0
        self.indexB = 1

    def _expected_diff(self) -> int:
        # Вычисляет ожидаемую разницу в байтах между элементами indexB и indexA.
        return 0

    def _check_answer(self, result: str) -> bool:
        # Проверяет ответ студента.
        # Важно: лишние пробелы не должны влиять на результат (использовать strip).
        return result.strip() == str(self._expected_diff())

    @property
    def questionText(self) -> str:
        # Генерирует HTML-текст задания.
        return f'TODO: задание 4 (тип: {self.typeName}, индексы: {self.indexA}, {self.indexB})'


    @property
    def preloadedCode(self) -> str:
        # Возвращает заготовку кода, которую студент видит в редакторе.
        return '\n'.join([
            '#include <stdio.h>',
            '',
            'int main() {',
            '',
            '    return 0;',
            '}'
        ])

    def test(self, code: str) -> Result.Ok | Result.Fail:
        # Проверяет решение студента.
        program = CProgramRunner(code)
        expected = str(self._expected_diff())

        try:
            result = program.run('')
            if not self._check_answer(result):
                return Result.Fail('', expected, result.strip())
        except ExecutionError as e:
            return Result.Fail('', expected, str(e))

        return Result.Ok()