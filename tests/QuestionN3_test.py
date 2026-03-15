from prog_questions import QuestionN3, Result, utility
from utility import moodleInit
import pytest

class TestQuestionN3:
    question = moodleInit(QuestionN3, seed=456)

    def test_code_preload(self):
        utility.CProgramRunner(self.question.preloadedCode)

    def test_question_text(self):
        assert f'<b>N</b> (не более 30)' in self.question.questionText
        assert f'результат побитового исключащего ИЛИ (XOR)' in self.question.questionText
        assert f'неотрицательных целых чисел' in self.question.questionText
        assert f'индексам, кратным 3' in self.question.questionText

    def test_code_success_run(self):
        assert self.question.test(r'''
            #include <stdio.h>

            int main() {
                unsigned long numbers[30] = { 0 };
                int n = 0;

                scanf("%d", &n);
                for (size_t i = 0; i < n; i++){
                    scanf("%lu", &numbers[i]);
                }

                unsigned long prod = 0;
                for (size_t i = 0; i < n; i ++) {
                    if (i % 3 == 0) {  
                        prod ^= numbers[i];
                    }
                }

                printf("%lu\n", prod);

                return 0;
            }
        ''') == Result.Ok()

    def test_code_compile_error(self):
        with pytest.raises(utility.CompilationError):
            self.question.test(r'''
                include <stdio.h>

                int main() {
                    int numbers[100] = { 0 };
                    int n = 0;

                    scanf("%d", &n);
                    for (size_t i = 0; i < n; i++){
                        scanf("%lu", &numbers[i]);
                    }

                    unsigned long prod = 0;
                    for (size_t i = 0; i < n; i ++) {
                        if (i % 3 == 0) {  
                            prod ^= numbers[i];
                        }
                    }

                    printf("%lu\n", prod);

                    return 0;
                }
            ''')

    def test_code_runtime_error(self):
        assert self.question.test(r'''
            #include <stdio.h>

            int main() {
                int numbers[2] = { 0 };
                int n = 0;

                scanf("%d", &n);
                for (size_t i = 0; i < n; i++){
                    scanf("%lu", &numbers[i]);
                }

                unsigned long prod = 0;
                for (size_t i = 0; i < n; i++) {
                    if (i % 3 == 0) {  
                        prod ^= numbers[i];
                    }
                }

                printf("%lu\n", prod);

                return 0;
            }
        ''') != Result.Ok()

    def test_code_wrong_answer(self):
        assert self.question.test(r'''
            #include <stdio.h>

            int main() {
                int numbers[100] = { 0 };
                int n = 0;

                scanf("%d", &n);
                for (size_t i = 0; i < n; i++){
                    scanf("%lu", &numbers[i]);
                }

                unsigned long prod = 0;
                for (size_t i = 0; i < n; i ++) {
                    if (i % 3 == 0) {  
                        prod ^= numbers[i];
                        prod += 1;
                    }
                    
                }

                printf("%lld\n", prod);

                return 0;
            }
        ''') != Result.Ok()
