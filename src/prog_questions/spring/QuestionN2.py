from ..QuestionBase import QuestionBase, Result
from ..utility import CProgramRunner, CompilationError, ExecutionError
from dataclasses import dataclass
from typing import Literal, Optional, List
import random


@dataclass
class TaskConfig:
    """Конфигурация задания, генерируемая из независимых параметров"""
    list_type: Literal['singly', 'doubly']
    num_lists: int
    operation: Literal['swap', 'reverse', 'shift', 'insert', 'delete']

    swap_indices: Optional[tuple[int, int]] = None
    shift_k: Optional[int] = None
    shift_direction: Optional[Literal['left', 'right']] = None
    insert_value: Optional[int] = None
    target_value: Optional[int] = None
    pos1: Optional[int] = None
    pos2: Optional[int] = None

    list_length: int = 5
    list2_length: int = 5
    is_sorted: bool = False
    allow_duplicates: bool = True
    may_be_empty: bool = False

    @property
    def task_id(self) -> str:
        # Генерирует уникальный ID задания для совместимости с внешним кодом
        lt = 's' if self.list_type == 'singly' else 'd'
        return f"{lt}{self.num_lists}_{self.operation}"

    @property
    def name(self) -> str:
        # Возвращает человекочитаемое название операции
        names = {
            'swap': 'Перестановка элементов',
            'reverse': 'Разворот списка',
            'shift': 'Циклический сдвиг',
            'insert': 'Вставка в отсортированный список',
            'delete': 'Удаление элементов по значению',
        }
        suffix = ' (два списка)' if self.num_lists == 2 else ''
        return f"{names.get(self.operation, self.operation)}{suffix}"


class TaskConfigGenerator:
    # Диапазоны для генерации случайных параметров тестов
    LIST_LENGTH_RANGE = (3, 15)
    VALUE_RANGE = (-100, 100)
    SHIFT_RANGE = (0, 20)

    def __init__(self, seed: int, strictness: float = 1.0):
        # Инициализация генератора с seed и уровнем строгости strictness
        self.seed = seed
        self.strictness = strictness
        random.seed(seed)

    def generate(self,
                 list_type_override: Optional[str] = None,
                 allowed_operations: Optional[List[str]] = None,
                 num_lists_override: Optional[int] = None) -> TaskConfig:
        # Генерирует конфигурацию задания с учетом ограничений и весов операций
        random.seed(self.seed)

        if list_type_override:
            list_type = list_type_override
        else:
            # чем больше strictness, тем выше вероятность двусвязных списков
            weights = [10 - int(self.strictness * 6), int(self.strictness * 6)]
            list_type = random.choices(
                ['singly', 'doubly'], weights=weights)[0]

        if list_type == 'doubly':
            num_lists = 1
        elif num_lists_override is not None:
            num_lists = num_lists_override
        else:
            num_lists = 1 if random.random() > self.strictness * 0.3 else 2

        available_ops = self._get_available_ops(list_type, num_lists)
        if allowed_operations:
            available_ops = [
                op for op in available_ops if op in allowed_operations]
        if not available_ops:
            available_ops = ['reverse']

        weights = [2 if op == 'reverse' else 3 for op in available_ops]
        operation = random.choices(available_ops, weights=weights)[0]

        list_length = random.randint(*self.LIST_LENGTH_RANGE)
        is_sorted = (operation in ['insert', 'delete']
                     ) and random.random() < 0.7

        config = TaskConfig(
            list_type=list_type,
            num_lists=num_lists,
            operation=operation,
            list_length=list_length,
            is_sorted=is_sorted,
            allow_duplicates=True,
            may_be_empty=(operation in ['reverse', 'shift', 'delete']),
        )

        self._populate_operation_params(config)

        if config.num_lists == 2:
            config.list2_length = random.randint(2, 10)

        return config

    def _get_available_ops(self, list_type: str, num_lists: int) -> List[str]:
        # Возвращает список допустимых операций для данной комбинации типа и количества списков
        ops = []
        if list_type == 'singly':
            if num_lists == 1:
                ops.extend(['swap', 'reverse', 'shift'])
            elif num_lists == 2:
                ops.append('swap')
        elif list_type == 'doubly':
            ops.extend(['insert', 'delete'])
        return ops if ops else ['reverse']

    def _populate_operation_params(self, config: TaskConfig):
        # Заполняет специфичные параметры операции (позиции, K, значения и т.д.)
        if config.operation == 'swap':
            if config.num_lists == 1:
                n = max(2, config.list_length)
                i = random.randint(1, n - 1)
                j = random.randint(i + 1, n)
                config.swap_indices = (i, j)
            else:
                config.pos1 = random.randint(1, max(1, config.list_length))
                config.pos2 = random.randint(1, max(1, config.list2_length))
        elif config.operation == 'shift':
            config.shift_k = random.randint(*self.SHIFT_RANGE)
            config.shift_direction = random.choice(['left', 'right'])
        elif config.operation == 'insert':
            config.is_sorted = True
            config.insert_value = random.randint(*self.VALUE_RANGE)
        elif config.operation == 'delete':
            config.target_value = random.randint(*self.VALUE_RANGE)


class QuestionN2(QuestionBase):
    questionName = 'Задание 2, Работа со связными списками'

    def __init__(self, *, seed: int, strictness: float = 1.0,
                 allowed_tasks: list = None, list_type_override: str = None):
        # Инициализация задания: генерация конфигурации и значений списков
        super().__init__(seed=seed, strictness=strictness,
                         allowed_tasks=allowed_tasks, list_type_override=list_type_override)
        self.strictness = strictness

        id_to_op = {'1': 'swap', '2': 'swap', '3': 'reverse',
                    '4': 'shift', '5': 'insert', '6': 'delete'}
        allowed_ops = allowed_tasks
        if allowed_tasks:
            allowed_ops = [id_to_op.get(t, t) for t in allowed_tasks]

        config_gen = TaskConfigGenerator(seed, strictness)
        self.config = config_gen.generate(
            list_type_override=list_type_override,
            allowed_operations=allowed_ops
        )

        self.task_id = self.config.task_id
        self.list_type = self.config.list_type
        self._generate_list_values()

    def _generate_list_values(self):
        # Генерирует значения списков с учетом сортировки и наличия target для delete
        if self.config.is_sorted:
            self.list_values = sorted([
                random.randint(*TaskConfigGenerator.VALUE_RANGE)
                for _ in range(self.config.list_length)
            ])
        else:
            self.list_values = [
                random.randint(*TaskConfigGenerator.VALUE_RANGE)
                for _ in range(self.config.list_length)
            ]

        # Для delete: гарантируем, что target_value встречается в списке
        if self.config.operation == 'delete' and self.config.target_value is not None:
            if self.list_values and random.random() < 0.8:
                positions = random.sample(
                    range(len(self.list_values)),
                    k=min(random.randint(1, 3), len(self.list_values))
                )
                for pos in positions:
                    self.list_values[pos] = self.config.target_value

        if self.config.num_lists == 2:
            self.list2_values = [
                random.randint(*TaskConfigGenerator.VALUE_RANGE)
                for _ in range(self.config.list2_length)
            ]

    def _apply_edge_case(self, test_num: int):
        # Модифицирует параметры конфигурации для краевых случаев (пустой список, минимум элементов и т.д.)
        cfg = self.config
        if test_num == 0:
            if cfg.operation == 'swap' and cfg.num_lists == 1:
                cfg.list_length = 2
                cfg.swap_indices = (1, 2)
            elif cfg.operation == 'swap' and cfg.num_lists == 2:
                cfg.list_length = 1
                cfg.list2_length = 1
                cfg.pos1, cfg.pos2 = 1, 1
            elif cfg.operation == 'shift':
                cfg.list_length = 1
                cfg.shift_k = 0
            else:
                cfg.list_length = 1
        elif test_num == 1:
            if cfg.operation in ['reverse', 'shift', 'delete']:
                cfg.list_length = 0
                self.list_values = []
                if cfg.operation == 'delete':
                    cfg.target_value = 0
            elif cfg.operation == 'insert':
                cfg.list_length = 0
                self.list_values = []
        elif test_num == 2 and cfg.operation == 'shift':
            cfg.shift_k = 0 if random.random() < 0.5 else cfg.list_length * 3
        elif test_num == 3 and cfg.operation == 'swap' and cfg.num_lists == 1 and cfg.list_length >= 2:
            i = random.randint(1, cfg.list_length - 1)
            cfg.swap_indices = (i, i + 1)
        elif test_num == 4 and cfg.operation == 'swap' and cfg.num_lists == 1 and cfg.list_length >= 2:
            cfg.swap_indices = (1, cfg.list_length)
        elif test_num == 5 and cfg.operation == 'swap' and cfg.num_lists == 1 and cfg.list_length >= 2:
            cfg.swap_indices = (1, 2)
        elif test_num == 6 and cfg.operation == 'swap' and cfg.num_lists == 1 and cfg.list_length >= 2:
            cfg.swap_indices = (cfg.list_length - 1, cfg.list_length)

    def _get_input_format_description(self) -> str:
        # Формирует HTML-описание формата входных данных для текущего типа задания
        cfg = self.config
        base = "<p><b>Формат входных данных:</b></p><ul>"
        if cfg.list_type == 'singly':
            base += "<li>Тип списка: <code>односвязный</code></li>"
        else:
            base += "<li>Тип списка: <code>двусвязный</code> (поля <code>prev</code> и <code>next</code>)</li>"

        if cfg.operation == 'swap' and cfg.num_lists == 2:
            base += "<li>Число <b>n</b> — количество элементов первого списка</li>"
            base += "<li><b>n целых чисел</b> — значения первого списка</li>"
            base += "<li>Число <b>m</b> — количество элементов второго списка</li>"
            base += "<li><b>m целых чисел</b> — значения второго списка</li>"
            base += "<li>Две позиции: <b>pos1 pos2</b></li>"
        elif cfg.operation in ['swap', 'reverse', 'shift']:
            base += "<li>Число <b>n</b> — количество элементов</li>"
            base += "<li><b>n целых чисел</b> — значения узлов</li>"
            if cfg.operation == 'swap' and cfg.num_lists == 1:
                base += "<li>Две позиции <b>i j</b> (индексация начинается с 1)</li>"
            elif cfg.operation == 'shift':
                base += "<li>Два числа: <b>K</b> (величина сдвига) и <b>direction</b> (0 = влево, 1 = вправо)</li>"
        elif cfg.operation == 'insert':
            base += "<li>Число <b>n</b> — количество элементов</li>"
            base += "<li><b>n отсортированных целых чисел</b> — значения списка</li>"
            base += "<li>Целое число — значение для вставки</li>"
        elif cfg.operation == 'delete':
            base += "<li>Число <b>n</b> — количество элементов</li>"
            base += "<li><b>n целых чисел</b> — значения списка</li>"
            base += "<li>Целое число <b>target</b> — значение для удаления</li>"

        base += "</ul>"
        return base

    def _get_output_format_description(self) -> str:
        # Формирует HTML-описание формата выходных данных
        if self.config.operation == 'swap' and self.config.num_lists == 2:
            return ("<p><b>Формат выходных данных:</b></p>"
                    "<ol><li>Значения первого списка через пробел</li>"
                    "<li>Значения второго списка через пробел (новая строка)</li></ol>")
        return ("<p><b>Формат выходных данных:</b></p>"
                "<p>Значения узлов результирующего списка через пробел в одну строку.</p>")

    def _get_task_specific_condition(self) -> str:
        # Возвращает текст условия задачи
        cfg = self.config
        if cfg.operation == 'swap':
            if cfg.num_lists == 1:
                return '''<p>Поменяйте местами узлы на заданных позициях <b>i</b> и <b>j</b> (нумерация с 1), сохраняя связность остальных элементов.</p>
                <p><b>Важно:</b> корректно обрабатывайте головной/хвостовой узел и соседние позиции.</p>'''
            else:
                return '''<p>Поменяйте узел на заданной позиции <b>pos1</b> первого списка с узлом на заданной позиции <b>pos2</b> второго списка.</p>
                <p><b>Важно:</b> обновите указатели на головы, если затронуты первые элементы.</p>'''
        elif cfg.operation == 'reverse':
            return '''<p>Выполните полное обращение списка: порядок узлов должен стать строго противоположным исходному.</p>
                <p><b>Важно:</b> корректно обрабатывайте пустой список и список из одного элемента.</p>'''
        elif cfg.operation == 'shift':
            return '''<p>Выполните циклический сдвиг списка на заданное количество позиций <b>K</b> в заданном направлении.</p>
                <p><b>Важно:</b> если K ≥ N, используйте <b>K % N</b>.</p>'''
        elif cfg.operation == 'insert':
            return '''<p>Вставьте узел с заданным значением в отсортированный список так, чтобы неубывающий порядок сохранился.</p>'''
        elif cfg.operation == 'delete':
            return '''<p>Удалите <b>все</b> узлы с заданным значением <code>target</code>.</p>
                <p><b>Важно:</b> обновите <code>prev</code>/<code>next</code>, верните <code>NULL</code>, если список стал пустым.</p>'''
        return ''

    @property
    def questionText(self) -> str:
        # Формирует полный текст задачи с примером
        cfg = self.config
        examples = {
            '1': ('4\n10 20 30 40\n2 4', '10 40 30 20', 'Обмен позиций 2 и 4'),
            '2': ('3\n1 2 3\n2\n10 20\n2 1', '1 10 3\n2 20', 'Обмен между списками'),
            '3': ('5\n5 4 3 2 1', '1 2 3 4 5', 'Полный реверс'),
            '4': ('5\n1 2 3 4 5\n2 1', '4 5 1 2 3', 'Сдвиг вправо на 2'),
            '5': ('4\n1 3 5 7\n4', '1 3 4 5 7', 'Вставка в отсортированный'),
            '6': ('5\n2 4 2 5 2\n2', '4 5', 'Удаление всех 2'),
        }

        # Выбор ключа примера на основе операции и количества списков
        if cfg.operation == 'swap':
            example_key = '2' if cfg.num_lists == 2 else '1'
        elif cfg.operation == 'reverse':
            example_key = '3'
        elif cfg.operation == 'shift':
            example_key = '4'
        elif cfg.operation == 'insert':
            example_key = '5'
        elif cfg.operation == 'delete':
            example_key = '6'
        else:
            example_key = '3'

        inp, out, note = examples.get(example_key, ('...', '...', '...'))

        return f'''
<p>Язык: <b>C</b> (компиляция <code>gcc</code>), тип списка: <b>{"двусвязный" if self.list_type == "doubly" else "односвязный"}</b>.</p>

{self._get_task_specific_condition()}
{self._get_input_format_description()}
{self._get_output_format_description()}

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
</table>
'''

    @property
    def preloadedCode(self) -> str:
        # Возвращает шаблон кода на C, который подставляется в редактор для студента
        return '''#include <stdio.h>
#include <stdlib.h>

int main() {
    // Ваш код
    return 0;
}
'''

    @staticmethod
    def _ref_swap_elements(values, i, j):
        # Эталон: перестановка элементов с индексами i и j (1-индексация)
        if not values:
            return []
        lst = values[:]
        if 0 <= i-1 < len(lst) and 0 <= j-1 < len(lst):
            lst[i-1], lst[j-1] = lst[j-1], lst[i-1]
        return lst

    @staticmethod
    def _ref_reverse(values):
        # Эталон: разворот списка
        return values[::-1]

    @staticmethod
    def _ref_cyclic_shift(values, k, direction):
        # Эталон: циклический сдвиг списка на k позиций в заданном направлении
        if not values:
            return []
        n = len(values)
        k = k % n
        if k == 0:
            return values[:]
        return values[-k:] + values[:-k] if direction == 'right' else values[k:] + values[:k]

    @staticmethod
    def _ref_swap_two_lists(list1, list2, pos1, pos2):
        # Эталон: обмен элементами между двумя списками на заданных позициях
        if not list1 or not list2:
            return list1[:], list2[:]
        l1, l2 = list1[:], list2[:]
        if 0 <= pos1-1 < len(l1) and 0 <= pos2-1 < len(l2):
            l1[pos1-1], l2[pos2-1] = l2[pos2-1], l1[pos1-1]
        return l1, l2

    @staticmethod
    def _ref_insert_sorted(values, value):
        # Эталон: вставка значения в отсортированный список с сохранением порядка
        lst = values[:]
        idx = 0
        while idx < len(lst) and lst[idx] < value:
            idx += 1
        lst.insert(idx, value)
        return lst

    @staticmethod
    def _ref_delete_by_value(values, target):
        # Эталон: удаление всех элементов со значением target
        return [x for x in values if x != target]

    def _generate_input(self) -> str:
        # Формирует строку входных данных для запуска C-программы студента
        cfg = self.config
        if cfg.operation == 'swap' and cfg.num_lists == 1:
            i, j = cfg.swap_indices
            return f"{cfg.list_length}\n{' '.join(map(str, self.list_values))}\n{i} {j}\n"
        elif cfg.operation == 'swap' and cfg.num_lists == 2:
            return f"{cfg.list_length}\n{' '.join(map(str, self.list_values))}\n{cfg.list2_length}\n{' '.join(map(str, self.list2_values))}\n{cfg.pos1} {cfg.pos2}\n"
        elif cfg.operation == 'reverse':
            return f"{cfg.list_length}\n{' '.join(map(str, self.list_values))}\n"
        elif cfg.operation == 'shift':
            d = 0 if cfg.shift_direction == 'left' else 1
            return f"{cfg.list_length}\n{' '.join(map(str, self.list_values))}\n{cfg.shift_k} {d}\n"
        elif cfg.operation == 'insert':
            return f"{cfg.list_length}\n{' '.join(map(str, self.list_values))}\n{cfg.insert_value}\n"
        elif cfg.operation == 'delete':
            return f"{cfg.list_length}\n{' '.join(map(str, self.list_values))}\n{cfg.target_value}\n"
        return ""

    def _compute_expected_output(self) -> str:
        # Вычисляет ожидаемый вывод через эталонные реализации на Python
        cfg = self.config
        if cfg.operation == 'swap' and cfg.num_lists == 1:
            return " ".join(map(str, self._ref_swap_elements(self.list_values, *cfg.swap_indices)))
        elif cfg.operation == 'swap' and cfg.num_lists == 2:
            l1, l2 = self._ref_swap_two_lists(
                self.list_values, self.list2_values, cfg.pos1, cfg.pos2)
            return f"{' '.join(map(str, l1))}\n{' '.join(map(str, l2))}"
        elif cfg.operation == 'reverse':
            return " ".join(map(str, self._ref_reverse(self.list_values)))
        elif cfg.operation == 'shift':
            return " ".join(map(str, self._ref_cyclic_shift(self.list_values, cfg.shift_k, cfg.shift_direction)))
        elif cfg.operation == 'insert':
            return " ".join(map(str, self._ref_insert_sorted(self.list_values, cfg.insert_value)))
        elif cfg.operation == 'delete':
            return " ".join(map(str, self._ref_delete_by_value(self.list_values, cfg.target_value)))
        return ""

    def test(self, code: str) -> Result.Ok | Result.Fail:
        # Запускает код студента на серии тестов (обычных + краевых) и возвращает результат проверки
        try:
            program = CProgramRunner(code)
        except CompilationError as e:
            raise

        min_tests, max_tests = 5, 25
        num_edge_cases = 7
        num_tests = max(int(min_tests + self.strictness *
                        (max_tests - min_tests)), num_edge_cases)
        original_num_lists = self.config.num_lists
        
        for test_num in range(num_tests):
            random.seed(self.seed + test_num)
            config_gen = TaskConfigGenerator(
                self.seed + test_num, self.strictness)
            self.config = config_gen.generate(
                list_type_override=self.list_type,
                allowed_operations=[self.config.operation],
                num_lists_override=original_num_lists
            )
            self.task_id = self.config.task_id

            if test_num < num_edge_cases:
                self._apply_edge_case(test_num)

            self._generate_list_values()
            program_input = self._generate_input()
            expected_output = self._compute_expected_output()

            try:
                student_output = program.run(program_input, timeout=5)
                student_output = student_output.replace(
                    '\r\n', '\n').rstrip('\n')
                expected_output = expected_output.replace(
                    '\r\n', '\n').rstrip('\n')
                if student_output.strip() != expected_output.strip():
                    return Result.Fail(program_input, expected_output, student_output)
            except ExecutionError as e:
                return Result.Fail(program_input, expected_output, str(e))
            except ValueError as e:
                return Result.Fail(program_input, expected_output, f"Structure validation error: {e}")

        return Result.Ok()
    