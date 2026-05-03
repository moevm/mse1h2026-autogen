from ..QuestionBase import QuestionBase, Result
from ..utility import CProgramRunner, CompilationError, ExecutionError
import random


AVAILABLE_TASKS = [
    {'id': '1',
        'name': 'Перестановка двух узлов (один список)', 'list_type': 'singly'},
    {'id': '2',
        'name': 'Перестановка узлов (два списка)', 'list_type': 'singly'},
    {'id': '3', 'name': 'Разворот списка', 'list_type': 'singly'},
    {'id': '4', 'name': 'Циклический сдвиг', 'list_type': 'singly'},
    {'id': '5', 'name': 'Вставка в отсортированный двусвязный список',
        'list_type': 'doubly'},
    {'id': '6', 'name': 'Удаление узлов по значению', 'list_type': 'doubly'},
]

LIST_LENGTH_RANGE = (3, 15)
VALUE_RANGE = (-100, 100)
SHIFT_RANGE = (0, 20)

class QuestionN2(QuestionBase):
    questionName = 'Задание 2, Работа со связными списками'

    class _SinglyNode:
        """Узел односвязного списка"""
        def __init__(self, data):
            self.data = data
            self.next = None

    class _DoublyNode:
        """Узел двусвязного списка"""
        def __init__(self, data):
            self.data = data
            self.prev = None
            self.next = None

    @staticmethod
    def _build_singly(values):
        """Построение односвязного списка из списка значений"""
        if not values:
            return None
        head = QuestionN2._SinglyNode(values[0])
        current = head
        for val in values[1:]:
            current.next = QuestionN2._SinglyNode(val)
            current = current.next
        return head

    @staticmethod
    def _to_values_singly(head):
        """Преобразовать односвязный список в список значений"""
        result = []
        current = head
        while current:
            result.append(current.data)
            current = current.next
        return result

    @staticmethod
    def _build_doubly(values):
        """Построить двусвязный список из списка значений"""
        if not values:
            return None
        head = QuestionN2._DoublyNode(values[0])
        current = head
        for val in values[1:]:
            new_node = QuestionN2._DoublyNode(val)
            current.next = new_node
            new_node.prev = current
            current = new_node
        return head


    @staticmethod
    def _to_values_doubly(head):
        """Преобразовать двусвязный список в список значений с проверкой prev-указателей"""
        if not head:
            return []
        result = []
        current = head
        # Проверка: у головы prev должен быть None
        if head.prev is not None:
            raise ValueError("Head node has non-None prev pointer")
        while current:
            result.append(current.data)
            # Проверка обратного указателя
            if current.next and current.next.prev is not current:
                raise ValueError(
                    f"Broken prev link at node with data {current.data}")
            current = current.next
        return result

    # Эталонные реализации функций для проверки
    @staticmethod
    def _ref_swap_nodes_singly(head, i, j):
        """Перестановка узлов с индексами i и j (1-индексация)"""
        if i == j or not head:
            return head
        if i > j:
            i, j = j, i
        # поиск узлов и их предков
        prev_i = None
        node_i = head
        for _ in range(1, i):
            prev_i = node_i
            node_i = node_i.next
        prev_j = None
        node_j = head
        for _ in range(1, j):
            prev_j = node_j
            node_j = node_j.next
        if not node_i or not node_j:
            return head
        # особый случай: соседние узлы (i+1 == j)
        if node_i.next is node_j:
            if prev_i:
                prev_i.next = node_j
            else:
                head = node_j  # node_j становится новой головой
            node_i.next = node_j.next
            node_j.next = node_i
        else:
            next_i, next_j = node_i.next, node_j.next
            if prev_i:
                prev_i.next = node_j
            else:
                head = node_j
            if prev_j:
                prev_j.next = node_i
            else:
                head = node_i
            node_i.next = next_j
            node_j.next = next_i
        return head

    @staticmethod
    def _ref_reverse_singly(head):
        """Разворот односвязного списка"""
        prev = None
        current = head
        while current:
            next_node = current.next
            current.next = prev
            prev = current
            current = next_node
        return prev

    @staticmethod
    def _ref_cyclic_shift_singly(head, k, direction):
        """
        Циклический сдвиг односвязного списка
        direction: 'left' или 'right'
        """
        values = QuestionN2._to_values_singly(head)
        if not values:
            return None
        n = len(values)
        if n <= 1:
            return head
        k = k % n
        if k == 0:
            return head
        if direction == 'right':
            shifted = values[-k:] + values[:-k]
        else:  # left
            shifted = values[k:] + values[:k]
        return QuestionN2._build_singly(shifted)

    @staticmethod
    def _ref_swap_two_lists(head1, head2, pos1, pos2):
        """
        Обмен узлами между двумя односвязными списками
        Возвращает кортеж (new_head1, new_head2)
        """
        if not head1 or not head2:
            return head1, head2
        # поиск node1 и prev1 в списке 1
        prev1 = None
        node1 = head1
        for _ in range(1, pos1):
            if node1:
                prev1 = node1
                node1 = node1.next
        # поиск node2 и prev2 в списке 2
        prev2 = None
        node2 = head2
        for _ in range(1, pos2):
            if node2:
                prev2 = node2
                node2 = node2.next
        if not node1 or not node2:
            return head1, head2
        next1, next2 = node1.next, node2.next
        if prev1:
            prev1.next = node2
        else:
            head1 = node2  # node2 становится новой головой списка 1
        node2.next = next1
        if prev2:
            prev2.next = node1
        else:
            head2 = node1  # node1 становится новой головой списка 2
        node1.next = next2
        return head1, head2

    @staticmethod
    def _ref_insert_sorted_doubly(head, value):
        """Вставка в отсортированный двусвязный список"""
        new_node = QuestionN2._DoublyNode(value)
        if not head:
            return new_node
        # вставка в начало
        if value <= head.data:
            new_node.next = head
            head.prev = new_node
            return new_node
        # поиск позиции вставки
        current = head
        while current.next and current.next.data < value:
            current = current.next
        # вставка после current + вставка в конец обрабатывается тут
        new_node.next = current.next
        new_node.prev = current
        if current.next:
            current.next.prev = new_node
        current.next = new_node
        return head

    @staticmethod
    def _ref_delete_by_value_doubly(head, target):
        """Удаление всех узлов со значением target из двусвязного списка"""
        current = head
        # удаляем совпадения в начале списка
        while current and current.data == target:
            head = current.next
            if head:
                head.prev = None
            current = head
        # удаляем в середине и конце
        current = head
        while current and current.next:
            if current.next.data == target:
                current.next = current.next.next
                if current.next:
                    current.next.prev = current
            else:
                current = current.next
        return head

    def __init__(self, *, seed: int, strictness: float = 1.0,
                 allowed_tasks: list = None, list_type_override: str = None):
        """
        параметры:
        seed - сид для воспроизводимости рандома
        strictness - уровень строкости (0.0 - 1.0), влияет на количество тестов
        allowed_tasks - cписок разрешенных id заданий (если None — все доступны)
        list_type_override - тип списка: 'singly' или 'doubly'
        """
        super().__init__(seed=seed, strictness=strictness,
                         allowed_tasks=allowed_tasks, list_type_override=list_type_override)
        self.strictness = strictness
        random.seed(seed)

        # выбор типа задания
        tasks_pool = [
            t for t in AVAILABLE_TASKS if allowed_tasks is None or t['id'] in allowed_tasks]
        if list_type_override:
            tasks_pool = [t for t in tasks_pool if t['list_type']
                          == list_type_override]

        self.task_config = random.choice(tasks_pool)
        self.task_id = self.task_config['id']
        self.list_type = self.task_config['list_type']

        self._generate_task_parameters()

    def _generate_task_parameters(self):
        """Генерация случайных параметров для текущего задания"""
        self.list_length = random.randint(*LIST_LENGTH_RANGE)
        self.list_values = [random.randint(
            *VALUE_RANGE) for _ in range(self.list_length)]
        
        if self.task_id == '1':  # обмен значениям в одном списке
            self.pos_i = random.randint(1, max(1, self.list_length - 1))
            self.pos_j = random.randint(self.pos_i + 1, self.list_length)
            
        elif self.task_id == '2':  # обмен значениям в двух списках
            self.list2_length = random.randint(2, 10)
            self.list2_values = [random.randint(
                *VALUE_RANGE) for _ in range(self.list2_length)]
            self.pos1 = random.randint(1, self.list_length)
            self.pos2 = random.randint(1, self.list2_length)
            
        elif self.task_id == '3':  # разворот
            pass
        
        elif self.task_id == '4':  # сдвиг
            self.shift_k = random.randint(*SHIFT_RANGE)
            self.shift_direction = random.choice(['left', 'right'])
            
        elif self.task_id == '5':  # вставка (двусвязный)
            self.list_values.sort()
            self.insert_value = random.randint(*VALUE_RANGE)
            
        elif self.task_id == '6':  # удаление (двусвязный)
            if self.list_values:
                self.target_value = random.choice(self.list_values)
                if random.random() < 0.8 and self.list_length > 1:
                    positions = random.sample(range(self.list_length),
                                              k=min(random.randint(1, 3), self.list_length))
                    for pos in positions:
                        self.list_values[pos] = self.target_value
            else:
                self.target_value = 0

    def _get_input_format_description(self) -> str:
        base = "<p><b>Формат входных данных:</b></p><ul>"
        if self.list_type == 'singly':
            base += "<li>Тип списка: <code>односвязный</code></li>"
        else:
            base += "<li>Тип списка: <code>двусвязный</code> (поля <code>prev</code> и <code>next</code>)</li>"
            
        if self.task_id in ['1', '3', '4']:
            base += f"<li>Число <b>n = {self.list_length}</b> — количество элементов</li>"
            base += "<li><b>n целых чисел</b> — значения узлов</li>"
            if self.task_id == '1':
                base += f"<li>Позиции: <b>i = {self.pos_i}</b>, <b>j = {self.pos_j}</b> (индексация начинается с 1)</li>"
            elif self.task_id == '4':
                dir_ru = "влево" if self.shift_direction == 'left' else "вправо"
                base += f"<li>Сдвиг: <b>K = {self.shift_k}</b>, направление: <b>{dir_ru}</b></li>"
                base += "<li><i>Код направления: <code>0</code> = влево, <code>1</code> = вправо</i></li>"

        elif self.task_id == '2':
            base += f"<li>Первый список: <b>n = {self.list_length}</b> элементов</li>"
            base += "<li><b>n целых чисел</b> — значения первого списка</li>"
            base += f"<li>Второй список: <b>m = {self.list2_length}</b> элементов</li>"
            base += "<li><b>m целых чисел</b> — значения второго списка</li>"
            base += f"<li>Позиции: <b>{self.pos1}</b> (список 1), <b>{self.pos2}</b> (список 2)</li>"

        elif self.task_id == '5':
            base += f"<li>Число <b>n = {self.list_length}</b> — количество элементов</li>"
            base += "<li><b>n отсортированных целых чисел</b> — значения списка</li>"
            base += f"<li>Значение для вставки: <b>{self.insert_value}</b></li>"

        elif self.task_id == '6':
            base += f"<li>Число <b>n = {self.list_length}</b> — количество элементов</li>"
            base += "<li><b>n целых чисел</b> — значения списка</li>"
            base += f"<li>Значение для удаления: <b>target = {self.target_value}</b></li>"

        base += "</ul>"
        return base

    def _get_output_format_description(self) -> str:
        if self.task_id == '2':
            return ("<p><b>Формат выходных данных:</b></p>"
                    "<ol><li>Значения первого списка через пробел</li>"
                    "<li>Значения второго списка через пробел (новая строка)</li></ol>")
        return ("<p><b>Формат выходных данных:</b></p>"
                "<p>Значения узлов результирующего списка через пробел в одну строку.</p>")

    def _get_task_specific_condition(self) -> str:
        if self.task_id == '1':
            return f'''
                <p>Поменяйте местами узлы на позициях <b>{self.pos_i}</b> и <b>{self.pos_j}</b> 
                (нумерация с 1), сохраняя связность остальных элементов.</p>
                <p><b>Важно:</b> корректно обрабатывайте головной/хвостовой узел и соседние позиции.</p>
            '''
        elif self.task_id == '2':
            return f'''
                <p>Поменяйте узел на позиции <b>{self.pos1}</b> первого списка с узлом на позиции 
                <b>{self.pos2}</b> второго списка.</p>
                <p><b>Важно:</b> обновите указатели на головы, если затронуты первые элементы.</p>
            '''
        elif self.task_id == '3':
            return '''
                <p>Выполните полное обращение списка: порядок узлов должен стать 
                строго противоположным исходному.</p>
                <p><b>Важно:</b> корректно обрабатывайте пустой список и список из одного элемента.</p>
            '''
        elif self.task_id == '4':
            dir_ru = "влево" if self.shift_direction == 'left' else "вправо"
            return f'''
                <p>Выполните циклический сдвиг на <b>K = {self.shift_k}</b> позиций 
                <b>{dir_ru}</b>.</p>
                <p><b>Важно:</b> если K ≥ N, используйте <b>K % N</b>.</p>
            '''
        elif self.task_id == '5':
            return f'''
                <p>Вставьте узел со значением <b>{self.insert_value}</b> в отсортированный список 
                так, чтобы неубываниющий порядок сохранился.</p>
            '''
        elif self.task_id == '6':
            return f'''
                <p>Удалите <b>все</b> узлы со значением <code>data == {self.target_value}</code>.</p>
                <p><b>Важно:</b> обновите <code>prev</code>/<code>next</code>, верните <code>NULL</code>, 
                если список стал пустым.</p>
            '''
        return ''
    
    @property
    def questionText(self) -> str:
        task_name = self.task_config['name']
        examples = {
            '1': ('4\n10 20 30 40\n2 4', '10 40 30 20', 'Обмен позиций 2 и 4'),
            '2': ('3\n1 2 3\n2\n10 20\n2 1', '1 10 3\n2 20', 'Обмен между списками'),
            '3': ('5\n5 4 3 2 1', '1 2 3 4 5', 'Полный реверс'),
            '4': ('5\n1 2 3 4 5\n2 1', '4 5 1 2 3', 'Сдвиг вправо на 2'),
            '5': ('4\n1 3 5 7\n4', '1 3 4 5 7', 'Вставка в отсортированный'),
            '6': ('5\n2 4 2 5 2\n2', '4 5', 'Удаление всех 2'),
        }
        inp, out, note = examples.get(self.task_id, ('...', '...', '...'))

        return f'''
<h1>{task_name} (ID: {self.task_id})</h1>
<p>Язык: <b>C</b> (компиляция <code>gcc</code>), тип списка: <b>{"двусвязный" if self.list_type == "doubly" else "односвязный"}</b>.</p>

{self._get_task_specific_condition()}
{self._get_input_format_description()}
{self._get_output_format_description()}

<h4>Пример</h4>
<table border="1" width="100%">
    <thead><tr><th>Вход</th><th>Выход</th><th>Пояснение</th></tr></thead>
    <tbody>
        <tr><td><pre>{inp}</pre></td><td><pre>{out}</pre></td><td><i>{note}</i></td></tr>
    </tbody>
</table>
<p><b>Seed:</b> <code>{self.seed}</code></p>
'''

    @property
    def preloadedCode(self) -> str:
        return '''#include <stdio.h>
#include <stdlib.h>

int main() {
    // Ваш код
    return 0;
}
'''

    def _generate_input(self) -> str:
        """Формирует входные данные для C-программы студента"""
        if self.task_id == '1':
            return (f"{self.list_length}\n" +
                    " ".join(map(str, self.list_values)) + "\n" +
                    f"{self.pos_i} {self.pos_j}\n")
        elif self.task_id == '2':
            return (f"{self.list_length}\n" +
                    " ".join(map(str, self.list_values)) + "\n" +
                    f"{self.list2_length}\n" +
                    " ".join(map(str, self.list2_values)) + "\n" +
                    f"{self.pos1} {self.pos2}\n")
        elif self.task_id == '3':
            return f"{self.list_length}\n" + " ".join(map(str, self.list_values)) + "\n"
        elif self.task_id == '4':
            direction_code = 0 if self.shift_direction == 'left' else 1
            return (f"{self.list_length}\n" +
                    " ".join(map(str, self.list_values)) + "\n" +
                    f"{self.shift_k} {direction_code}\n")
        elif self.task_id == '5':
            return (f"{self.list_length}\n" +
                    " ".join(map(str, self.list_values)) + "\n" +
                    f"{self.insert_value}\n")
        elif self.task_id == '6':
            return (f"{self.list_length}\n" +
                    " ".join(map(str, self.list_values)) + "\n" +
                    f"{self.target_value}\n")

    def _compute_expected_output(self) -> str:
        """Вычисляет ожидаемый вывод через эталонную Python-реализацию"""
        if self.task_id == '1':
            head = self._build_singly(self.list_values)
            head = self._ref_swap_nodes_singly(head, self.pos_i, self.pos_j)
            return " ".join(map(str, self._to_values_singly(head)))

        elif self.task_id == '2':
            h1 = self._build_singly(self.list_values)
            h2 = self._build_singly(self.list2_values)
            h1, h2 = self._ref_swap_two_lists(h1, h2, self.pos1, self.pos2)
            return f"{' '.join(map(str, self._to_values_singly(h1)))}\n{' '.join(map(str, self._to_values_singly(h2)))}"

        elif self.task_id == '3':
            head = self._build_singly(self.list_values)
            head = self._ref_reverse_singly(head)
            return " ".join(map(str, self._to_values_singly(head)))

        elif self.task_id == '4':
            head = self._build_singly(self.list_values)
            head = self._ref_cyclic_shift_singly(
                head, self.shift_k, self.shift_direction)
            return " ".join(map(str, self._to_values_singly(head)))

        elif self.task_id == '5':
            head = self._build_doubly(self.list_values)
            head = self._ref_insert_sorted_doubly(head, self.insert_value)
            return " ".join(map(str, self._to_values_doubly(head)))

        elif self.task_id == '6':
            head = self._build_doubly(self.list_values)
            head = self._ref_delete_by_value_doubly(head, self.target_value)
            values = self._to_values_doubly(head)
            return " ".join(map(str, values)) if values else ""

        return ""

    def _generate_edge_case(self, test_num: int):
        """Модифицирует параметры для краевых случаев"""
        if test_num == 0:  # минимальный допустимый список
            if self.task_id == '1':  # обмен узлов: нужно минимум 2 элемента
                self.list_length = 2
                self.list_values = [random.randint(
                    *VALUE_RANGE) for _ in range(2)]
                self.pos_i, self.pos_j = 1, 2
            elif self.task_id == '2':  # два списка
                self.list_length = 1
                self.list_values = [random.randint(*VALUE_RANGE)]
                self.list2_length = 1
                self.list2_values = [random.randint(*VALUE_RANGE)]
                self.pos1, self.pos2 = 1, 1
            elif self.task_id == '4':  # сдвиг
                self.list_length = 1
                self.list_values = [random.randint(*VALUE_RANGE)]
                self.shift_k = 0
            else:  # задания 3, 5, 6 допускают 1 элемент
                self.list_length = 1
                self.list_values = [random.randint(*VALUE_RANGE)]

        elif test_num == 1:  # пустой список (где это допустимо)
            if self.task_id in ['3', '4', '6']:
                self.list_length = 0
                self.list_values = []
                if self.task_id == '6':
                    self.target_value = 0
            elif self.task_id == '5':  # вставка в пустой список
                self.list_length = 0
                self.list_values = []
                self.insert_value = random.randint(*VALUE_RANGE)
                
        elif test_num == 2:  # K = 0 или K >= n для сдвига
            if self.task_id == '4':
                self.shift_k = 0 if random.random() < 0.5 else self.list_length * 3
        
        elif test_num == 3:  # соседние позиции для обмена
            if self.task_id == '1' and self.list_length >= 2:
                self.pos_i = random.randint(1, self.list_length - 1)
                self.pos_j = self.pos_i + 1
        
        elif test_num == 4:  # обмен головы/хвоста
            if self.task_id == '1' and self.list_length >= 2:
                self.pos_i, self.pos_j = 1, self.list_length
                
        elif test_num == 5:  # обмен головы и второго элемента
            if self.task_id == '1' and self.list_length >= 2:
                self.pos_i, self.pos_j = 1, 2

        elif test_num == 6:  # обмен предпоследнего и хвоста
            if self.task_id == '1' and self.list_length >= 2:
                self.pos_i, self.pos_j = self.list_length - 1, self.list_length

    def test(self, code: str) -> Result.Ok | Result.Fail:
        try:
            program = CProgramRunner(code)
        except CompilationError as e:
            raise

        min_tests, max_tests = 5, 25
        num_edge_cases = 7
        num_tests = max(
            int(min_tests + self.strictness * (max_tests - min_tests)),
            num_edge_cases
        )

        for test_num in range(num_tests):
            # Воспроизводимая рандомизация
            random.seed(self.seed + test_num)
            self._generate_task_parameters()

            # Применяем крайние случаи на первых итерациях
            if test_num < num_edge_cases:
                self._generate_edge_case(test_num)

            # Генерация теста
            program_input = self._generate_input()
            expected_output = self._compute_expected_output()

            try:
                student_output = program.run(program_input, timeout=5)
                # Нормализация: убираем лишние пробелы/переносы для сравнения
                if student_output.strip() != expected_output.strip():
                    return Result.Fail(program_input, expected_output, student_output)
            except ExecutionError as e:
                return Result.Fail(program_input, expected_output, str(e))
            except ValueError as e:
                return Result.Fail(
                    program_input,
                    expected_output,
                    f"Structure validation error: {e}"
                )

        return Result.Ok()
