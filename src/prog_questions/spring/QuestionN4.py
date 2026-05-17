from ..QuestionBase import QuestionBase, Result
from ..utility import CppProgramRunner, CompilationError, ExecutionError, InternalError
import random
from textwrap import dedent
import subprocess
import os
import sys
from collections import defaultdict, Counter

# 4.1 Группировка по ключу
class Task41:
    def __init__(self, seed: int, strictness: float):
        random.seed(seed)
        self.strictness = strictness
        
        self.words_pool = ['apple', 'ant', 'apricot', 'banana', 'bat', 'bear', 
                          'cat', 'car', 'cup', 'dog', 'duck', 'deer', 'elephant']
        
        word_count = random.randint(8, 20)
        self.input_words = [random.choice(self.words_pool) for _ in range(word_count)]
        
        complexity_types = ['none', 'min_count', 'max_count', 'exact_count', 'letter_filter']
        self.complexity = random.choice(complexity_types)
        
        if self.complexity == 'none':
            self.filter_desc = ""
            self.filter_func = lambda count, letter: True
        elif self.complexity == 'min_count':
            self.threshold = random.randint(2, 4)
            self.filter_desc = f"Выводите только буквы, у которых {self.threshold} или более слов."
            self.filter_func = lambda count, letter: count >= self.threshold
        elif self.complexity == 'max_count':
            self.threshold = random.randint(2, 4)
            self.filter_desc = f"Выводите только буквы, у которых не более {self.threshold} слов."
            self.filter_func = lambda count, letter: count <= self.threshold
        elif self.complexity == 'exact_count':
            self.threshold = random.randint(2, 3)
            self.filter_desc = f"Выводите только буквы, у которых ровно {self.threshold} слов."
            self.filter_func = lambda count, letter: count == self.threshold
        else:  # letter_filter
            self.allowed_letters = set(random.sample('abcdefg', k=random.randint(2, 4)))
            self.filter_desc = f"Выводите только буквы: {', '.join(sorted(self.allowed_letters))}."
            self.filter_func = lambda count, letter: letter in self.allowed_letters

    def generate_input(self) -> str:
        return ' '.join(self.input_words) + ' #'

    def generate_expected_output(self) -> str:
        groups = defaultdict(list)
        for w in self.input_words:
            if w:
                groups[w[0]].append(w)
        
        lines = []
        for letter in sorted(groups.keys()):
            if not self.filter_func(len(groups[letter]), letter):
                continue
            words_sorted = sorted(groups[letter])
            lines.append(f"{letter}: {' '.join(words_sorted)}")
        return '\n'.join(lines) if lines else "NO_DATA"

    def _get_input_format_description(self) -> str:
        return """<p><b>Формат входных данных:</b></p>
<ul>
    <li>Строка слов через пробел</li>
    <li>Окончание ввода: символ <code>#</code></li>
</ul>"""

    def _get_output_format_description(self) -> str:
        desc = """<p><b>Формат выходных данных:</b></p>
<p><code>&lt;буква&gt;: &lt;слово1&gt; &lt;слово2&gt; ...</code></p>
<ul>
    <li>Группы отсортированы по букве.</li>
    <li>Слова внутри группы отсортированы лексикографически.</li>
</ul>
<p><i>Если после фильтрации не осталось ни одной группы, выведите <code>NO_DATA</code>.</i></p>"""
        return desc

    def _get_example_table(self) -> str:
        inp = "apple ant banana bat cat #"
        out = "a: ant apple\nb: banana bat\nc: cat"
        note = "Группировка по первой букве, сортировка внутри"
        
        return f'''
<b>Пример</b>
<table class="coderunnerexamples">
    <thead>
        <tr>
            <th class="header c0" scope="col">Входные данные</th>
            <th class="header c1" scope="col">Результат</th>
            <th class="header c2 lastcol" scope="col">Пояснение</th>
        </tr>
    </thead>
    <tbody>
        <tr class="r0 lastrow">
            <td class="cell c0"><pre class="tablecell">{inp}</pre></td>
            <td class="cell c1"><pre class="tablecell">{out}</pre></td>
            <td class="cell c2 lastcol">{note}</td>
        </tr>
    </tbody>
</table>'''

    @property
    def question_text(self) -> str:
        header = "<p>Язык: <b>C++</b> (компиляция <code>g++</code>), тема: <b>Группировка по ключу</b>.</p>"
        
        condition = """<p>Считайте строку слов, записанных через пробел (в конце строки <code>#</code>), 
и сгруппируйте их по первой букве.</p>
<p>Для каждой буквы, у которой есть хотя бы одно слово, выведите букву и все 
соответствующие слова в лексикографическом порядке.</p>"""
        
        if self.filter_desc:
            condition += f'<p><b>Дополнительное условие:</b> {self.filter_desc}</p>'
        
        return dedent(f"{header}{condition}{self._get_input_format_description()}{self._get_output_format_description()}{self._get_example_table()}")

    @property
    def preloaded_code(self) -> str:
        return """#include <iostream>
#include <string>
#include <map>
#include <vector>
#include <algorithm>
#include <sstream>

using namespace std;

int main() {
    // Ваш код
    return 0;
}
"""

    def test(self, code: str) -> Result.Ok | Result.Fail:
        runner = CppProgramRunner(code)
        input_data = self.generate_input()
        expected = self.generate_expected_output().strip()
        
        try:
            output = runner.run(input_data).replace('\r', '').strip()
        except ExecutionError as e:
            return Result.Fail(input_data, expected, str(e))
        
        if output == expected:
            return Result.Ok()
        return Result.Fail(input_data, expected, output)


# 4.2 Частотный фильтр с маской
class Task42:
    def __init__(self, seed: int, strictness: float):
        random.seed(seed)
        self.strictness = strictness
        
        self.operation = random.choice(['shift', 'and'])
        self.mask = random.choice([0x03, 0x05, 0x0F, 0x07])
        self.min_freq = random.randint(2, 3)
        
        self.numbers = []
        for _ in range(random.randint(3, 6)):
            num = random.randint(1, 200)
            if random.random() < 0.6:
                num = (num | self.mask)
            freq = random.randint(self.min_freq, self.min_freq + 2)
            self.numbers.extend([num] * freq)
        
        for _ in range(random.randint(5, 15)):
            self.numbers.append(random.randint(1, 200))
        
        random.shuffle(self.numbers)

    def generate_input(self) -> str:
        return ' '.join(map(str, self.numbers)) + ' 0'

    def generate_expected_output(self) -> str:
        freq = Counter(self.numbers)
        
        results = []
        for num in sorted(freq.keys()):
            count = freq[num]
            if count < self.min_freq:
                continue
            if (num & self.mask) != self.mask:
                continue
            
            if self.operation == 'shift':
                result_val = num << count
            else:
                result_val = num & self.mask
            
            results.append(f"{num} {count} {result_val}")
        
        return '\n'.join(results) if results else "NO_DATA"

    def _get_input_format_description(self) -> str:
        return """<p><b>Формат входных данных:</b></p>
<ul>
    <li>Поток целых неотрицательных чисел через пробел</li>
    <li>Окончание ввода: число <code>0</code> (не обрабатывается)</li>
</ul>"""

    def _get_output_format_description(self) -> str:
        op_desc = "побитовый сдвиг влево на количество вхождений" if self.operation == 'shift' else "побитовое И с маской"
        return f"""<p><b>Формат выходных данных:</b></p>
<p><code>&lt;число&gt; &lt;частота&gt; &lt;результат&gt;</code></p>
<ul>
    <li>Вывод отсортирован по возрастанию исходного числа.</li>
    <li>Результат вычисляется как: {op_desc}.</li>
</ul>
<p><i>Если после фильтрации не осталось ни одного числа, выведите <code>NO_DATA</code>.</i></p>"""

    def _get_example_table(self) -> str:
        inp = "3 3 3 5 5 0"
        out = "3 3 24"
        note = f"Маска 0x{self.mask:02X}, операция: {'shift' if self.operation == 'shift' else 'AND'}"
        
        return f'''
<b>Пример</b>
<table class="coderunnerexamples">
    <thead>
        <tr>
            <th class="header c0" scope="col">Входные данные</th>
            <th class="header c1" scope="col">Результат</th>
            <th class="header c2 lastcol" scope="col">Пояснение</th>
        </tr>
    </thead>
    <tbody>
        <tr class="r0 lastrow">
            <td class="cell c0"><pre class="tablecell">{inp}</pre></td>
            <td class="cell c1"><pre class="tablecell">{out}</pre></td>
            <td class="cell c2 lastcol">{note}</td>
        </tr>
    </tbody>
</table>'''

    @property
    def question_text(self) -> str:
        header = "<p>Язык: <b>C++</b> (компиляция <code>g++</code>), тема: <b>Частотный фильтр с маской</b>.</p>"
        
        op_desc = "побитовый сдвиг влево на количество вхождений (num << count)" if self.operation == 'shift' else "побитовое И с маской (num & mask)"
        op_code = "num << count" if self.operation == 'shift' else f"num & 0x{self.mask:02X}"
        
        condition = f"""<p>Считайте поток целых неотрицательных чисел. Подсчитайте частоту каждого числа.</p>
<p>Выведите только те числа, которые:</p>
<ol>
    <li>Встретились <b>{self.min_freq} или более раз</b></li>
    <li>У которых установлен бит(ы) маски <code>0x{self.mask:02X}</code> (проверка: <code>(num & 0x{self.mask:02X}) == 0x{self.mask:02X}</code>)</li>
</ol>
<p>Для каждого подходящего числа выведите: исходное число, количество вхождений и результат операции <b>{op_desc}</b>.</p>
<p>Формула: <code>result = {op_code}</code></p>"""
        
        return dedent(f"{header}{condition}{self._get_input_format_description()}{self._get_output_format_description()}{self._get_example_table()}")

    @property
    def preloaded_code(self) -> str:
        return """#include <iostream>
#include <map>
#include <vector>
#include <algorithm>

using namespace std;

int main() {
    // Ваш код
    return 0;
}
"""

    def test(self, code: str) -> Result.Ok | Result.Fail:
        runner = CppProgramRunner(code)
        input_data = self.generate_input()
        expected = self.generate_expected_output().strip()
        
        try:
            output = runner.run(input_data).replace('\r', '').strip()
        except ExecutionError as e:
            return Result.Fail(input_data, expected, str(e))
        
        if output == expected:
            return Result.Ok()
        return Result.Fail(input_data, expected, output)


# 4.3 Динамический учёт слов
class Task43:
    def __init__(self, seed: int, strictness: float):
        random.seed(seed)
        self.strictness = strictness
        
        self.word_pool = ['apple', 'banana', 'cherry', 'date', 'fig', 'grape', 'kiwi']
        self.commands = []
        self.counters = {}
        
        op_count = random.randint(15, 30)
        for _ in range(op_count):
            word = random.choice(self.word_pool)
            op = random.choices(['ADD', 'SUB', 'GET'], weights=[0.4, 0.3, 0.3])[0]
            self.commands.append((op, word))
            
            if op == 'ADD':
                self.counters[word] = self.counters.get(word, 0) + 1
            elif op == 'SUB' and word in self.counters and self.counters[word] > 0:
                self.counters[word] -= 1

    def generate_input(self) -> str:
        lines = [str(len(self.commands))]
        for op, word in self.commands:
            lines.append(f"{op} {word}")
        return '\n'.join(lines)

    def generate_expected_output(self) -> str:
        results = []
        current_counters = {}
        
        for op, word in self.commands:
            if op == 'ADD':
                current_counters[word] = current_counters.get(word, 0) + 1
            elif op == 'SUB':
                if current_counters.get(word, 0) > 0:
                    current_counters[word] -= 1
            elif op == 'GET':
                results.append(str(current_counters.get(word, 0)))
                
        return '\n'.join(results)

    def _get_input_format_description(self) -> str:
        return """<p><b>Формат входных данных:</b></p>
<ul>
    <li>Первая строка: <code>N</code> — количество команд.</li>
    <li>Далее <code>N</code> строк с командами формата <code>OP WORD</code>.</li>
</ul>"""

    def _get_output_format_description(self) -> str:
        return """<p><b>Формат выходных данных:</b></p>
<p>По одной строке на каждую команду <code>GET</code> — текущий счётчик слова.</p>"""

    def _get_example_table(self) -> str:
        inp = "3\nADD apple\nGET apple\nSUB apple"
        out = "1"
        note = "Добавили apple, запросили счетчик (1), уменьшили"
        
        return f'''
<b>Пример</b>
<table class="coderunnerexamples">
    <thead>
        <tr>
            <th class="header c0" scope="col">Входные данные</th>
            <th class="header c1" scope="col">Результат</th>
            <th class="header c2 lastcol" scope="col">Пояснение</th>
        </tr>
    </thead>
    <tbody>
        <tr class="r0 lastrow">
            <td class="cell c0"><pre class="tablecell">{inp}</pre></td>
            <td class="cell c1"><pre class="tablecell">{out}</pre></td>
            <td class="cell c2 lastcol">{note}</td>
        </tr>
    </tbody>
</table>'''

    @property
    def question_text(self) -> str:
        header = "<p>Язык: <b>C++</b> (компиляция <code>g++</code>), тема: <b>Динамический учёт слов</b>.</p>"
        
        condition = """<p>Реализуйте систему потокового подсчёта вхождений слов с командами:</p>
<ul>
    <li><code>ADD &lt;слово&gt;</code> — увеличить счётчик слова на 1</li>
    <li><code>SUB &lt;слово&gt;</code> — уменьшить счётчик на 1 (игнорировать, если счётчик уже 0)</li>
    <li><code>GET &lt;слово&gt;</code> — вывести текущий счётчик (0, если слово не добавлено)</li>
</ul>"""
        
        return dedent(f"{header}{condition}{self._get_input_format_description()}{self._get_output_format_description()}{self._get_example_table()}")

    @property
    def preloaded_code(self) -> str:
        return """#include <iostream>
#include <string>
#include <map>

using namespace std;

int main() {
    // Ваш код
    return 0;
}
"""

    def test(self, code: str) -> Result.Ok | Result.Fail:
        runner = CppProgramRunner(code)
        input_data = self.generate_input()
        expected = self.generate_expected_output().strip()
        
        try:
            output = runner.run(input_data).replace('\r', '').strip()
        except ExecutionError as e:
            return Result.Fail(input_data, expected, str(e))
        
        if output == expected:
            return Result.Ok()
        return Result.Fail(input_data, expected, output)


class QuestionN4(QuestionBase):
    questionName = "Задание 4. Алгоритмические задачи с map/set"

    def __init__(self, *, seed: int, strictness: float = 0.7):
        super().__init__(seed=seed, strictness=strictness)
        random.seed(seed)
        
        self.task_type = random.choice(['4.1', '4.2', '4.3'])
        
        if self.task_type == '4.1':
            self.task = Task41(seed, strictness)
        elif self.task_type == '4.2':
            self.task = Task42(seed, strictness)
        else:
            self.task = Task43(seed, strictness)

    @property
    def questionText(self) -> str:
        return self.task.question_text

    @property
    def preloadedCode(self) -> str:
        return self.task.preloaded_code

    def test(self, code: str) -> Result.Ok | Result.Fail:
        try:
            return self.task.test(code)
        except CompilationError as e:
            raise
        except Exception as e:
            return Result.Fail("INTERNAL", "No error expected", f"Internal error: {str(e)}")
