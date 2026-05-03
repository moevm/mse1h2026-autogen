from prog_questions.spring.QuestionN4 import QuestionN4, CppProgramRunner, Task41, Task42, Task43
from prog_questions import Result, utility
from utility import moodleInit
import pytest

class TestQuestion4:
    def setup_method(self):
        self.question = QuestionN4(seed=42, strictness=0.5)

    def test_preloaded_code_compiles(self):
        """Проверка, что шаблон кода компилируется"""
        CppProgramRunner(self.question.preloadedCode)

    def test_task_41_basic(self):
        """Тест задания 4.1 с фиксированным seed"""
        q = moodleInit(QuestionN4, seed=100, strictness=0.3)
        q.task_type = '4.1'
        q.task = Task41(seed=100, strictness=0.3)
        
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
        assert q.test(solution) == Result.Ok()

    def test_task_42_basic(self):
        """Тест задания 4.2 с фиксированным seed"""
        q = moodleInit(QuestionN4, seed=200, strictness=0.3)
        q.task_type = '4.2'
        q.task = Task42(seed=200, strictness=0.3)
        q.task.mask = 0x05
        q.task.operation = 'shift'
        
        solution = f'''#include <iostream>
#include <unordered_map>
#include <vector>
#include <algorithm>

int main() {{
    std::unordered_map<int, int> freq;
    int num;
    const int mask = 0x{q.task.mask:02X};
    
    while (std::cin >> num && num != 0) {{
        freq[num]++;
    }}
    
    std::vector<std::tuple<int,int,int>> results;
    for (auto& [n, c] : freq) {{
        if (c >= 2 && (n & mask) == mask) {{
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
        assert q.test(solution) == Result.Ok()

    def test_task_43_basic(self):
        """Тест задания 4.3 с фиксированным seed"""
        q = moodleInit(QuestionN4, seed=300, strictness=0.3)
        q.task_type = '4.3'
        q.task = Task43(seed=300, strictness=0.3)
        
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
        assert q.test(solution) == Result.Ok()

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
        with pytest.raises(utility.CompilationError):
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