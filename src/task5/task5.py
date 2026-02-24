from .QuestionBase import QuestionBase, Result
from .utility import CProgramRunner, ExecutionError, CompilationError
import random
from faker import Faker
import re

fake = Faker()
AVG_WORD_SIZE = 5


class QuestionN5(QuestionBase):
    questionName = 'Работа с массивом строк'

    def __init__(self, *, seed, maxSentenceSize: int = 100):
        super().__init__(seed=seed, maxSentenceSize=maxSentenceSize)
        self.maxSentenceSize = maxSentenceSize

        random.seed(self.seed)
        self.criteria_list = [
            {'type': 'length', 'mode': 'max',
                'text_type': 'длиной', 'text_mode': 'наибольшей'},
            {'type': 'length', 'mode': 'min',
                'text_type': 'длиной', 'text_mode': 'наименьшей'},
            {'type': 'words',  'mode': 'max',
                'text_type': 'количеством слов', 'text_mode': 'наибольшим'},
            {'type': 'words',  'mode': 'min',
                'text_type': 'количеством слов', 'text_mode': 'наименьшим'},
        ]
        self.current_criterion = random.choice(self.criteria_list)
        self.metricType = self.current_criterion['type']
        self.maxWords = self.maxSentenceSize // (AVG_WORD_SIZE+1)

    def generateSentence(self, size: int) -> str:
        sentence = None
        while not sentence or len(sentence) > self.maxSentenceSize:
            sentence = fake.sentence(size, self.metricType == 'words')

        return sentence

    def generateTest(self) -> tuple[str, str]:
        quantity = random.randint(2, self.maxWords)
        sentenceSizes = list(range(1, self.maxWords + 1))
        random.shuffle(sentenceSizes)
        sentenceSizes = sentenceSizes[:quantity]

        sentences = [self.generateSentence(size) for size in sentenceSizes]

        metric = {
            'length': lambda x: len(x),
            'words': lambda x: len(x.split())
        }[self.metricType]
        metricDict = {metric(sentence): sentence for sentence in sentences}

        quantity = len(metricDict)
        if self.current_criterion['mode'] == 'max':
            bestMetric = max(metricDict.keys())
        else:
            bestMetric = min(metricDict.keys())
        sentences = list(metricDict.values())
        random.shuffle(sentences)
        programInput = f"{quantity}\n{chr(10).join(sentences)}\n"
        expectedOutput = f'{bestMetric}: {metricDict[bestMetric]}'

        return programInput, expectedOutput

    @property
    def questionText(self) -> str:
        extraDescription = {
            'length': '',
            'words': '''
                Предложение состоит из слов (слово == последовательность любых  символов, <b>кроме символов пробела и точки</b>),
                разделённых ровно одним символом пробела, и оканчивающееся символом точки.<br>
                '''
        }[self.metricType]

        metricTask = f'''
            <li>Находит строку с <b>{self.current_criterion['text_mode']} {self.current_criterion['text_type']}</b> из всего текста 
                (гарантируется, что строк с одинаковым значением критерия нет во входных данных)</li>
            <li>Выводит эту строку и её значение критерия в консоль в формате: <b>&lt;Значение&gt;: строка</b></li>
            '''

        Faker.seed(self.seed)
        random.seed(self.seed)
        tests = self.generateTest(), self.generateTest()

        exampleTable = f'''
            <table border>
                <tr>
                    <th>Входные данные</th><th>Результат</th>
                </tr>
                <tr>
                    <td><p>{tests[0][0].replace(chr(10), '</p><p>')}</p></td><td>{tests[0][1]}</td>
                </tr>
                <tr>
                    <td><p>{tests[1][0].replace(chr(10), '</p><p>')}</p></td><td>{tests[1][1]}</td>
                </tr>
            </table>
            '''

        return f'''
            На вход программе подаётся строка, содержащая число <b>N - число строк</b> в тексте и заканчивающаяся на символ переноса строки '\\n'.
            Затем подаётся текст. Текстом является последовательность строк (строка == набор символов до '\\n' <b>не включая</b>, длиной <b>не более {self.maxSentenceSize} символов</b>),
            содержащих <b>ровно одно</b> предложение.<br>
            {extraDescription}<br>
            Напишите программу, которая:
            <ol>
                <li>Построчно считывает текста с количеством строк <b>N</b></li>
                {metricTask}
            </ol><br>
            <b>Нельзя пользоваться библиотечными функциями</b><br><br>
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
        if re.search(r'#include.*string\.h.+', code) or re.search(r'#undef\s+_STRING_H', code):
            raise CompilationError('Использовать &lt;string.h&gt; нельзя')

        modifiedCode = f'''
            {code}
            {chr(10)*5}
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
                if result.strip() != expectedOutput.strip():
                    return Result.Fail(programInput, expectedOutput, result)
            except ExecutionError as e:
                return Result.Fail(programInput, expectedOutput, str(e))

        return Result.Ok()
