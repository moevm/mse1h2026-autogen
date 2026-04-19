from .QuestionBase import QuestionBase, Result
from .utility import CProgramRunner, ExecutionError
import random
import re
import time

# Константы для работы с символами
DIGITS = '0123456789'
SYMBOLS_LOWER = 'abcdefghijklmnopqrstuvwxyz'
SYMBOLS_UPPER = SYMBOLS_LOWER.upper()
VOWELS = 'aeiouyAEIOUY'  # Гласные буквы (нижний и верхний регистр)

class QuestionN2(QuestionBase):
    questionName = 'Задание 2, Операции над строками'  # Название задачи

    def __init__(self, *, seed, maxInputSize: int = 100, operation: str = None):
        super().__init__(seed=seed, maxInputSize=maxInputSize)
        self.maxInputSize = maxInputSize

        # Устанавливаем seed для повторяемости выбора операции
        random.seed(self.seed)
        # Случайно выбираем операцию для обработки строки
        self.operation = random.choice([ 
            'remove_digits',          # удалить все цифры
            'remove_upper',           # удалить все символы верхнего регистра
            'remove_lower',           # удалить все символы нижнего регистра
            'keep_digits',            # оставить только цифры
            'to_upper',               # преобразовать в верхний регистр
            'to_lower',               # преобразовать в нижний регистр
            'replace_digits_star',    # заменить все цифры на '*'
            'remove_non_alpha',       # удалить все, кроме букв
            'remove_non_alnum',       # удалить все, кроме букв и цифр
            'replace_vowels_dash',    # заменить гласные на '-'
            'double_letters',         # удвоить все буквы
            'reverse',                # обратить строку
            'remove_vowels',          # удалить гласные буквы
            'remove_consonants',      # удалить согласные буквы
            'replace_spaces_underscore', # заменить пробелы на '_'
            'count_digits',           # посчитать цифры и вывести их количество
            'count_upper',            # посчитать заглавные буквы
            'count_lower',            # посчитать строчные буквы
            'sort_chars',             # отсортировать символы строки
            'unique_chars',           # удалить повторяющиеся символы, оставить первые
            'caesar_cipher'           # шифр цезаря
        ])

    # Применение выбранной операции к строке
    def applyOperation(self, s: str) -> str:
        match self.operation: 
            case 'remove_digits':
                return re.sub(r'\d', '', s)  # удалить цифры
            case 'remove_upper':
                return re.sub(r'[A-Z]', '', s)  # удалить заглавные буквы
            case 'remove_lower':
                return re.sub(r'[a-z]', '', s)  # удалить строчные буквы
            case 'keep_digits':
                return ''.join(filter(str.isdigit, s))  # оставить только цифры
            case 'to_upper':
                return s.upper()  # в верхний регистр
            case 'to_lower':
                return s.lower()  # в нижний регистр
            case 'replace_digits_star':
                return re.sub(r'\d', '*', s)  # цифры заменить на '*'
            case 'remove_non_alpha':
                return ''.join(c for c in s if c.isalpha())  # оставить только буквы
            case 'remove_non_alnum':
                return ''.join(c for c in s if c.isalnum())  # оставить буквы и цифры
            case 'replace_vowels_dash':
                return ''.join('-' if c in VOWELS else c for c in s)  # гласные на '-'
            case 'double_letters':
                return ''.join(c*2 if c.isalpha() else c for c in s)  # удвоить буквы
            case 'reverse':
                return s[::-1]  # перевернуть строку
            case 'remove_vowels':
                return ''.join(c for c in s if c not in VOWELS)  # удалить гласные
            case 'remove_consonants':
                # оставить только не согласные (т.е. удалить согласные)
                return ''.join(c for c in s if not (c.isalpha() and c not in VOWELS))
            case 'replace_spaces_underscore':
                return s.replace(' ', '_')  # пробелы заменить на '_'
            case 'count_digits':
                return str(sum(1 for c in s if c.isdigit()))  # количество цифр в строке
            case 'count_upper':
                return str(sum(1 for c in s if c.isupper()))  # количество заглавных
            case 'count_lower':
                return str(sum(1 for c in s if c.islower()))  # количество строчных
            case 'sort_chars':
                return ''.join(sorted(s))  # сортировка символов
            case 'unique_chars':
                seen = set()
                # оставить только первые вхождения символов
                return ''.join(c for c in s if not (c in seen or seen.add(c)))
            case 'caesar_cipher':  # шифр цезаря, сдвиг по seed
                shift_rng = random.Random(self.seed + 1000)
                shift = shift_rng.randint(1, 5)
                result = []

                for c in s:
                    if 'a' <= c <= 'z':
                        result.append(chr((ord(c) - ord('a') + shift) % 26 + ord('a')))
                    elif 'A' <= c <= 'Z':
                        result.append(chr((ord(c) - ord('A') + shift) % 26 + ord('A')))
                    else:
                        result.append(c)

                return ''.join(result)
            case _:
                return s  # если операция не распознана, вернуть без изменений

    # Генерация корректного теста: случайная строка и результат операции
    def generateGoodTest(self) -> tuple[str, str]:
        length = random.randint(1, self.maxInputSize - 1)
        allowed_chars = DIGITS + SYMBOLS_LOWER + SYMBOLS_UPPER + ' _-+=@#$%^&*()[]{}'
        inputString = ''.join(random.choices(allowed_chars, k=length))
        outputString = self.applyOperation(inputString)
        return inputString, outputString

    # Генерация "плохого" теста — специально составленного для проверки краевых случаев
    def generateBadTest(self) -> tuple[str, str]:
        # В зависимости от операции генерируем подходящую строку для проверки
        if self.operation == 'keep_digits' or self.operation == 'remove_digits':
            inputString = ''.join(random.choices(SYMBOLS_LOWER + SYMBOLS_UPPER, k=random.randint(1, self.maxInputSize - 1)))
        elif self.operation == 'to_upper':
            inputString = ''.join(random.choices(SYMBOLS_UPPER, k=random.randint(1, self.maxInputSize - 1)))
        elif self.operation == 'to_lower':
            inputString = ''.join(random.choices(SYMBOLS_LOWER, k=random.randint(1, self.maxInputSize - 1)))
        elif self.operation == 'replace_digits_star':
            inputString = ''.join(random.choices(SYMBOLS_LOWER + SYMBOLS_UPPER, k=random.randint(1, self.maxInputSize - 1)))
        elif self.operation == 'remove_non_alpha':
            inputString = ''.join(random.choices(SYMBOLS_LOWER + SYMBOLS_UPPER, k=random.randint(1, self.maxInputSize - 1)))
        elif self.operation == 'remove_non_alnum':
            inputString = ''.join(random.choices(DIGITS + SYMBOLS_LOWER + SYMBOLS_UPPER, k=random.randint(1, self.maxInputSize - 1)))
        elif self.operation == 'replace_vowels_dash':
            inputString = ''.join(random.choices([c for c in SYMBOLS_LOWER + SYMBOLS_UPPER if c not in VOWELS], k=random.randint(1, self.maxInputSize - 1)))
        elif self.operation == 'double_letters':
            inputString = ''.join(random.choices(DIGITS + ' !@#$%^&*', k=random.randint(1, self.maxInputSize - 1)))
        elif self.operation == 'reverse':
            inputString = ''.join(random.choices(SYMBOLS_LOWER + SYMBOLS_UPPER + DIGITS, k=1))
        elif self.operation == 'remove_vowels':
            inputString = ''.join(c for c in ''.join(random.choices(SYMBOLS_LOWER, k=10)) if c not in VOWELS)
        elif self.operation == 'remove_consonants':
            inputString = ''.join(c for c in ''.join(random.choices(SYMBOLS_LOWER, k=10)) if c in VOWELS)
        elif self.operation == 'replace_spaces_underscore':
            inputString = ''.join(random.choices(DIGITS + SYMBOLS_LOWER, k=10))
        elif self.operation == 'count_digits':
            inputString = ''.join(random.choices(SYMBOLS_LOWER + SYMBOLS_UPPER, k=10))
        elif self.operation == 'count_upper':
            inputString = ''.join(random.choices(SYMBOLS_LOWER + DIGITS, k=10))
        elif self.operation == 'count_lower':
            inputString = ''.join(random.choices(SYMBOLS_UPPER + DIGITS, k=10))
        elif self.operation == 'sort_chars':
            inputString = ''.join(random.choices(SYMBOLS_LOWER + SYMBOLS_UPPER + DIGITS, k=1))
        elif self.operation == 'unique_chars':
            inputString = ''.join(dict.fromkeys(''.join(random.choices(SYMBOLS_LOWER + DIGITS, k=5))))
        elif self.operation == 'caesar_cipher':
            inputString = ''.join(random.choices(DIGITS + '!@#$%^&*', k=5))
        else:
            inputString = 'Test123'  # на всякий случай

        return inputString, self.applyOperation(inputString)

    # Текст задачи с описанием операции и примерами
    @property
    def questionText(self) -> str:
        operationDescriptions = {
            'remove_digits': 'удаляет <b>все цифры</b>',
            'remove_upper': 'удаляет <b>все символы верхнего регистра</b>',
            'remove_lower': 'удаляет <b>все символы нижнего регистра</b>',
            'keep_digits': 'оставляет <b>только цифры</b>',
            'to_upper': 'преобразует строку в <b>верхний регистр</b>',
            'to_lower': 'преобразует строку в <b>нижний регистр</b>',
            'replace_digits_star': 'заменяет <b>все цифры на символ *</b>',
            'remove_non_alpha': 'удаляет <b>все символы, кроме латинских букв</b>',
            'remove_non_alnum': 'удаляет <b>все, кроме букв и цифр</b>',
            'replace_vowels_dash': 'заменяет <b>все гласные на тире (-)</b>',
            'double_letters': 'удваивает <b>все буквы</b>',
            'reverse': 'разворачивает строку в обратном порядке',
            'remove_vowels': 'удаляет <b>все гласные буквы</b>',
            'remove_consonants': 'удаляет <b>все согласные буквы</b>',
            'replace_spaces_underscore': 'заменяет <b>все пробелы на подчёркивания</b>',
            'count_digits': 'выводит <b>количество цифр</b> в строке',
            'count_upper': 'выводит <b>количество символов верхнего регистра</b>',
            'count_lower': 'выводит <b>количество символов нижнего регистра</b>',
            'sort_chars': 'сортирует <b>все символы строки по возрастанию</b>',
            'unique_chars': 'удаляет <b>повторяющиеся символы</b>, оставляя только первые вхождения',
            'caesar_cipher': 'шифрует строку <b>шифром Цезаря</b>'
        }

        # Hack to generate not long strings in example
        save_max_size = self.maxInputSize
        self.maxInputSize = 20
        # Генерируем тесты с использованием фиксированных seed для повторяемости
        random.seed(self.seed)
        goodTest = self.generateGoodTest()
        random.seed(self.seed + 1)
        badTest = self.generateBadTest()

        self.maxInputSize = save_max_size

        # Формируем HTML-таблицу с примерами входных данных и результатов
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

        # Возвращаем полный текст условия с описанием и примером
        return f'''
            Напишите программу, которая получает строку длиной <b>не более {self.maxInputSize} символов</b>
            и {operationDescriptions[self.operation]}.<br>
            Последним символом во входной строке всегда является символ новой строки '\\n'.<br><br>
            Пример:
            {exampleTable}
        '''

    # Заготовка кода на C для начала решения
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

    # Тестирование решения пользователя
    def test(self, code: str) -> Result.Ok | Result.Fail:
        program = CProgramRunner(code)

        # Проверяем 5 корректных тестов 
        random.seed(self.seed)
        for _ in range(3):
            programInput, expectedOutput = self.generateGoodTest()
            try:
                result = program.run(programInput + '\n')  # добавляем символ новой строки в конце
                if result != expectedOutput:
                    return Result.Fail(programInput, expectedOutput, result)  # неверный результат
            except ExecutionError as e:
                return Result.Fail(programInput, expectedOutput, str(e))  # ошибка выполнения

        # Проверяем 5 "плохих" тестов
        random.seed(self.seed + 1)
        for _ in range(3):
            programInput, expectedOutput = self.generateBadTest()
            try:
                result = program.run(programInput + '\n')
                if result != expectedOutput:
                    return Result.Fail(programInput, expectedOutput, result)
            except ExecutionError as e:
                return Result.Fail(programInput, expectedOutput, str(e))

        random.seed(int(time.time()))
        for _ in range(30):
            programInput, expectedOutput = self.generateGoodTest() if random.random() < 0.7 else self.generateBadTest()
            try:
                result = program.run(programInput + '\n')
                if result.strip() != expectedOutput.strip():
                    return Result.Fail(programInput, expectedOutput, result)
            except ExecutionError as e:
                return Result.Fail(programInput, expectedOutput, str(e))

        # Если все тесты пройдены успешно
        return Result.Ok()