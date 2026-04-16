from .QuestionBase import QuestionBase, Result
from .utility import CProgramRunner, CompilationError, ExecutionError
from .utility.StringOperations import generate_operations, generate_input_string, apply_operations, generate_text # генерация операций и тестов для задачи (без risc-v)
from textwrap import dedent
import random

TASK_DESCRIPTION = "Дана строка, содержащая латинские буквы (в верхнем и нижнем регистрах), цифры, пробелы, специальные символы (!@#$%^&*()[]{{}}/?|~) и знаки подчеркивания. Необходимо написать программу, которая выполняет над этой строкой операции, указанные ниже."
SIMPLE_TASK_DESCRIPTION = "Дана строка, содержащая латинские буквы (в верхнем и нижнем регистрах), цифры, пробелы, специальные символы (!@#$%^&*()[]{{}}/?|~) и знаки подчеркивания. Необходимо написать тело функции processString, которая выполняет над этой строкой операции, указанные ниже."

QUESTION_TEXT = """
<h1>Условие задачи</h1>
<p align="justify">{task_description}</p>
<br>
<b>Ваше условие:</b>
<br>
<ol>{operations}</ol>
<br><br>
<p align="justify">{task_operations_order}</p>
<h4>Формат входных данных</h4>
<p align="justify">На вход подается строка по длине не превосходящая <code>{max_length}</code>, содержащая латинские буквы (верхний и нижний регистр), цифры, пробелы, специальные символы (!@#$%^&*()[]{{}}/?|~) и знаки подчеркивания.</p>
<h4>Формат выходных данных</h4>
<p align="justify">Вывести преобразованную строку после применения всех заданных операций в stdout.</p>
<h4>Пример</h4>
<table border="1" width="100%">
	<colgroup>
        <col style="width: 33%;">
        <col style="width: 33%;">
        <col style="width: 34%;">
  	</colgroup>
    <thead align="center">
        <tr>
            <th>Операции</th>
            <th>Входные данные</th>
            <th>Выходные данные</th>
        </tr>
    </thead>
    <tbody>
        {example}
    </tbody>
</table>
"""

PRELOADED_CODE = """
#include <stdio.h>
int main() {
   return 0;
}
"""

SIMPLE_HIDDEN_CODE = r"""
#include <stdio.h>
#include <string.h>

void processString(char *str);

int main() {{
    char str[2*{N}+1] = {{ 0 }};

    if (fgets(str, sizeof(str), stdin) != NULL) {{
        size_t len = strlen(str);
        if (len > 0 && str[len-1] == '\n') {{
            str[len-1] = '\0';
        }}
    }}

    processString(str);
    printf("%s", str);
    return 0;
}}
"""

SIMPLE_PRELOADED_CODE = """
void processString(char *str) {
    // Решите задачу внутри этой функции
}
"""


def get_operation_html_description(operations):
    return "\n".join(f"<p>{op.get_text()}</p>" for op in operations)


class QuestionStringOperations(QuestionBase):
    questionName = 'Операции над строками'

    def __init__(self, *, seed: int, num_operations: int=1, min_length: int=30, max_length: int=100, strictness: float=1, is_simple_task: bool=True):
        """
        :param seed: Seed для воспроизводимости тестов.
        :param num_operations: количество операций задачи.
        :param min_length: минимальная длина входных данных.
        :param max_length: максимальная длина входных данных.
        :param strictness: Параметр для регулирования количества случайных тестов (0.0 - минимум, 1.0 - максимум).
        :param is_simple_task: Флаг, который определяет режим работы программы (True - простой режим, False - сложный режим)
        """
        super().__init__(seed=seed, num_operations=num_operations,
                         min_length=min_length, max_length=max_length, strictness=strictness, is_simple_task=is_simple_task)
        self.strictness = strictness
        self.num_operations = num_operations
        self.operations = generate_operations(seed, num_operations)
        self.min_length = min_length
        self.max_length = max_length
        self.is_simple_task = is_simple_task

    @property
    def questionText(self) -> str:
        dedent_question_text = dedent(QUESTION_TEXT)
        input_strings = [
            ([op], generate_input_string([op], 10, 30)) for op in self.operations
        ]
        if self.num_operations != 1:
            input_strings.append((self.operations, generate_input_string(self.operations, 10, 50)))

        return dedent_question_text.format(
            max_length=self.max_length,
            operations="\n".join(f"<li>{op.get_text()}</li>" for op in self.operations),
            example="\n".join(f"<tr><td>{get_operation_html_description(string[0])}</td>"
                              f"<td><code>{string[1]}</code>"
                              f"</td><td><code>{apply_operations(string[1], string[0])}<code></td></tr>"
                              for string in input_strings
                              ),
            task_description=SIMPLE_TASK_DESCRIPTION if self.is_simple_task else TASK_DESCRIPTION,
            task_operations_order="" if self.num_operations == 1 else "Все операции выполняются последовательно, в порядке, в котором они указаны в тексте задачи.",
        )

    @property
    def preloadedCode(self) -> str:
        return SIMPLE_PRELOADED_CODE if self.is_simple_task else PRELOADED_CODE

    def noise_input_string(self, input_string: str):
        if self.strictness == 0.0 or len(input_string) >= self.max_length:
            return input_string

        noise_chars = "!@#$%^&*()[]{}/?|~"
        noise_level = int(self.strictness * 10)

        words = input_string.split(" ")
        extra_space = self.max_length - len(input_string)

        new_words = []
        for word in words:
            if extra_space <= 0:
                new_words.append(word)
                continue

            if random.random() < self.strictness:
                noise = ''.join(random.choices(noise_chars, k=min(noise_level, extra_space)))
                if random.random() < 0.5:
                    new_words.append(noise + word)
                else:
                    new_words.append(word + noise)
                extra_space -= len(noise)
            else:
                new_words.append(word)

        return " ".join(new_words).strip()

    def test_case(self, runner: CProgramRunner, input_string: str, noise: bool = True):
        if noise:
            input_string = self.noise_input_string(input_string)

        expected_output = apply_operations(input_string, self.operations)

        try:
            output = runner.run(input_string)
        except ExecutionError as e:
            return Result.Fail(input_string, expected_output, str(e))


        if output == expected_output:
            return Result.Ok()
        else:
            return Result.Fail(input_string, expected_output, output)

    def test(self, code: str) -> Result.Ok | Result.Fail:
        if self.is_simple_task:
            code = SIMPLE_HIDDEN_CODE.format(N=self.max_length) + code

        random.seed(self.seed)
        runner = CProgramRunner(code)

        boundary_inputs = [
            "", "A", "A" * self.max_length,
            "123467890", "___  __   _",
            "BCDFG", "AEIOUY"
        ]

        random_count = 20 + self.strictness * 30
        random_inputs = [
            generate_input_string(self.operations, self.min_length, self.max_length) for _ in range(int(random_count))
        ]

        all_inputs = [(s, False) for s in boundary_inputs] + [(s, True) for s in random_inputs]

        for input_string, use_noise in all_inputs:
            result = self.test_case(runner, input_string, use_noise)
            if result != Result.Ok():
                return result

        return Result.Ok()


