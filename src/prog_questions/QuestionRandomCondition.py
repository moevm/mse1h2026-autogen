from .QuestionBase import QuestionBase, Result
from .utility import CProgramRunner, CompilationError, ExecutionError
from .utility.RandomConditionLoop import Task # генерация условия и тестов для задачи (без risc-v)
import random
from textwrap import dedent

PRELOADED_CODE = """\
#include <stdio.h>

int main() {

   return 0;
}
"""

PRELOADED_CODE_SIMPLE_MODE = """\
void random_condition_solver(long long *arr, size_t arr_length) {{
    // Используйте данную сигнатуру
}}
"""

BASE_TEXT = """\
    <h1>Условие задачи</h1>
    <p align="justify">Напишите программу, которая обрабатывает подаваемый на вход массив согласно условию. Условие необходимо пересчитывать после каждого изменения массива.</p>
    <p align="justify"><b>Hint</b>: Учтите возможность переполнения int.</p>
    <br>
    <b>Ваше условие:</b>
    <br>
    {condition}
    <br><br>
    <p align="justify">Для нулевого элемента массива принять <b>arr[i - 1] = 0</b></p>
    <h4>Формат входных данных</h4>
    <p align="justify">На вход программе в stdin подаётся массив чисел длины {array_length}. Числа разделены пробелами (не обязательно одним).</p>
    <h4>Формат выходных данных</h4>
    <p align="justify">Изменённый массив необходимо вернуть в stdout, элементы разделить пробелами.</p>
    <h4>Пример</h4>
    <table border="1" width="100%">
    	<colgroup>
            <col style="width: 50%;">
            <col style="width: 50%;">
  	    </colgroup>
        <thead align="center">
            <tr>
                <th>Входные данные</th>
                <th>Выходные данные</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><code>{input}</code></td>
                <td><code>{output}</code></td>
            </tr>
        </tbody>
    </table>

"""

BASE_TEXT_SIMPLE_MODE = """\
    <h1>Условие задачи</h1>
    <p align="justify">Напишите функцию, которая обрабатывает подаваемый на вход массив согласно условию. Условие необходимо пересчитывать после каждого изменения массива.</p>
    <p align="justify"><b>Hint</b>: Учтите возможность переполнения int.</p>
    <br>
    <b>Ваше условие:</b>
    <br>
    {condition}
    <br><br>
    <p align="justify">Для нулевого элемента массива принять <b>arr[i - 1] = 0</b></p>
    <h4>Формат входных данных</h4>
    <p align="justify">На вход функции <code>random_condition_solver</code> подаётся указатель на массив чисел <code>arr</code> и его длина <code>arr_length</code>.</p>
    <h4>Формат выходных данных</h4>
    <p align="justify">Возвращаемое значение отсутствует, поскольку работа с массивом осуществляется по указателю.</p>
    <h4>Пример</h4>
    <table border="1" width="100%">
    	<colgroup>
            <col style="width: 50%;">
            <col style="width: 50%;">
  	    </colgroup>
        <thead align="center">
            <tr>
                <th>Входные данные</th>
                <th>Выходные данные</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><code>{input}</code></td>
                <td><code>{output}</code></td>
            </tr>
        </tbody>
    </table>

"""

EXAMPLE_CODE = """\
#include <stdio.h>

int main() {{
    long long arr[{array_length}];
    int i;

    for (int i = 0; i < {array_length}; i++) {{
        scanf("%lld", &arr[i]);
    }}

    for (int i = 0; i < {array_length}; i++) {{
        long long prev = (i - 1 >= 0) ? arr[i - 1] : 0;
        long long condition = {condition_string};
        if (condition {condition_operator} {threshold}) {{
            arr[i] = prev {then_operator} {then_number};
        }} else {{
            arr[i] = arr[i] {else_operator} {else_number};
        }}
    }}

    for (i = 0; i < {array_length}; i++) {{
        printf("%lld ", arr[i]);
    }}

    return 0;
}}
"""

HIDDEN_CODE_SIMPLE_MODE = """\
#include <stdio.h>

void random_condition_solver(long long *arr, size_t arr_length);

int main() {{
    long long arr[{array_length}];
    int i;

    for (int i = 0; i < {array_length}; i++) {{
        scanf("%lld", &arr[i]);
    }}

    random_condition_solver(arr, {array_length});

    for (i = 0; i < {array_length}; i++) {{
        printf("%lld ", arr[i]);
    }}

    return 0;
}}
"""

class QuestionRandomCondition(QuestionBase):
    questionName = "Случайное условие"

    def __init__(self, *, seed: int, condition_length: int=4, array_length: int=10, strictness: float=1, is_simple_task: bool=True):
        """
        :param seed: Seed для воспроизводимости тестов.
        :param condition_length: Длина условия задачи.
        :param array_length: Длина массива данных.
        :param strictness: Параметр для регулирования количества случайных тестов (0.0 - минимум, 1.0 - максимум).
        """
        super().__init__(seed=seed, condition_length=condition_length, array_length=array_length, strictness=strictness, is_simple_task = is_simple_task)
        self.task = Task(array_length, condition_length, seed)
        self.parse(self.task.text)
        self.seed = seed
        self.is_simple_task = is_simple_task
        self.example_solution = EXAMPLE_CODE.format(
            array_length=self.task.array_length,
            condition_string=self.condtition_string,
            condition_operator=self.condition_operator,
            threshold=self.task.threshold,
            then_number=self.task.then_number,
            else_number=self.task.else_number,
            then_operator=self.then_operator,
            else_operator=self.else_operator
        )
        self.expected_output_runner = CProgramRunner(self.example_solution)

    @property
    def questionText(self) -> str:
        if self.is_simple_task:
            cleaned_text = dedent(BASE_TEXT_SIMPLE_MODE)
        else:
            cleaned_text = dedent(BASE_TEXT)

        input_arr = [random.randint(1, 500) for _ in range(self.parameters['array_length'])]
        input = " ".join(map(str, input_arr))

        output = self.expected_output_runner.run(input)

        result = cleaned_text.format(
            condition = ("<br>\n".join(self.task.text.split("\n"))),
            array_length = self.task.array_length,
            input = input,
            output = output
        )

        return result

    @property
    def preloadedCode(self) -> str:
        if self.is_simple_task:
            return PRELOADED_CODE_SIMPLE_MODE.format(length = self.task.array_length)
        return PRELOADED_CODE

    # get arguments from task
    def parse(self, task_text: str):
        task_strings = task_text.split("\n")
        first_string = task_strings[0][5:]
        self.condtition_string = first_string.split(")")[0][2:]
        self.condition_operator = first_string.split(")")[1][1:3]
        self.then_operator = task_strings[1].split()[-2]
        self.else_operator = task_strings[2].split()[-2]

    # test specific case
    def test_case(self, arr: list, code: str, space_amount: int) -> str:
        separator = " " * space_amount
        input = separator.join(map(str, arr))

        expected_output = self.expected_output_runner.run(input)

        try:
            runner = CProgramRunner(code)
            output = runner.run(input)
        except ExecutionError as e:
            return Result.Fail(input, expected_output, str(e))

        if output == expected_output:
            return Result.Ok()
        else:
            return Result.Fail(input, expected_output, output)

    # form test: same numbers
    def test_same_numbers_case(self, code: str, amount: int, exponentiation: int) -> str:
        for serial_number in range(amount):
            upper_edge = self.test_case([10 ** exponentiation] * self.parameters['array_length'], code, serial_number + 1)
            if upper_edge != Result.Ok():
                return upper_edge
            lower_edge = self.test_case([-10 ** exponentiation] * self.parameters['array_length'], code, serial_number + 1)
            return lower_edge

    # form test: alternate number
    def test_alternate_numbers_case(self, code: str, amount: int, exponentiation: int) -> str:
        for serial_number in range(amount):
            small_number = random.randint(-10, 10)
            big_number = random.randint((10**(exponentiation-1)), 10**exponentiation)
            alternating_list = []
            for i in range(self.parameters['array_length']):
                if i % 2 == 0:
                    alternating_list.append(big_number)
                else:
                    alternating_list.append(small_number)

            positive_case = self.test_case(alternating_list, code, serial_number + 1)
            if positive_case != Result.Ok():
                return positive_case
            negative_case = self.test_case([-x for x in alternating_list], code, serial_number + 1)
            return negative_case

    # form test: random numbers
    def test_random(self, code: str, amount: int, upper_border: int) -> str:
        for serial_number in range(amount):
            test_arr = []
            for _ in range(self.parameters['array_length']):
                test_arr.append(random.randint(-(10**upper_border), 10**upper_border))

            test_result = self.test_case(test_arr, code, serial_number + 1)
            if test_result != Result.Ok():
                return test_result
        return Result.Ok()

    def distribute_random_tests(self, total_amount: int, exponentiation_amount: int) -> list:
        random_test_amount = [total_amount // exponentiation_amount] * exponentiation_amount
        for ind in range(total_amount % exponentiation_amount):
            random_test_amount[ind] += 1
        return random_test_amount

    # test
    def test(self, code: str) -> str:
        random.seed(self.seed)

        edge_case_exponentiation = [2, 4, 7, 12]

        if self.is_simple_task:
            code = HIDDEN_CODE_SIMPLE_MODE.format(array_length=self.task.array_length) + code

        # same numbers testing
        for exponentiation in edge_case_exponentiation:
            test_result_same_numbers = self.test_same_numbers_case(code, 1, exponentiation)
            if test_result_same_numbers != Result.Ok():
                return test_result_same_numbers

        # alternate numbers testing
        for exponentiation in edge_case_exponentiation:
            test_result_alternate_numbers = self.test_alternate_numbers_case(code, 1, exponentiation)
            if test_result_alternate_numbers != Result.Ok():
                return test_result_alternate_numbers

        # random numbers testing
        random_test_borders = [2, 3, 4, 5, 7, 9, 12]
        min_tests_number = 20 - 4 * len(edge_case_exponentiation)
        max_tests_number = 50 - 4 * len(edge_case_exponentiation)
        random_test_number = round(min_tests_number + self.parameters['strictness'] * (max_tests_number - min_tests_number))
        random_test_amount = self.distribute_random_tests(random_test_number, len(random_test_borders))

        for ind in range(len(random_test_borders)):
            test_result_random_border = self.test_random(code, random_test_amount[ind], random_test_borders[ind])
            if test_result_random_border != Result.Ok():
                return test_result_random_border

        return Result.Ok()

if __name__ == "__main__":
    test = QuestionRandomCondition(seed=52, condition_length=10, array_length=10, strictness=0.7)
    print(test.questionText)

    with open("test.c", "r", encoding="utf-8") as file:
        c_code = file.read()

    print(test.test(c_code))
