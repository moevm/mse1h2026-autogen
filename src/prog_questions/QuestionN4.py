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
        super().__init__(seed=seed, inputSize=0)
        self.arraySize = arraySize

        random.seed(self.seed)
        # выбрать случайный тип из TYPES
        self.typeName = None
        self.typeSize = None
        # выбрать два случайных индекса indexA < indexB
        self.indexA = None
        self.indexB = None

    def _expected_diff(self) -> int:
        # Вычисляет ожидаемую разницу в байтах между элементами indexB и indexA.

        raise NotImplementedError

    def _check_answer(self, result: str) -> bool:
        # Проверяет ответ студента.
        # Важно: лишние пробелы не должны влиять на результат (использовать strip).

        raise NotImplementedError

    @property
    def questionText(self) -> str:
        # Генерирует HTML-текст задания.

        raise NotImplementedError

    @property
    def preloadedCode(self) -> str:
        # Возвращает заготовку кода, которую студент видит в редакторе.
        
        raise NotImplementedError

    def test(self, code: str) -> Result.Ok | Result.Fail:
        # Проверяет решение студента.
        
        raise NotImplementedError