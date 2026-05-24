from ..QuestionBase import QuestionBase, Result
from ..utility import CppProgramRunner, CompilationError, ExecutionError
from dataclasses import dataclass
from typing import Optional, List, Tuple, Set, Literal
import random
from collections import defaultdict, Counter
from textwrap import dedent

@dataclass
class Task4Config:
    """Конфигурация для одного варианта задания 4."""
    task_type: Literal['4.1', '4.2', '4.3']
    seed: int
    strictness: float

    # Параметры для 4.1 (группировка по ключу)
    words: Optional[List[str]] = None
    filter_type: Optional[str] = None          # 'none', 'min_count', 'max_count', 'exact_count', 'letter_filter'
    threshold: Optional[int] = None
    allowed_letters: Optional[Set[str]] = None

    # Параметры для 4.2 (частотный фильтр с маской)
    operation: Optional[Literal['shift', 'and']] = None
    mask: Optional[int] = None
    min_freq: Optional[int] = None
    numbers: Optional[List[int]] = None

    # Параметры для 4.3 (динамический учёт слов)
    commands: Optional[List[Tuple[str, str]]] = None

    @property
    def name(self) -> str:
        names = {
            '4.1': 'Группировка по ключу',
            '4.2': 'Частотный фильтр с маской',
            '4.3': 'Динамический учёт слов',
        }
        return names.get(self.task_type, self.task_type)


class Task4ConfigGenerator:
    """Генератор конфигураций для задания 4."""
    # Константы для генерации
    WORDS_POOL = ['apple', 'ant', 'apricot', 'banana', 'bat', 'bear',
                  'cat', 'car', 'cup', 'dog', 'duck', 'deer', 'elephant']
    VALUE_RANGE = (1, 200)
    SHIFT_MASK_CHOICES = [0x03, 0x05, 0x0F, 0x07]
    MIN_FREQ_CHOICES = [2, 3]
    WORD_POOL_43 = ['apple', 'banana', 'cherry', 'date', 'fig', 'grape', 'kiwi']

    def __init__(self, seed: int, strictness: float):
        self.seed = seed
        self.strictness = strictness

    def generate(self, task_type_override: Optional[str] = None) -> Task4Config:
        """Генерирует полную конфигурацию задания."""
        random.seed(self.seed)

        # Выбор типа задания
        if task_type_override:
            task_type = task_type_override
        else:
            task_type = random.choice(['4.1', '4.2', '4.3'])

        config = Task4Config(
            task_type=task_type,
            seed=self.seed,
            strictness=self.strictness
        )

        if task_type == '4.1':
            self._generate_41_config(config)
        elif task_type == '4.2':
            self._generate_42_config(config)
        else:  # '4.3'
            self._generate_43_config(config)

        return config

    def _generate_41_config(self, config: Task4Config):
        """Генерирует параметры для 4.1."""
        word_count = random.randint(8, 20)
        config.words = [random.choice(self.WORDS_POOL) for _ in range(word_count)]

        # Выбор фильтра
        filter_types = ['none', 'min_count', 'max_count', 'exact_count', 'letter_filter']
        config.filter_type = random.choice(filter_types)

        if config.filter_type == 'none':
            config.threshold = None
            config.allowed_letters = None
        elif config.filter_type in ('min_count', 'max_count', 'exact_count'):
            config.threshold = random.randint(2, 4) if config.filter_type != 'exact_count' else random.choice([2, 3])
            config.allowed_letters = None
        else:  # letter_filter
            config.threshold = None
            letters = random.sample('abcdefg', k=random.randint(2, 4))
            config.allowed_letters = set(letters)

    def _generate_42_config(self, config: Task4Config):
        """Генерирует параметры для 4.2."""
        config.operation = random.choice(['shift', 'and'])
        config.mask = random.choice(self.SHIFT_MASK_CHOICES)
        config.min_freq = random.choice(self.MIN_FREQ_CHOICES)

        numbers = []
        num_good = random.randint(3, 6)
        for _ in range(num_good):
            base = random.randint(*self.VALUE_RANGE)
            # гарантируем, что число имеет установленные биты маски
            num = base | config.mask
            freq = random.randint(config.min_freq, config.min_freq + 2)
            numbers.extend([num] * freq)

        for _ in range(random.randint(5, 15)):
            numbers.append(random.randint(*self.VALUE_RANGE))

        random.shuffle(numbers)
        config.numbers = numbers

    def _generate_43_config(self, config: Task4Config):
        """Генерирует параметры для 4.3."""
        commands = []
        # Количество команд
        cmd_count = random.randint(15, 30)
        # Возможные команды с весами
        op_choices = ['ADD', 'SUB', 'GET']
        weights = [0.4, 0.3, 0.3]

        for _ in range(cmd_count):
            word = random.choice(self.WORD_POOL_43)
            op = random.choices(op_choices, weights=weights)[0]
            commands.append((op, word))
        config.commands = commands



def format_example_table(inp: str, out: str, note: str) -> str:
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


def generate_question_text_41(config: Task4Config) -> str:
    """Формирует текст задания для 4.1."""
    header = "<p>Язык: <b>C++</b> (компиляция <code>g++</code>), тема: <b>Группировка по ключу</b>.</p>"
    condition = """<p>Считайте строку слов, записанных через пробел (в конце строки <code>#</code>), 
и сгруппируйте их по первой букве.</p>
<p>Для каждой буквы, у которой есть хотя бы одно слово, выведите букву и все 
соответствующие слова в лексикографическом порядке.</p>"""

    filter_desc = ""
    if config.filter_type == 'min_count':
        filter_desc = f"<p><b>Дополнительное условие:</b> Выводите только буквы, у которых {config.threshold} или более слов.</p>"
    elif config.filter_type == 'max_count':
        filter_desc = f"<p><b>Дополнительное условие:</b> Выводите только буквы, у которых не более {config.threshold} слов.</p>"
    elif config.filter_type == 'exact_count':
        filter_desc = f"<p><b>Дополнительное условие:</b> Выводите только буквы, у которых ровно {config.threshold} слов.</p>"
    elif config.filter_type == 'letter_filter':
        letters = ', '.join(sorted(config.allowed_letters))
        filter_desc = f"<p><b>Дополнительное условие:</b> Выводите только буквы: {letters}.</p>"

    input_desc = """<p><b>Формат входных данных:</b></p>
<ul>
    <li>Строка слов через пробел</li>
    <li>Окончание ввода: символ <code>#</code></li>
</ul>"""

    output_desc = """<p><b>Формат выходных данных:</b></p>
<p><code>&lt;буква&gt;: &lt;слово1&gt; &lt;слово2&gt; ...</code></p>
<ul>
    <li>Группы отсортированы по букве.</li>
    <li>Слова внутри группы отсортированы лексикографически.</li>
</ul>
<p><i>Если после фильтрации не осталось ни одной группы, выведите <code>NO_DATA</code>.</i></p>"""

    # Пример
    example_words = ['apple', 'ant', 'apricot', 'banana', 'bat', 'cat']
    example_inp = ' '.join(example_words) + ' #'

    groups = defaultdict(list)
    for w in example_words:
        if w: groups[w[0]].append(w)

    lines = []
    for letter in sorted(groups.keys()):
        count = len(groups[letter])
        if config.filter_type == 'min_count' and count < config.threshold: continue
        if config.filter_type == 'max_count' and count > config.threshold: continue
        if config.filter_type == 'exact_count' and count != config.threshold: continue
        if config.filter_type == 'letter_filter' and letter not in config.allowed_letters: continue
        words_sorted = sorted(groups[letter])
        lines.append(f"{letter}: {' '.join(words_sorted)}")

    example_out = '\n'.join(lines) if lines else "NO_DATA"
    note = f"Пример с учётом фильтра: {config.filter_type if config.filter_type != 'none' else 'без фильтра'}"
    example_table = format_example_table(example_inp, example_out, note)

    return dedent(f"{header}{condition}{filter_desc}{input_desc}{output_desc}{example_table}")


def generate_question_text_42(config: Task4Config) -> str:
    """Формирует текст задания для 4.2."""
    header = "<p>Язык: <b>C++</b> (компиляция <code>g++</code>), тема: <b>Частотный фильтр с маской</b>.</p>"

    op_desc = "побитовый сдвиг влево на количество вхождений (num << count)" if config.operation == 'shift' else f"побитовое И с маской (num & 0x{config.mask:02X})"
    op_code = "num << count" if config.operation == 'shift' else f"num & 0x{config.mask:02X}"

    condition = f"""<p>Считайте поток целых неотрицательных чисел. Подсчитайте частоту каждого числа.</p>
<p>Выведите только те числа, которые:</p>
<ol>
    <li>Встретились <b>{config.min_freq} или более раз</b></li>
    <li>У которых установлен бит(ы) маски <code>0x{config.mask:02X}</code> (проверка: <code>(num & 0x{config.mask:02X}) == 0x{config.mask:02X}</code>)</li>
</ol>
<p>Для каждого подходящего числа выведите: исходное число, количество вхождений и результат операции <b>{op_desc}</b>.</p>
<p>Формула: <code>result = {op_code}</code></p>"""

    input_desc = """<p><b>Формат входных данных:</b></p>
<ul>
    <li>Поток целых неотрицательных чисел через пробел</li>
    <li>Окончание ввода: число <code>0</code> (не обрабатывается)</li>
</ul>"""

    output_desc = f"""<p><b>Формат выходных данных:</b></p>
<p><code>&lt;число&gt; &lt;частота&gt; &lt;результат&gt;</code></p>
<ul>
    <li>Вывод отсортирован по возрастанию исходного числа.</li>
    <li>Результат вычисляется как: {op_desc}.</li>
</ul>
<p><i>Если после фильтрации не осталось ни одного числа, выведите <code>NO_DATA</code>.</i></p>"""

    # Пример
    example_numbers = []
    matching_num = config.mask
    example_numbers.extend([matching_num] * config.min_freq)
    example_numbers.extend([1, 2, 3])

    example_inp = ' '.join(map(str, example_numbers)) + ' 0'

    freq = Counter(example_numbers)
    results = []
    for num in sorted(freq.keys()):
        count = freq[num]
        if count < config.min_freq: continue
        if (num & config.mask) != config.mask: continue
        if config.operation == 'shift':
            res = num << count
        else:
            res = num & config.mask
        results.append(f"{num} {count} {res}")

    example_out = '\n'.join(results) if results else "NO_DATA"
    note = f"Маска 0x{config.mask:02X}, операция: {config.operation}, min_freq={config.min_freq}"
    example_table = format_example_table(example_inp, example_out, note)

    return dedent(f"{header}{condition}{input_desc}{output_desc}{example_table}")


def generate_question_text_43(config: Task4Config) -> str:
    """Формирует текст задания для 4.3."""
    header = "<p>Язык: <b>C++</b> (компиляция <code>g++</code>), тема: <b>Динамический учёт слов</b>.</p>"

    condition = """<p>Реализуйте систему потокового подсчёта вхождений слов с командами:</p>
<ul>
    <li><code>ADD &lt;слово&gt;</code> — увеличить счётчик слова на 1</li>
    <li><code>SUB &lt;слово&gt;</code> — уменьшить счётчик на 1 (игнорировать, если счётчик уже 0)</li>
    <li><code>GET &lt;слово&gt;</code> — вывести текущий счётчик (0, если слово не добавлено)</li>
</ul>"""

    input_desc = """<p><b>Формат входных данных:</b></p>
<ul>
    <li>Первая строка: <code>N</code> — количество команд.</li>
    <li>Далее <code>N</code> строк с командами формата <code>OP WORD</code>.</li>
</ul>"""

    output_desc = """<p><b>Формат выходных данных:</b></p>
<p>По одной строке на каждую команду <code>GET</code> — текущий счётчик слова.</p>"""

    # Пример
    example_inp = "3\nADD apple\nGET apple\nSUB apple"
    example_out = "1"
    note = "Добавили apple, запросили счетчик (1), уменьшили"
    example_table = format_example_table(example_inp, example_out, note)

    return dedent(f"{header}{condition}{input_desc}{output_desc}{example_table}")



class QuestionN4(QuestionBase):
    questionName = "Задание 4. Алгоритмические задачи с map/set"

    def __init__(self, *, seed: int, strictness: float = 0.7, task_type_override: Optional[str] = None):
        super().__init__(seed=seed, strictness=strictness)
        self.seed = seed
        self.strictness = strictness
        generator = Task4ConfigGenerator(seed, strictness)
        self.config = generator.generate(task_type_override=task_type_override)
        self.task_type = self.config.task_type

    @property
    def questionText(self) -> str:
        # Возвращаем текст в зависимости от типа
        if self.task_type == '4.1':
            return generate_question_text_41(self.config)
        elif self.task_type == '4.2':
            return generate_question_text_42(self.config)
        else:
            return generate_question_text_43(self.config)

    @property
    def preloadedCode(self) -> str:
        # Общий шаблон для всех вариантов
        return """#include <iostream>
#include <string>
#include <map>
#include <vector>
#include <algorithm>
#include <sstream>
#include <unordered_map>

using namespace std;

int main() {
    // Ваш код
    return 0;
}
"""

    def _apply_edge_case(self, config: Task4Config, test_num: int):
        """Модифицирует конфигурацию для краевых случаев."""
        if config.task_type == '4.1':
            if test_num == 0:
                config.words = []
            elif test_num == 1:
                config.words = ['apple']
            elif test_num == 2:
                config.words = ['cat', 'car', 'cup']
        elif config.task_type == '4.2':
            if test_num == 0:
                config.numbers = []
            elif test_num == 1:
                config.numbers = [1, 2, 3]
            elif test_num == 2:
                if (5 & config.mask) == config.mask:
                    config.numbers = [5, 5]
                else:
                    config.numbers = [1, 1]
            elif test_num == 3:
                config.numbers = [config.mask] * (config.min_freq + 2)
        elif config.task_type == '4.3':
            if test_num == 0:
                config.commands = [('ADD', 'apple'), ('SUB', 'apple')]
            elif test_num == 1:
                config.commands = [('GET', 'apple')]
            elif test_num == 2:
                config.commands = [('SUB', 'apple'), ('GET', 'apple')]
            elif test_num == 3:
                pass

    @staticmethod
    def _expected_41(config: Task4Config) -> str:
        """Вычисляет ожидаемый вывод для 4.1."""
        groups = defaultdict(list)
        for w in config.words:
            if w:
                groups[w[0]].append(w)

        lines = []
        for letter in sorted(groups.keys()):
            count = len(groups[letter])
            if config.filter_type == 'min_count' and count < config.threshold:
                continue
            if config.filter_type == 'max_count' and count > config.threshold:
                continue
            if config.filter_type == 'exact_count' and count != config.threshold:
                continue
            if config.filter_type == 'letter_filter' and letter not in config.allowed_letters:
                continue
            words_sorted = sorted(groups[letter])
            lines.append(f"{letter}: {' '.join(words_sorted)}")
        return '\n'.join(lines) if lines else "NO_DATA"

    @staticmethod
    def _expected_42(config: Task4Config) -> str:
        """Вычисляет ожидаемый вывод для 4.2."""
        freq = Counter(config.numbers)
        results = []
        for num in sorted(freq.keys()):
            count = freq[num]
            if count < config.min_freq:
                continue
            if (num & config.mask) != config.mask:
                continue
            if config.operation == 'shift':
                res = num << count
            else:
                res = num & config.mask
            results.append(f"{num} {count} {res}")
        return '\n'.join(results) if results else "NO_DATA"

    @staticmethod
    def _expected_43(config: Task4Config) -> str:
        """Вычисляет ожидаемый вывод для 4.3."""
        counters = {}
        output = []
        for op, word in config.commands:
            if op == 'ADD':
                counters[word] = counters.get(word, 0) + 1
            elif op == 'SUB':
                if counters.get(word, 0) > 0:
                    counters[word] -= 1
            elif op == 'GET':
                output.append(str(counters.get(word, 0)))
        return '\n'.join(output)

    def _generate_input(self, config: Task4Config) -> str:
        """Генерирует входные данные для заданной конфигурации."""
        if config.task_type == '4.1':
            return ' '.join(config.words) + ' #'
        elif config.task_type == '4.2':
            return ' '.join(map(str, config.numbers)) + ' 0'
        else:  # 4.3
            lines = [str(len(config.commands))]
            for op, word in config.commands:
                lines.append(f"{op} {word}")
            return '\n'.join(lines)

    def test(self, code: str) -> Result.Ok | Result.Fail:
        """Запускает код студента на серии тестов."""
        try:
            runner = CppProgramRunner(code)
        except CompilationError as e:
            raise

        min_tests, max_tests = 5, 25
        num_tests = max(int(min_tests + self.strictness * (max_tests - min_tests)), 8)
        edge_cases = 4  # количество краевых тестов

        for test_num in range(num_tests):
            generator = Task4ConfigGenerator(self.seed + test_num, self.strictness)
            config = generator.generate(task_type_override=self.task_type)

            if test_num < edge_cases:
                self._apply_edge_case(config, test_num)

            input_data = self._generate_input(config)

            if config.task_type == '4.1':
                expected = self._expected_41(config).strip()
            elif config.task_type == '4.2':
                expected = self._expected_42(config).strip()
            else:
                expected = self._expected_43(config).strip()

            try:
                output = runner.run(input_data).replace('\r', '').strip()
            except ExecutionError as e:
                return Result.Fail(input_data, expected, str(e))

            if output != expected:
                return Result.Fail(input_data, expected, output)

        return Result.Ok()
    