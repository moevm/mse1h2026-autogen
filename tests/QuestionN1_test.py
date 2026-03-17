from prog_questions import QuestionN1, Result, utility
from utility import moodleInit
import pytest

class TestQuestionN1:
    question = moodleInit(QuestionN1, seed=123, inputSize=2)

    def test_code_preload(self):
        utility.CProgramRunner(self.question.preloadedCode)

    def test_question_text(self):
        assert 'целых чисел в <b>восьмиричной</b>' in self.question.questionText
        assert 'сумму в <b>шестнадцатиричной</b>' in self.question.questionText
        assert 'разделены <b>пробелом</b>' in self.question.questionText

    def test_code_success_run(self):
        assert self.question.test(r'''
            #include <stdio.h>

            int main() {
                int a, b;
                int read = scanf("%o %o", &a, &b);
                if (read != 2) {
                    printf("error: %d", read);
                    return 0;
                }

                printf("%x\n", a+b);
                return 0;
            }
        ''') == Result.Ok()

    def test_code_compile_error(self):
        with pytest.raises(utility.CompilationError):
            self.question.test(r'''
                #include <stdio.h>

                int main() {
                    int a, b;
                    int read = scanf("%o %o", &a, &b);
                    if (read != 2) {
                        printf("error: %d", read);
                        return 0;
                    }

                    printf("%x\n, a+b);
                    return 0;
                }
            ''')

    def test_code_runtime_error(self):
        assert self.question.test(r'''
            #include <stdio.h>

            int main() {
                int a, b;
                int read = scanf("%o %o", &a, &b);
                if (read != 2) {
                    printf("error: %d", read);
                    return 0;
                }

                printf("%s\n", a+b);
                return 0;
            }
        ''') != Result.Ok()

    def test_code_wrong_answer(self):
        assert self.question.test(r'''
            #include <stdio.h>

            int main() {
                int a, b;
                int read = scanf("%o %o", &a, &b);
                if (read != 1) {
                    printf("error: %d", read);
                    return 0;
                }

                printf("%x\n", a+b);
                return 0;
            }
        ''') != Result.Ok()
