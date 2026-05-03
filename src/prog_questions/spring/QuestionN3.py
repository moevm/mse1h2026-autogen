from ..QuestionBase import QuestionBase, Result
from ..utility import CProgramRunner, ExecutionError, CompilationError, InternalError
import random
import re
import os
import subprocess
import sys

NUM_RANDOM_TESTS = 30
OP_BUFFER_SIZE = 16
EXAMPLE_SEED_XOR = 0x123456

class CppProgramRunner(CProgramRunner):
    """Раннер для C++"""

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
                raise InternalError("Компиляция прошла, но файл не создан")

            return exec_path

        except CompilationError:
            raise
        except FileNotFoundError:
            raise CompilationError("g++ не найден")
        except Exception as e:
            raise InternalError(f"Ошибка компиляции: {e}")


class QuestionN3(QuestionBase):
    questionName = 'Задание 3, Классы и шаблоны: реализация стека или очереди'

    FORBIDDEN_PATTERNS = [
        (r'#\s*include\s*<\s*stack\s*>',  'Запрещено подключать <stack>'),
        (r'#\s*include\s*<\s*queue\s*>',  'Запрещено подключать <queue>'),
        (r'#\s*include\s*<\s*deque\s*>',  'Запрещено подключать <deque>'),
        (r'\bstd\s*::\s*stack\b',         'Запрещено использовать std::stack'),
        (r'\bstd\s*::\s*queue\b',         'Запрещено использовать std::queue'),
        (r'\bstd\s*::\s*deque\b',         'Запрещено использовать std::deque'),
    ]

    def __init__(self, *, seed):
        super().__init__(seed=seed)
        random.seed(self.seed)

        # Stack или Queue
        self.containerType = random.choice(['Stack', 'Queue'])

        # Тип элементов: конкретный или шаблонный
        self.elementType = random.choice(['int', 'double', 'template'])

        # База реализации
        self.implType = random.choice(['array', 'list'])

        # Вариант: обычный контейнер или Limited с наследованием
        self.limitedVariant = random.choice([False, True])

        # Поведение при переполнении
        # 'ignore'- push при полном контейнере игнорируется
        # 'evict' - при push вытесняется самый старый элемент
        self.overflowBehavior = random.choice(['ignore', 'evict'])

        # Лимит для Limited (5..15)
        self.limitSize = random.randint(5, 15)

        # Метод доступа зависит от контейнера
        self.accessMethod = 'top' if self.containerType == 'Stack' else 'front'

        # Конкретный C++-тип для вывода в тексте задания
        self.cppType = {
            'int':      'int',
            'double':   'double',
            'template': 'T',
        }[self.elementType]

    def _make_harness(self, use_limited: bool = False) -> str:
        used_cls  = f'Limited{self.containerType}' if use_limited else self.containerType
        access = self.accessMethod

        if self.elementType == 'template':
            instance     = f'{used_cls}<int> c;'
            read_val     = 'int val; scanf("%d", &val);'
            print_access = f'printf("%d\\n", c.{access}());'
        elif self.elementType == 'double':
            instance     = f'{used_cls} c;'
            read_val     = 'double val; scanf("%lf", &val);'
            print_access = f'printf("%.6f\\n", c.{access}());'
        else:
            instance     = f'{used_cls} c;'
            read_val     = 'int val; scanf("%d", &val);'
            print_access = f'printf("%d\\n", c.{access}());'

        return f"""
#include <cstdio>
#include <cstring>

int main() {{
    int n;
    scanf("%d", &n);
    {instance}
    for (int i = 0; i < n; i++) {{
        char op[{OP_BUFFER_SIZE}];
        scanf("%s", op);
        if (strcmp(op, "push") == 0) {{
            {read_val}
            c.push(val);
        }} else if (strcmp(op, "pop") == 0) {{
            c.pop();
        }} else if (strcmp(op, "{access}") == 0) {{
            {print_access}
        }} else if (strcmp(op, "isEmpty") == 0) {{
            printf("%d\\n", c.isEmpty() ? 1 : 0);
        }}
    }}
    return 0;
}}
"""

    def _generate_value(self):
        if self.elementType == 'double':
            return round(random.uniform(-1000.0, 1000.0), 6)
        else:
            return random.randint(-100000, 100000)

    def _simulate(self, ops: list) -> list:
        container = []
        output = []
        limit = self.limitSize if self.limitedVariant else None

        for op in ops:
            name = op[0]
            if name == 'push':
                val = op[1]
                if limit is not None and len(container) >= limit:
                    if self.overflowBehavior == 'ignore':
                        pass
                    else:
                        container.pop(0)
                        container.append(val)
                else:
                    container.append(val)
            elif name == 'pop':
                if container:
                    if self.containerType == 'Stack':
                        container.pop()
                    else:
                        container.pop(0)
            elif name in ('top', 'front'):
                if container:
                    val = container[-1] if self.containerType == 'Stack' else container[0]
                    if self.elementType == 'double':
                        output.append(f'{val:.6f}')
                    else:
                        output.append(str(val))
            elif name == 'isEmpty':
                output.append('1' if not container else '0')
        return output

    def generateTest(self) -> tuple:
        ops = []
        size = 0
        limit = self.limitSize if self.limitedVariant else 50
        num_ops = random.randint(12, 25)

        for _ in range(num_ops):
            choices = ['push', 'isEmpty']
            if size > 0:
                choices += ['pop', self.accessMethod, self.accessMethod, self.accessMethod]
            if self.limitedVariant and size < limit:
                choices += ['push', 'push']
            name = random.choice(choices)

            if name == 'push':
                val = self._generate_value()
                ops.append(('push', val))
                if size < limit:
                    size += 1
                elif self.overflowBehavior == 'evict':
                    pass
            else:
                ops.append((name,))
                if name == 'pop' and size > 0:
                    size -= 1

        lines = [str(len(ops))]
        for op in ops:
            if op[0] == 'push':
                if self.elementType == 'double':
                    lines.append(f'push {op[1]:.6f}')
                else:
                    lines.append(f'push {op[1]}')
            else:
                lines.append(op[0])

        programInput   = '\n'.join(lines)
        expectedOutput = '\n'.join(self._simulate(ops))
        return programInput, expectedOutput

    def _static_checks(self, code: str) -> str | None:
        code_clean = re.sub(
            r'//.*?$|/\*.*?\*/|"[^"]*"',
            '',
            code,
            flags=re.MULTILINE | re.DOTALL
        )

        for pattern, message in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, code_clean):
                return message

        if not re.search(r'\bnew\b', code_clean):
            return 'Необходимо использовать динамическое выделение памяти (оператор new).'

        if self.implType == 'list':
            if not re.search(r'\b(next|Node|node)\b', code_clean):
                return 'Требуется реализация на односвязном списке.'
        elif self.implType == 'array':
            if not re.search(r'(\[\s*\d*\s*\]|capacity|size|head|tail)', code_clean):
                return 'Требуется реализация на динамическом массиве.'

        return None

    @property
    def questionText(self) -> str:
        cls       = self.containerType
        access    = self.accessMethod
        impl_ru   = 'динамического массива' if self.implType == 'array' else 'односвязного списка'
        cls_ru    = 'стека' if cls == 'Stack' else 'очереди'
        access_ru = 'верхний' if cls == 'Stack' else 'первый'

        if self.elementType == 'int':
            type_note = 'Тип элементов: <code>int</code>.'
            type_str  = 'int'
        elif self.elementType == 'double':
            type_note = 'Тип элементов: <code>double</code>. Выводите числа с 6 знаками после запятой.'
            type_str  = 'double'
        else:
            type_note = 'Класс должен быть шаблонным: <code>template&lt;typename T&gt;</code>.'
            type_str  = 'T'

        saved_state = random.getstate()
        random.seed(self.seed ^ EXAMPLE_SEED_XOR)
        example_input, example_output = self.generateTest()
        random.setstate(saved_state)

        example_table = f'''
            <table class="coderunnerexamples">
                <thead>
                    <tr>
                        <th class="header c0" scope="col">Входные данные</th>
                        <th class="header c2 lastcol" scope="col">Результат</th>
                    </tr>
                </thead>
                <tbody>
                    <tr class="r0 lastrow">
                        <td class="cell c1"><pre class="tablecell">{example_input}</pre></td>
                        <td class="cell c1"><pre class="tablecell">{example_output}</pre></td>
                    </tr>
                </tbody>
            </table>
        '''

        if not self.limitedVariant:
            task_desc = f'''
                Реализуйте класс <b>{cls}</b> для типа <code>{type_str}</code>,
                интерфейс которого описан в шаблоне.<br>
                {type_note}<br>
                Функцию <code>main()</code> и ввод/вывод писать <b>не нужно</b>.<br>
                {"Стек" if cls == "Stack" else "Очередь"} требуется реализовать на базе <b>{impl_ru}</b>
                (обязательно использовать оператор <code>new</code>).<br>
                Считать, что в {cls_ru} единовременно никогда не будет более <b>50 элементов</b>.<br>
                <b>Запрещено</b> использовать <code>&lt;stack&gt;</code>, <code>&lt;queue&gt;</code>,
                <code>&lt;deque&gt;</code> и соответствующие типы из <code>std</code>.<br>
            '''
        else:
            overflow_ru = (
                'игнорируется (элемент не добавляется)'
                if self.overflowBehavior == 'ignore'
                else f'вытесняет самый старый элемент ({"нижний элемент стека" if cls == "Stack" else "первый элемент очереди"} удаляется)'
            )
            task_desc = f'''
                Реализуйте два класса:<br>
                <ul>
                    <li><b>{cls}</b> - базовый {"стек" if cls == "Stack" else "очередь"}, интерфейс описан в шаблоне.</li>
                    <li><b>Limited{cls}</b> - наследник <b>{cls}</b> с ограничением на размер.</li>
                </ul>
                {type_note}<br>
                Функцию <code>main()</code> и ввод/вывод писать <b>не нужно</b>.<br>
                Реализация - на базе <b>{impl_ru}</b> (обязательно использовать оператор <code>new</code>).<br>
                Считать, что в базовом {cls_ru} единовременно никогда не будет более <b>50 элементов</b>.<br>
                В <b>Limited{cls}</b> максимальный размер равен <b>{self.limitSize} элементам</b>.<br>
                При попытке добавить элемент в полный <b>Limited{cls}</b> операция <code>push</code> {overflow_ru}.<br>
                <b>Запрещено</b> использовать <code>&lt;stack&gt;</code>, <code>&lt;queue&gt;</code>,
                <code>&lt;deque&gt;</code> и соответствующие типы из <code>std</code>.<br>
            '''

        return f'''
            {task_desc}
            <br>
            Методы класса:
            <ul>
                <li><code>void push({type_str} val)</code> - добавить элемент</li>
                <li><code>void pop()</code> - удалить элемент (на пустом {cls_ru} не вызывается)</li>
                <li><code>{type_str} {access}()</code> - вернуть {access_ru} элемент (на пустом не вызывается)</li>
                <li><code>bool isEmpty()</code> - вернуть <code>true</code> если контейнер пуст</li>
            </ul>
            <b>Пример</b>:<br><br>
            {example_table}
            Используйте шаблон ниже и дополните реализацию.<br>
        '''

    @property
    def preloadedCode(self) -> str:
        cls    = self.containerType
        access = self.accessMethod

        if self.elementType == 'template':
            T             = 'T'
            tmpl          = 'template<typename T>\n'
            cls_name      = f'{cls}<T>'
            lim_cls_name  = f'Limited{cls}<T>'
            lim_tmpl      = 'template<typename T>\n'
        else:
            T             = self.elementType
            tmpl          = ''
            cls_name      = cls
            lim_cls_name  = f'Limited{cls}'
            lim_tmpl      = ''

        base_class = '\n'.join([
            f'{tmpl}class {cls} {{',
            f'public:',
            f'    {cls}(){{}}',
            f'    ~{cls}(){{}}',
            f'    void push({T} val){{ // кладет элемент в {cls}',
            f'    }}',
            f'    void pop(){{  // извлекает элемент из {cls}',
            f'    }}',
            f'    {T} {access}(){{ // возвращает верхний элемент {cls} не извлекая',
            f'    }}',
            f'    bool isEmpty(){{ // возвращает true, если {cls} пуст. false',
            f'    }}',
            f'}};',
        ])

        if not self.limitedVariant:
            return base_class

        limited_class = '\n'.join([
            f'',
            f'{lim_tmpl}class Limited{cls} : public {cls_name} {{',
            f'    // Максимальный размер: {self.limitSize}',
            f'public:',
            f'    void push({T} val){{',
            f'    }}',
            f'}};',
        ])

        return base_class + limited_class

    def _run_tests(self, program, use_limited: bool) -> 'Result.Ok | Result.Fail':
        orig = self.limitedVariant
        self.limitedVariant = use_limited

        random.seed(self.seed)
        for i in range(NUM_RANDOM_TESTS):
            programInput, expectedOutput = self.generateTest()
            try:
                result = program.run(programInput)
                result_normalized   = result.replace('\r\n', '\n').replace('\r', '\n').strip()
                expected_normalized = expectedOutput.strip()
                if result_normalized != expected_normalized:
                    self.limitedVariant = orig
                    return Result.Fail(programInput, expectedOutput, result)
            except ExecutionError as e:
                self.limitedVariant = orig
                return Result.Fail(programInput, expectedOutput, str(e))

        self.limitedVariant = orig
        return Result.Ok()

    def test(self, code: str) -> 'Result.Ok | Result.Fail':
        error_msg = self._static_checks(code)
        if error_msg:
            return Result.Fail('', '', error_msg)

        base_code = code + '\n' + self._make_harness()
        base_program = CppProgramRunner(base_code)
        result = self._run_tests(base_program, use_limited=False)
        if result != Result.Ok():
            return result

        if self.limitedVariant:
            limited_code = code + '\n' + self._make_harness(use_limited=True)
            limited_program = CppProgramRunner(limited_code)

            over_limit = self.limitSize + 5
            ops_count  = over_limit + 1

            lines = [str(ops_count)]
            for i in range(over_limit):
                if self.elementType == 'double':
                    lines.append(f'push {float(i):.6f}')
                else:
                    lines.append(f'push {i}')
            lines.append(self.accessMethod)

            programInput = '\n'.join(lines)

            def _fmt(val: int) -> str:
                return f'{float(val):.6f}' if self.elementType == 'double' else str(val)

            if self.overflowBehavior == 'ignore':
                if self.containerType == 'Stack':
                    expected = _fmt(self.limitSize - 1)
                else:
                    expected = _fmt(0)
            else:
                if self.containerType == 'Stack':
                    expected = _fmt(over_limit - 1)
                else:
                    expected = _fmt(over_limit - self.limitSize)

            try:
                result = limited_program.run(programInput).strip()
                if result != expected:
                    return Result.Fail(programInput, expected, result)
            except ExecutionError as e:
                return Result.Fail(programInput, expected, str(e))

            result = self._run_tests(limited_program, use_limited=True)
            if result != Result.Ok():
                return result

        return Result.Ok()