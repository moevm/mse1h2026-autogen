from prog_questions import QuestionN1, Result, utility
from utility import moodleInit
import pytest

class TestQuestionN1:
    def setup_method(self):
        self.question = moodleInit(QuestionN1, seed=123, inputSize=2)

    def test_code_preload(self):
        utility.CProgramRunner(self.question.preloadedCode)

    def test_question_text(self):
        self.question.inputBase = 8
        assert 'числа в <b>восьмеричной</b>' in self.question.questionText

    def test_code_success_run(self):
        self.question.inputSize = 2
        self.question.inputBase = 8 
        self.question.outputBase = 16
        self.question.inputFormat = 'spaces'
        self.question.outputFormat = 'plain'
        self.question.operation = 'sum'

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
        
    def test_code_success_run_pow(self):
        self.question.inputSize = 3
        self.question.inputBase = 10 
        self.question.outputBase = 10
        self.question.inputFormat = 'spaces'
        self.question.outputFormat = 'plain'
        self.question.operation = 'pow'

        assert self.question.test(r'''
            #include <stdio.h>

            int main() {
                int n = 3;
                long long res;
                                  
                for (int i = 0; i < n; i++) {
                    long long val;
                    if (scanf("%lld", &val) != 1) {
                        printf("error: %d", i);
                        return 0;              
                    }
                                  
                    if (i == 0) {
                        res = val;              
                    } else {
                        long long base = res; 
                        res = 1; 
                        for (int j = 0; j < val; j++) {
                            res *= base;          
                        }              
                    }
                }
               
                printf("%lld\n", res);
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
