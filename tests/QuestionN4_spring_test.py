from prog_questions.spring.QuestionN4 import QuestionN4, Task4ConfigGenerator
from prog_questions.utility import CppProgramRunner, CompilationError
from prog_questions.QuestionBase import Result
from utility import moodleInit
import pytest
import random

def assert_cpp_solution_works_on_config(solution_code, config, task_type):
    """Компилирует и запускает решение на входных данных из config, сравнивает с эталоном."""
    runner = CppProgramRunner(solution_code)
    q = QuestionN4(seed=config.seed, strictness=config.strictness)
    input_data = q._generate_input(config)
    expected = None
    if task_type == '4.1':
        expected = q._expected_41(config)
    elif task_type == '4.2':
        expected = q._expected_42(config)
    else:
        expected = q._expected_43(config)
    try:
        output = runner.run(input_data).replace('\r', '').strip()
    except Exception as e:
        raise AssertionError(f"Ошибка выполнения: {e}")
    assert output == expected.strip(), f"Вывод:\n{output}\nОжидалось:\n{expected}"


class TestQuestion4:
    def setup_method(self):
        self.question = QuestionN4(seed=42, strictness=0.5)

    def test_preloaded_code_compiles(self):
        """Проверка, что шаблон кода компилируется"""
        CppProgramRunner(self.question.preloadedCode)

    def test_task_41_basic(self):
        """Тест задания 4.1 на конкретной конфигурации (без фильтра)"""
        gen = Task4ConfigGenerator(seed=100, strictness=0.3)
        config = gen.generate(task_type_override='4.1')
        config.filter_type = 'none'
        solution = '''#include <iostream>
#include <map>
#include <vector>
#include <string>
#include <algorithm>

int main() {
    std::map<char, std::vector<std::string>> groups;
    std::string word;
    while (std::cin >> word) {
        if (word == "#") break;
        if (!word.empty() && word.back() == '#') {
            word.pop_back();
            if (word == "#") break;
        }
        if (!word.empty()) {
            groups[word[0]].push_back(word);
        }
    }
    for (auto& [letter, words] : groups) {
        std::sort(words.begin(), words.end());
        std::cout << letter << ":";
        for (const auto& w : words) std::cout << " " << w;
        std::cout << "\\n";
    }
    return 0;
}'''
        assert_cpp_solution_works_on_config(solution, config, '4.1')

    def test_task_42_basic(self):
        """Тест задания 4.2 на конкретной конфигурации (маска 0x05, операция shift, min_freq=2)"""
        gen = Task4ConfigGenerator(seed=200, strictness=0.3)
        config = gen.generate(task_type_override='4.2')
        config.mask = 0x05
        config.operation = 'shift'
        config.min_freq = 2
        config.numbers = [5, 5, 5, 13, 13, 13, 13, 1, 2, 3]  # 5 (3 раза), 13 (4 раза)
        solution = f'''#include <iostream>
#include <unordered_map>
#include <vector>
#include <algorithm>
#include <tuple>

int main() {{
    std::unordered_map<int, int> freq;
    int num;
    const int mask = 0x{config.mask:02X};
    while (std::cin >> num && num != 0) {{
        freq[num]++;
    }}
    std::vector<std::tuple<int,int,int>> results;
    for (auto& [n, c] : freq) {{
        if (c >= {config.min_freq} && (n & mask) == mask) {{
            results.emplace_back(n, c, n << c);
        }}
    }}
    std::sort(results.begin(), results.end());
    if (results.empty()) {{
        std::cout << "NO_DATA";
    }} else {{
        for (auto& [n, c, r] : results) {{
            std::cout << n << " " << c << " " << r << "\\n";
        }}
    }}
    return 0;
}}'''
        assert_cpp_solution_works_on_config(solution, config, '4.2')

    def test_task_43_basic(self):
        """Тест задания 4.3 на конкретной конфигурации (произвольные команды, но решение универсально)"""
        gen = Task4ConfigGenerator(seed=300, strictness=0.3)
        config = gen.generate(task_type_override='4.3')
        solution = '''#include <iostream>
#include <string>
#include <unordered_map>

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n;
    std::cin >> n;
    std::unordered_map<std::string, int> counters;
    for (int i = 0; i < n; ++i) {
        std::string cmd, word;
        std::cin >> cmd >> word;
        if (cmd == "ADD") {
            counters[word]++;
        } else if (cmd == "SUB" && counters[word] > 0) {
            counters[word]--;
        } else if (cmd == "GET") {
            std::cout << counters[word] << "\\n";
        }
    }
    return 0;
}'''
        assert_cpp_solution_works_on_config(solution, config, '4.3')

    def test_wrong_answer_detected(self):
        """Проверка, что неправильный ответ детектируется"""
        wrong_code = '''#include <stdio.h>
int main() { printf("42\\n"); return 0; }'''
        result = self.question.test(wrong_code)
        assert result != Result.Ok()
        assert isinstance(result, Result.Fail)

    def test_compilation_error_caught(self):
        """Проверка обработки ошибки компиляции"""
        broken_code = '''#include <iostream>
int main() { std::cout << "missing semicolon" return 0; }'''
        with pytest.raises(CompilationError):
            self.question.test(broken_code)

    def test_all_task_types_possible(self):
        """Проверка, что все три типа заданий могут быть выбраны"""
        types_seen = set()
        for seed in range(1, 50):
            q = moodleInit(QuestionN4, seed=seed, strictness=0.5)
            types_seen.add(q.task_type)
            if len(types_seen) == 3:
                break
        assert len(types_seen) == 3, f"Only saw task types: {types_seen}"


class TestTask4ConfigGenerator:
    def test_generates_all_types(self):
        from prog_questions.spring.QuestionN4 import Task4ConfigGenerator
        types_seen = set()
        for seed in range(20):
            gen = Task4ConfigGenerator(seed, 0.7)
            config = gen.generate()
            types_seen.add(config.task_type)
        assert types_seen == {'4.1', '4.2', '4.3'}

    def test_41_parameters_vary(self):
        from prog_questions.spring.QuestionN4 import Task4ConfigGenerator
        filters_seen = set()
        words_lengths = []
        for seed in range(30):
            gen = Task4ConfigGenerator(seed, 0.7)
            config = gen.generate(task_type_override='4.1')
            filters_seen.add(config.filter_type)
            words_lengths.append(len(config.words))
        assert len(filters_seen) >= 3
        assert max(words_lengths) > min(words_lengths)

    def test_42_parameters_vary(self):
        from prog_questions.spring.QuestionN4 import Task4ConfigGenerator
        ops = set()
        masks = set()
        for seed in range(20):
            gen = Task4ConfigGenerator(seed, 0.7)
            config = gen.generate(task_type_override='4.2')
            ops.add(config.operation)
            masks.add(config.mask)
        assert len(ops) == 2
        assert len(masks) >= 3

    def test_43_parameters_vary(self):
        from prog_questions.spring.QuestionN4 import Task4ConfigGenerator
        lengths = set()
        has_get = False
        for seed in range(20):
            gen = Task4ConfigGenerator(seed, 0.7)
            config = gen.generate(task_type_override='4.3')
            lengths.add(len(config.commands))
            if any(op == 'GET' for op, _ in config.commands):
                has_get = True
        assert len(lengths) > 1
        assert has_get
    
    def test_task_type_override_works(self):
        """Проверка, что параметр task_type_override принудительно задаёт тип задания"""
        for override in ['4.1', '4.2', '4.3']:
            q = QuestionN4(seed=42, task_type_override=override)
            assert q.task_type == override, f"Ожидался {override}, получен {q.task_type}"
            # Проверяем, что текст вопроса соответствует типу
            if override == '4.1':
                assert 'Группировка по ключу' in q.questionText
            elif override == '4.2':
                assert 'Частотный фильтр с маской' in q.questionText
            else:
                assert 'Динамический учёт слов' in q.questionText

    def test_without_override_generates_random_types(self):
        """Без параметра task_type_override типы должны меняться при разных seed"""
        types_seen = set()
        for seed in range(20):
            q = QuestionN4(seed=seed)
            types_seen.add(q.task_type)
        assert len(types_seen) == 3, f"Ожидались все 3 типа, получены {types_seen}"

    def test_empty_result_shows_no_data(self):
        """
        Проверяет, что если после фильтрации не осталось ни одной группы/числа,
        программа выводит "NO_DATA", а не пустую строку.
        """

        gen = Task4ConfigGenerator(seed=123, strictness=0.3)
        config = gen.generate(task_type_override='4.1')
        config.filter_type = 'exact_count'
        config.threshold = 10
        config.words = ['cat', 'dog']
        
        solution = '''#include <iostream>
    #include <map>
    #include <vector>
    #include <string>
    #include <algorithm>
    int main() {
        std::map<char, std::vector<std::string>> groups;
        std::string word;
        while (std::cin >> word && word != "#") {
            if (!word.empty()) groups[word[0]].push_back(word);
        }
        bool printed = false;
        for (auto& [letter, words] : groups) {
            if ((int)words.size() == 10) {  // наш точный порог
                std::sort(words.begin(), words.end());
                std::cout << letter << ":";
                for (const auto& w : words) std::cout << " " << w;
                std::cout << "\\n";
                printed = true;
            }
        }
        if (!printed) std::cout << "NO_DATA";
        return 0;
    }'''
        
        assert_cpp_solution_works_on_config(solution, config, '4.1')
