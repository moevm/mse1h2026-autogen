from prog_questions.QuestionBase import QuestionBase, Result
from prog_questions.utility.CProgramRunner import CProgramRunner, CompilationError, ExecutionError, InternalError
import random
from textwrap import dedent
import subprocess
import os
import sys
from collections import defaultdict, Counter

# раннер с++
class CppProgramRunner(CProgramRunner):
    """Переопределяет только компиляцию для C++. Остальное наследуется от базового раннера."""
    def _compile(self) -> str:
        try:
            src_path = os.path.join(self.tmp_dir.name, 'program.cpp')
            with open(src_path, 'w', encoding='utf-8') as f:
                f.write(self.c_code)

            exec_ext = '.exe' if sys.platform == 'win32' else ''
            exec_path = os.path.join(self.tmp_dir.name, f'program{exec_ext}')

            compile_result = subprocess.run(
                ['g++', src_path, '-std=c++17', '-o', exec_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            if compile_result.returncode != 0:
                error_msg = compile_result.stderr.decode('utf-8', errors='replace')
                raise CompilationError(error_msg)

            if not os.path.isfile(exec_path):
                raise InternalError("Компиляция завершилась успешно, но файл не создан")

            return exec_path
        except CompilationError:
            raise
        except FileNotFoundError:
            raise CompilationError("g++ not found in PATH. Install MinGW-w64.")
        except Exception as e:
            raise InternalError(f"Internal compilation error: {e}")

# 4.1 Группировка по ключу
class Task41:
    def __init__(self, seed: int, strictness: float):
        random.seed(seed)
        self.strictness = strictness
        
        # Словарь для генерации слов
        self.words_pool = ['apple', 'ant', 'apricot', 'banana', 'bat', 'bear', 
                          'cat', 'car', 'cup', 'dog', 'duck', 'deer', 'elephant']
        
        # Генерируем входные данные
        word_count = random.randint(8, 20)
        self.input_words = [random.choice(self.words_pool) for _ in range(word_count)]
        
        # Рандомизируем усложнение
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

    @property
    def question_text(self) -> str:
        base = """
<h1>Задание 4.1. Группировка по ключу</h1>
<p>Считайте строку слов, записанных через пробел (в конце строки <code>#</code>), 
и сгруппируйте их по первой букве.</p>
<p>Для каждой буквы, у которой есть хотя бы одно слово, выведите букву и все 
соответствующие слова в лексикографическом порядке.</p>
"""
        if self.filter_desc:
            base += f"<p><b>Дополнительное условие:</b> {self.filter_desc}</p>"
        
        base += """
<h4>Формат ввода</h4>
<p>Слова через пробел, окончание ввода: <code>#</code></p>
<h4>Формат вывода</h4>
<p><code>&lt;буква&gt;: &lt;слово1&gt; &lt;слово2&gt; ...</code>, группы отсортированы по букве.</p>
<p><i>Если после фильтрации не осталось ни одного числа, выведите <code>NO_DATA</code>.</i></p>
"""
        return dedent(base)

    @property
    def preloaded_code(self) -> str:
        return """#include <iostream>
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
        
        # Рандомизируем: операция (сдвиг или побитовое И)
        self.operation = random.choice(['shift', 'and'])
        self.mask = random.choice([0x03, 0x05, 0x0F, 0x07])
        self.min_freq = random.randint(2, 3)
        
        # Генерируем числа с контролируемыми частотами
        self.numbers = []
        # Создаём числа, которые точно пройдут фильтр
        for _ in range(random.randint(3, 6)):
            num = random.randint(1, 200)
            # Гарантируем, что (num & mask) == mask для части чисел
            if random.random() < 0.6:
                num = (num | self.mask)
            freq = random.randint(self.min_freq, self.min_freq + 2)
            self.numbers.extend([num] * freq)
        
        # Добавляем шум (числа с частотой 1 или не проходящие маску)
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
            else:  # and
                result_val = num & self.mask
            
            results.append(f"{num} {count} {result_val}")
        
        return '\n'.join(results) if results else "NO_DATA"

    @property
    def question_text(self) -> str:
        op_desc = "побитовый сдвиг влево на количество вхождений (num << count)" if self.operation == 'shift' else "побитовое И с маской (num & mask)"
        op_code = "num << count" if self.operation == 'shift' else f"num & 0x{self.mask:02X}"
        
        base = f"""
<h1>Задание 4.2. Частотный фильтр с маской</h1>
<p>Считайте поток целых неотрицательных чисел. Подсчитайте частоту каждого числа.</p>
<p>Выведите только те числа, которые:</p>
<ol>
    <li>Встретились <b>{self.min_freq} или более раз</b></li>
    <li>У которых установлен бит(ы) маски <code>0x{self.mask:02X}</code> (проверка: <code>(num & 0x{self.mask:02X}) == 0x{self.mask:02X}</code>)</li>
</ol>
<p>Для каждого выведите: исходное число, количество вхождений и результат операции <b>{op_desc}</b>.</p>
<p>Формула: <code>result = {op_code}</code></p>
<h4>Формат ввода</h4>
<p>Числа через пробел, окончание: <code>0</code> (не обрабатывается)</p>
<h4>Формат вывода</h4>
<p><code>&lt;число&gt; &lt;частота&gt; &lt;результат&gt;</code>, отсортировано по возрастанию числа.</p>
<p><i>Если после фильтрации не осталось ни одного числа, выведите <code>NO_DATA</code>.</i></p>
"""
        return dedent(base)

    @property
    def preloaded_code(self) -> str:
        return """#include <iostream>
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
        
        # Генерируем последовательность команд
        op_count = random.randint(15, 30)
        for _ in range(op_count):
            word = random.choice(self.word_pool)
            op = random.choices(['ADD', 'SUB', 'GET'], weights=[0.4, 0.3, 0.3])[0]
            self.commands.append((op, word))
            
            if op == 'ADD':
                self.counters[word] = self.counters.get(word, 0) + 1
            elif op == 'SUB' and word in self.counters and self.counters[word] > 0:
                self.counters[word] -= 1
            # GET не меняет состояние

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

    @property
    def question_text(self) -> str:
        base = """
<h1>Задание 4.3. Динамический учёт слов</h1>
<p>Реализуйте систему потокового подсчёта вхождений слов с командами:</p>
<ul>
    <li><code>ADD &lt;слово&gt;</code> — увеличить счётчик слова на 1</li>
    <li><code>SUB &lt;слово&gt;</code> — уменьшить счётчик на 1 (игнорировать, если 0)</li>
    <li><code>GET &lt;слово&gt;</code> — вывести текущий счётчик (0, если слово не добавлено)</li>
</ul>
<h4>Формат ввода</h4>
<p>Первая строка: <code>N</code> — количество команд. Далее <code>N</code> строк с командами.</p>
<h4>Формат вывода</h4>
<p>По одной строке на каждую команду <code>GET</code> — текущий счётчик слова.</p>
"""
        return dedent(base)

    @property
    def preloaded_code(self) -> str:
        return """#include <iostream>
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


# рандомный выбор задания
class Question4(QuestionBase):
    questionName = "Задание 4. Алгоритмические задачи с map/set"

    def __init__(self, *, seed: int, strictness: float = 0.7):
        super().__init__(seed=seed, strictness=strictness)
        random.seed(seed)
        
        # Случайный выбор одного из трёх заданий
        self.task_type = random.choice(['4.1', '4.2', '4.3'])
        
        if self.task_type == '4.1':
            self.task = Task41(seed, strictness)
        elif self.task_type == '4.2':
            self.task = Task42(seed, strictness)
        else:
            self.task = Task43(seed, strictness)

    @property
    def questionText(self) -> str:
        header = f"<p style='color: #666; font-size: 0.9em;'>Вариант задания: <b>{self.task_type}</b></p>"
        return header + self.task.question_text

    @property
    def preloadedCode(self) -> str:
        return self.task.preloaded_code

    def test(self, code: str) -> Result.Ok | Result.Fail:
        try:
            return self.task.test(code)
        except CompilationError as e:
            raise
        except Exception as e:
            # Логируем ошибку, но не ломаем проверку
            return Result.Fail("INTERNAL", "No error expected", f"Internal error: {str(e)}")