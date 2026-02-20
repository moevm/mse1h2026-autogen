from .QuestionBase import QuestionBase, Result
from .utility import CProgramRunner, ExecutionError
import random
from functools import reduce

class QuestionN3(QuestionBase):
    questionName = 'Работа с массивом различных типов данных'

    def __init__(self, *, seed):
        super().__init__(seed=seed)
        random.seed(self.seed)  # Инициализируем генератор случайных чисел фиксированным seed для повторяемости

        # Выбор типа данных из расширенного списка (~15 вариантов)
        self.dataType = random.choice([
            'char', 'unsigned char', 'short', 'unsigned short', 'int', 'unsigned int',
            'long', 'unsigned long', 'long long', 'unsigned long long',
            'float', 'double', 'long double',
            '_Bool', 'size_t'
        ])

        # Выбор типа индексов элементов массива, по которым будет выполняться операция
        self.elementType = random.choice([
            'odd',              # элементы с нечетными индексами
            'even',             # с четными индексами
            'all',              # все элементы
            'multiples_of_3',   # индексы кратные 3
            'multiples_of_5',   # индексы кратные 5
            'prime_indices'     # индексы — простые числа
        ])

        # Выбор типа операции, которую нужно выполнить над выбранными элементами
        self.operationType = random.choice([
            'sum',              # сумма
            'product',          # произведение
            'max',              # максимум
            'min',              # минимум
            'average'           # среднее арифметическое
        ])

        # Задание максимальной длины массива в зависимости от операции
        if self.operationType == 'product':
            self.maxLength = 15  # чтобы не было слишком больших произведений
        elif self.operationType == 'average':
            self.maxLength = 50
        else:
            self.maxLength = 30

    def generateNumber(self) -> float | int:
        """
        Генерирует случайное число в зависимости от выбранного типа данных.
        Для целочисленных типов возвращает int, для float-типов — округленное float.
        """
        match self.dataType:
            case 'char':
                return random.randint(-128, 127)
            case 'unsigned char':
                return random.randint(0, 255)
            case 'short':
                return random.randint(-32_768, 32_767)
            case 'unsigned short':
                return random.randint(0, 65_535)
            case 'int':
                return random.randint(-1_000_000, 1_000_000)
            case 'unsigned int':
                return random.randint(0, 1_000_000)
            case 'long':
                return random.randint(-2_000_000, 2_000_000)
            case 'unsigned long':
                return random.randint(0, 2_000_000)
            case 'long long':
                return random.randint(-10**12, 10**12)
            case 'unsigned long long':
                return random.randint(0, 10**12)
            case 'float':
                return round(random.uniform(-1000.0, 1000.0), 3)
            case 'double':
                return round(random.uniform(-1e6, 1e6), 6)
            case 'long double':
                return round(random.uniform(-1e9, 1e9), 8)
            case '_Bool':
                return random.choice([0, 1])
            case 'size_t':
                return random.randint(0, 2**32 - 1)
            case _:
                # Запасной вариант — генерация целого числа в разумных пределах
                return random.randint(-1000, 1000)

    def generateTest(self) -> tuple[str, str]:
        """
        Генерирует тестовый вход и ожидаемый результат.
        - Создает массив чисел выбранного типа.
        - Выбирает подмножество элементов согласно элементType.
        - Выполняет выбранную операцию над выбранными элементами.
        - Возвращает входные данные и отформатированный результат как строки.
        """
        length = random.randint(10, self.maxLength)  # длина массива
        numbers = [self.generateNumber() for _ in range(length)]  # генерация массива

        # Функция для проверки простоты числа (для выбора prime_indices)
        def is_prime(n):
            if n < 2:
                return False
            for i in range(2, int(n ** 0.5) + 1):
                if n % i == 0:
                    return False
            return True

        # Формируем список выбранных элементов по индексам в зависимости от elementType
        if self.elementType == 'even':
            selected = [numbers[i] for i in range(length) if i % 2 == 0]
        elif self.elementType == 'odd':
            selected = [numbers[i] for i in range(length) if i % 2 == 1]
        elif self.elementType == 'all':
            selected = numbers
        elif self.elementType == 'multiples_of_3':
            selected = [numbers[i] for i in range(length) if i % 3 == 0]
        elif self.elementType == 'multiples_of_5':
            selected = [numbers[i] for i in range(length) if i % 5 == 0]
        elif self.elementType == 'prime_indices':
            selected = [numbers[i] for i in range(length) if is_prime(i)]
        else:
            selected = numbers  # по умолчанию все элементы

        # Если выбранных элементов нет — обрабатываем по-особенному
        if not selected:
            if self.operationType == 'product':
                result = 1  # нейтральный элемент для произведения
            elif self.operationType in ['max', 'min']:
                result = 0  # если нет элементов, возвращаем 0
            else:
                result = 0  # для суммы и среднего

        else:
            # Вычисляем результат в зависимости от operationType
            match self.operationType:
                case 'sum':
                    result = sum(selected)
                case 'product':
                    result = reduce(lambda x, y: x * y, selected, 1)
                case 'max':
                    result = max(selected)
                case 'min':
                    result = min(selected)
                case 'average':
                    result = sum(selected) / len(selected)
                case _:
                    result = 0

        # Форматируем результат для вывода
        if self.dataType in ['float', 'double', 'long double']:
            expectedOutput = f'{result:.6f}'  # 6 знаков после запятой для float
        elif self.dataType == '_Bool':
            expectedOutput = str(int(bool(result)))  # 0 или 1
        else:
            expectedOutput = str(int(result))  # целочисленные типы — целое число

        # Формируем входную строку: длина + числа через пробел
        programInput = f"{length} " + ' '.join(str(x) for x in numbers)
        return programInput, expectedOutput

    @property
    def questionText(self) -> str:
        """
        Формирует текст вопроса с описанием задачи, параметрами и примером.
        """
        opText = {
            'sum': 'сумму',
            'product': 'произведение',
            'max': 'максимум',
            'min': 'минимум',
            'average': 'среднее арифметическое'
        }.get(self.operationType, self.operationType)

        indexText = {
            'odd': 'нечётным',
            'even': 'чётным',
            'all': 'всех',
            'multiples_of_3': 'индексам, кратным 3',
            'multiples_of_5': 'индексам, кратным 5',
            'prime_indices': 'простым индексам'
        }.get(self.elementType, self.elementType)

        # Генерируем пример входа и выхода
        exampleInput, exampleOutput = self.generateTest()

        # Формируем таблицу с примером
        exampleTable = f'''
            <table border>
                <tr>
                    <th>Входные данные</th><th>Результат</th>
                </tr>
                <tr>
                    <td>{exampleInput}</td><td>{exampleOutput}</td>
                </tr>
            </table>
        '''

        # Возвращаем финальный текст задачи с подсказками
        return f'''
            Напишите программу на C, которая получает число <b>N</b> (не более {self.maxLength}), затем <b>N</b> чисел типа <code>{self.dataType}</code>.<br>
            Необходимо сохранить числа в массив соответствующего типа и вычислить {opText} элементов с {indexText} индексами.<br><br>
            Тип данных: <b>{self.dataType}</b><br>
            <b>Пример</b>:<br><br>
            {exampleTable}
            Используйте правильный тип массива и корректный формат вывода.
        '''

    @property
    def preloadedCode(self) -> str:
        """
        Возвращает базовый каркас программы на C для вставки пользователем.
        """
        return '\n'.join([
            '#include <stdio.h>',
            '',
            'int main() {',
            '',
            '    return 0;',
            '}'
        ])

    def test(self, code: str) -> Result.Ok | Result.Fail:
        """
        Запускает тесты для проверяемого кода.
        Для 5 разных наборов входных данных сравнивает вывод с ожидаемым.
        Для float-типов допускает небольшую погрешность (0.01).
        Возвращает Result.Ok при успешных проверках, Result.Fail с подробностями при ошибках.
        """
        program = CProgramRunner(code)

        random.seed(self.seed)  # фиксируем seed для одинаковых тестов
        for _ in range(5):
            programInput, expectedOutput = self.generateTest()
            try:
                result = program.run(programInput)
                if self.dataType in ['float', 'double', 'long double']:
                    try:
                        result_val = float(result)
                        expected_val = float(expectedOutput)
                        if abs(result_val - expected_val) > 0.01:
                            return Result.Fail(programInput, expectedOutput, result)
                    except ValueError:
                        return Result.Fail(programInput, expectedOutput, result)
                elif self.dataType == '_Bool':
                    if result.strip() not in ['0', '1'] or result.strip() != expectedOutput:
                        return Result.Fail(programInput, expectedOutput, result)
                else:
                    if result.strip() != expectedOutput:
                        return Result.Fail(programInput, expectedOutput, result)
            except ExecutionError as e:
                return Result.Fail(programInput, expectedOutput, str(e))

        return Result.Ok()
