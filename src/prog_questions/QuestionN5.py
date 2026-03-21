from .QuestionBase import QuestionBase, Result
from .utility import CProgramRunner, ExecutionError, CompilationError
import random
from faker import Faker
import re
import time
import copy

fake = Faker()
AVG_WORD_SIZE = 5


class QuestionN5(QuestionBase):
    questionName = 'Задание 5, Работа с массивом строк по различным критериям'

    def __init__(self, *, seed, maxSentenceSize: int = 100):
        super().__init__(seed=seed, maxSentenceSize=maxSentenceSize)
        self.maxSentenceSize = maxSentenceSize

        random.seed(self.seed)
        Faker.seed(self.seed)

        self.metricBase = random.choice([
            'words',         # количество слов
            'length',        # длина строки
            'special_chars',  # спецсимволы
            'digit_count',   # цифры
            'vowel_count',   # гласные
            'consonant_count',  # согласные
            'uppercase_count',  # заглавные
            'lowercase_count',  # строчные
            'punctuation_count',  # знаки препинания
            'space_count',   # пробелы
            'longest_word'   # самое длинное слово
            # 'palindrome',     # палиндром с максимальной длиной (или минимальной — в зависимости от выбора)
            # 'word_length_variety', # максимальное (или минимальное) разнообразие по длине слов
        ])

        # направление: 'min' только для words и length, остальные - 'max'
        if self.metricBase in ['words', 'length']:
            self.metricDirection = random.choice(['min', 'max'])
        else:
            self.metricDirection = 'max'

        # Определяем максимальное количество слов в одной строке (учитывая средний размер слова + пробел)
        self.maxWords = self.maxSentenceSize // (AVG_WORD_SIZE + 1)

    def generateSentence(self, size: int) -> str:
        """
        Генерирует предложение заданного размера (числа слов).
        Для метрики 'special_chars' добавляет случайные спецсимволы в случайное слово.
        """
        sentence = None
        while not sentence or len(sentence) > self.maxSentenceSize:
            # Если метрика связана со словами — генерируем предложение с указанным числом слов,
            # иначе – случайное предложение с произвольным размером
            sentence = fake.sentence(size, self.metricBase in [
                                     'words', 'longest_word'])

            if self.metricBase == 'special_chars':
                # Вставляем случайное количество спецсимволов в случайное слово (если слов >1)
                extra = ''.join(random.choices(
                    '!@#$%^&*()_+=[]{}:;,.<>?', k=random.randint(1, 5)))
                words = sentence.split()
                if len(words) > 1:
                    i = random.randint(1, len(words) - 1)
                    words[i] += extra
                    sentence = ' '.join(words)

            # Для палиндромов (если используется эта метрика), можно было бы дополнительно генерировать,
            # но для простоты оставим обычные предложения

        sentence = re.sub(r'[^a-zA-Z0-9 .,!?]', '', sentence)
        return sentence

    def getMetric(self, sentence: str) -> int:
        """
        Рассчитывает значение метрики для конкретной строки.
        """
        # Вспомогательные функции
        def count_vowels(s):
            return sum(ch.lower() in 'aeiou' for ch in s)

        def count_consonants(s):
            return sum(ch.isalpha() and ch.lower() not in 'aeiou' for ch in s)

        def count_digits(s):
            return sum(ch.isdigit() for ch in s)

        def count_punctuation(s):
            # Считаем знаки препинания по строке, используя простой шаблон
            return sum(ch in '.,;:!?-—()[]{}"\'' for ch in s)

        def count_spaces(s):
            return s.count(' ')

        def is_palindrome(s):
            # Проверяем строку без пробелов и регистра
            s_clean = ''.join(ch.lower() for ch in s if ch.isalnum())
            return s_clean == s_clean[::-1]

        def word_length_variety(s):
            lengths = set(len(word.strip('.,!?')) for word in s.split())
            return len(lengths)

        def longest_word_length(s):
            return max(len(word.strip('.,!?')) for word in s.split())

        match self.metricBase:
            case 'words':
                return len(sentence.split())
            case 'length':
                return len(sentence)
            case 'special_chars':
                return sum(1 for c in sentence if not c.isalnum() and c not in [' ', '\n'])
            case 'digit_count':
                return count_digits(sentence)
            case 'vowel_count':
                return count_vowels(sentence)
            case 'consonant_count':
                return count_consonants(sentence)
            case 'uppercase_count':
                return sum(c.isupper() for c in sentence)
            case 'lowercase_count':
                return sum(c.islower() for c in sentence)
            case 'punctuation_count':
                return count_punctuation(sentence)
            case 'space_count':
                return count_spaces(sentence)
            case 'longest_word':
                return longest_word_length(sentence)
            case 'palindrome':
                # Возвращаем длину строки, если это палиндром, иначе 0 (для max/min палиндромов)
                return len(sentence) if is_palindrome(sentence) else 0
            case 'word_length_variety':
                return word_length_variety(sentence)
            case _:
                return 0

    def generateTest(self) -> tuple[str, str]:
        """
        Генерирует тестовый набор данных и вычисляет ожидаемый результат.
        """
        quantity = random.randint(2, self.maxWords)  # число строк
        sentenceSizes = list(range(1, self.maxWords + 1))
        random.shuffle(sentenceSizes)
        sentenceSizes = sentenceSizes[:quantity]

        # Генерируем предложения с заданным числом слов
        sentences = [self.generateSentence(size) for size in sentenceSizes]

        # Вычисляем метрики для каждого предложения
        metrics = [(self.getMetric(s), s) for s in sentences]

        # Находим предложение с максимальным/минимальным значением метрики
        if self.metricDirection == 'max':
            bestMetric, bestSentence = max(metrics, key=lambda x: x[0])
        else:
            bestMetric, bestSentence = min(metrics, key=lambda x: x[0])

        # Формируем входные данные (количество строк + сами строки)
        programInput = f"{len(sentences)}\n" + '\n'.join(sentences) + '\n'
        # Форматируем ожидаемый вывод
        expectedOutput = f'{bestMetric}: {bestSentence}'

        return programInput, expectedOutput

    @property
    def questionText(self) -> str:
        """
        Возвращает текст задания с описанием условия, включая пример.
        """
        metricBaseDescriptions = {
            'words': 'числом слов',
            'length': 'длиной',
            'special_chars': 'числом спецсимволов (не букв/цифр/пробелов)',
            'digit_count': 'количеством цифр',
            'vowel_count': 'количеством гласных букв (a, e, i, o, u)',
            'consonant_count': 'количеством согласных букв',
            'uppercase_count': 'количеством заглавных букв',
            'lowercase_count': 'количеством строчных букв',
            'punctuation_count': 'количеством знаков препинания',
            'space_count': 'количеством пробелов',
            'longest_word': 'длиной самого длинного слова'
        }

        directionDescriptions = {
            'max': 'наибольшим',
            'min': 'наименьшим'
        }

        metricDescription = f'строку с <b>{directionDescriptions[self.metricDirection]}</b> {metricBaseDescriptions[self.metricBase]}'

        extraDescription = ''
        if self.metricBase in ['words', 'longest_word']:
            extraDescription = '''
                Предложение состоит из слов (слово == последовательность любых символов, <b>кроме символов пробела и точки</b>),
                разделённых ровно одним символом пробела, и заканчивается символом точки.<br>
            '''
        elif self.metricBase == 'special_chars':
            extraDescription = '''
                Спецсимволы — это любые символы, не являющиеся буквами, цифрами или пробелами.<br>
            '''
        elif self.metricBase == 'palindrome':
            extraDescription = '''
                Палиндром — строка, которая читается одинаково слева направо и справа налево без учета регистра и пробелов.<br>
            '''

        Faker.seed(self.seed)
        random.seed(self.seed)
        saved_max_ssize = self.maxWords
        self.maxWords = 5
        tests = self.generateTest(), self.generateTest()
        self.maxWords = saved_max_ssize
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
                        <td class="cell  c1" style=""><pre class="tablecell">{tests[0][0].replace(chr(10), '</p><p>')}</pre></td>
                        <td class="cell  c1" style=""><pre class="tablecell">{tests[0][1]}</pre></td>
                    </tr>
                    <tr class="r0 lastrow">
                        <td class="cell  c1" style=""><pre class="tablecell">{tests[1][0].replace(chr(10), '</p><p>')}</pre></td>
                        <td class="cell  c1" style=""><pre class="tablecell">{tests[1][1]}</pre></td>
                    </tr>
                </tbody>
            </table>
        '''

        return f'''
            На вход программе подаётся число <b>N</b> — количество строк, затем <b>N строк</b>, каждая длиной не более <b>{self.maxSentenceSize} символов</b>. Каждая строка заканчивается символом '\\n'.<br><br>
            {extraDescription}
            Напишите программу, которая:
            <ol>
                <li>Считывает <b>N строк</b> из входного потока</li>
                <li>Находит {metricDescription}</li>
                <li>Выводит результат в формате: <b>&lt;значение&gt;: строка</b></li>
            </ol>
            <b>Нельзя использовать библиотеку <code>&lt;string.h&gt;</code></b><br><br>
            {exampleTable}
        '''

    @property
    def preloadedCode(self) -> str:
        """
        Возвращает шаблон C-программы, который будет предоставлен участникам.
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
        Тестирует скомпилированный код на нескольких сгенерированных тестах.
        Проверяет запрещённый include <string.h>.
        """
        # Проверяем наличие запрещённого include
        if re.search(r'#include.*string\.h', code) or re.search(r'#undef\s+_STRING_H', code):
            raise CompilationError('Использовать &lt;string.h&gt; нельзя')

        # Добавляем защиту от случайного включения <string.h> при компиляции
        modifiedCode = f'''
            {code}

            #ifdef _STRING_H
            #error You cannot include <string.h>
            #endif
        '''

        try:
            program = CProgramRunner(modifiedCode)
        except CompilationError as e:
            if 'You cannot include <string.h>' in str(e):
                raise CompilationError('Использовать &lt;string.h&gt; нельзя')
            raise

        Faker.seed(self.seed)
        random.seed(self.seed)
        for _ in range(5):
            programInput, expectedOutput = self.generateTest()
            try:
                result = program.run(programInput)
                if result != expectedOutput:
                    return Result.Fail(programInput, expectedOutput, result)
            except ExecutionError as e:
                return Result.Fail(programInput, expectedOutput, str(e))

        seed = int(time.time())
        Faker.seed(seed)
        random.seed(seed)
        for _ in range(20):
            programInput, expectedOutput = self.generateTest()
            try:
                result = program.run(programInput)
                if result != expectedOutput:
                    return Result.Fail(programInput, expectedOutput, result)
            except ExecutionError as e:
                return Result.Fail(programInput, expectedOutput, str(e))

        return Result.Ok()
