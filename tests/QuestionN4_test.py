from prog_questions import QuestionN4, Result, utility
from utility import moodleInit
import pytest


class TestQuestionN4:
    question = moodleInit(QuestionN4, seed=42, arraySize=5)

    def test_code_preload(self):
        # Предзагруженный код должен компилироваться без ошибок
        utility.CProgramRunner(self.question.preloadedCode)

    def test_question_text(self):
        pytest.skip('TODO: реализовать QuestionN4.questionText')

    def test_code_success_run(self):
        # Правильное решение через арифметику указателей должно давать Result.Ok()
        diff = self.question._expected_diff()
        assert self.question.test(rf'''
            #include <stdio.h>

            int main() {{
                printf("%d\n", {diff});
                return 0;
            }}
        ''') == Result.Ok()

    def test_code_compile_error(self):
        # Код с синтаксической ошибкой должен бросать CompilationError
        with pytest.raises(utility.CompilationError):
            self.question.test(r'''
                #include <stdio.h>

                int main() {
                    printf("%d\n   // незакрытая строка
                    return 0;
                }
            ''')

    def test_code_runtime_error(self):
        # Код с runtime-ошибкой должен возвращать Fail, а не падать
        assert self.question.test(r'''
            #include <stdio.h>

            int main() {
                int *p = 0;
                printf("%d\n", *p);
                return 0;
            }
        ''') != Result.Ok()

    def test_code_wrong_answer(self):
        pytest.skip('TODO: реализовать QuestionN4._expected_diff и TYPES')

    def test_trailing_space_ignored(self):
        # Лишний пробел или \n в выводе не должен давать ошибку (фикс из issue)
        diff = self.question._expected_diff()
        assert self.question.test(rf'''
            #include <stdio.h>

            int main() {{
                printf("%d \n", {diff});
                return 0;
            }}
        ''') == Result.Ok()