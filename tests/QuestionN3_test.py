from prog_questions import QuestionN3, Result, utility
from utility import moodleInit
import pytest
import random

class TestQuestionN3:
    question1 = moodleInit(QuestionN3, seed=123)
    question2 = moodleInit(QuestionN3, seed=456)

    def test_code_preload(self):
        utility.CProgramRunner(self.question1.preloadedCode)
        utility.CProgramRunner(self.question2.preloadedCode)

    def test_question_text(self):
        assert f'<b>N</b> (не более 30)' in self.question1.questionText
        assert f'сумму' in self.question1.questionText
        assert f'чисел с плавающей точкой' in self.question1.questionText
        assert f'нечётным' in self.question1.questionText

        assert f'<b>N</b> (не более 30)' in self.question2.questionText
        assert f'результат побитового исключащего ИЛИ (XOR)' in self.question2.questionText
        assert f'целых чисел' in self.question2.questionText
        assert f'индексам, кратным 3' in self.question2.questionText

    def test_code_success_run1(self):
        assert self.question1.test(r'''
            #include <stdio.h>

            int main() {
                double numbers[30] = { 0 };
                int n = 0;

                scanf("%d", &n);
                for (size_t i = 0; i < n; i++){
                    scanf("%lf", &numbers[i]);
                }

                double prod = 0;
                for (size_t i = 1; i < n; i+=2) {
                    prod += numbers[i];
                }

                printf("%.6f\n", prod);

                return 0;
            }
        ''') == Result.Ok()

    
    def test_code_success_run2(self):
        assert self.question2.test(r'''
            #include <stdio.h>

            int main() {
                size_t numbers[30] = { 0 };
                int n = 0;

                scanf("%d", &n);
                for (size_t i = 0; i < n; i++){
                    scanf("%zu", &numbers[i]);
                }

                size_t prod = 0;
                for (size_t i = 0; i < n; i ++) {
                    if (i % 3 == 0) {  
                        prod ^= numbers[i];
                    }
                }

                printf("%zu\n", prod);

                return 0;
            }
        ''') == Result.Ok()

    def test_code_compile_error1(self):
        with pytest.raises(utility.CompilationError):
            self.question1.test(r'''
                include <stdio.h>

                int main() {
                    long long numbers[30] = { 0 };
                    int n = 0;

                    scanf("%d", &n);
                    for (size_t i = 0; i < n; i++){
                        scanf("%lld", &numbers[i]);
                    }

                    long long prod = 0;
                    for (size_t i = 1; i < n; i+=2) {
                        prod += numbers[i];
                    }
                    printf("%lld\n", prod);

                    return 0;
                }
            ''')

    def test_code_compile_error2(self):
        with pytest.raises(utility.CompilationError):
            self.question2.test(r'''
                include <stdio.h>

                int main() {
                    size_t numbers[30] = { 0 };
                    int n = 0;

                    scanf("%d", &n);
                    for (size_t i = 0; i < n; i++){
                        scanf("%zu", &numbers[i]);
                    }

                    size_t prod = 0;
                    for (size_t i = 0; i < n; i ++) {
                        if (i % 3 == 0) {  
                            prod ^= numbers[i];
                        }
                    }

                    printf("%zu\n", prod);

                    return 0;
                }
            ''')

    def test_code_runtime_error1(self):
        assert self.question1.test(r'''
            #include <stdio.h>

            int main() {
                long long numbers[2] = { 0 };
                int n = 0;

                scanf("%d", &n);
                for (size_t i = 0; i < n; i++){
                    scanf("%lld", &numbers[i]);
                }

                long long prod = 0;
                for (size_t i = 1; i < n; i+=2) {
                    prod += numbers[i];
                }
                                   
                printf("%lld\n", prod);

                return 0;
            }
        ''') != Result.Ok()

    def test_code_runtime_error2(self):
        assert self.question2.test(r'''
            #include <stdio.h>

            int main() {
                size_t numbers[2] = { 0 };
                int n = 0;

                scanf("%d", &n);
                for (size_t i = 0; i < n; i++){
                    scanf("%zu", &numbers[i]);
                }

                size_t prod = 0;
                for (size_t i = 0; i < n; i++) {
                    if (i % 3 == 0) {  
                        prod ^= numbers[i];
                    }
                }

                printf("%zu\n", prod);

                return 0;
            }
        ''') != Result.Ok()

    def test_code_wrong_answer1(self):
        assert self.question1.test(r'''
            #include <stdio.h>

            int main() {
                long long numbers[30] = { 0 };
                int n = 0;

                scanf("%d", &n);
                for (size_t i = 0; i < n; i++){
                    scanf("%lld", &numbers[i]);
                }

                long long prod = 0;
                for (size_t i = 1; i < n; i+=2) {
                    prod += numbers[i];
                    prod += 1;
                }

                printf("%lld\n", prod);

                return 0;
            }
        ''') != Result.Ok()

    def test_code_wrong_answer2(self):
        assert self.question2.test(r'''
            #include <stdio.h>

            int main() {
                size_t numbers[30] = { 0 };
                int n = 0;

                scanf("%d", &n);
                for (size_t i = 0; i < n; i++){
                    scanf("%zu", &numbers[i]);
                }

                size_t prod = 0;
                for (size_t i = 0; i < n; i ++) {
                    if (i % 3 == 0) {  
                        prod ^= numbers[i];
                        prod += 1;
                    }
                    
                }

                printf("%zu\n", prod);

                return 0;
            }
        ''') != Result.Ok()
        
    def test_generate_number_ranges_by_type(self):
        q = QuestionN3(seed=100)
        samples = 200

        q.dataType = 'char'
        for _ in range(samples):
            value = q.generateNumber()
            assert -128 <= value <= 127

        q.dataType = 'unsigned char'
        for _ in range(samples):
            value = q.generateNumber()
            assert 0 <= value <= 255

        q.dataType = 'int'
        for _ in range(samples):
            value = q.generateNumber()
            assert -1_000_000 <= value <= 1_000_000

        q.dataType = 'unsigned int'
        for _ in range(samples):
            value = q.generateNumber()
            assert 0 <= value <= 1_000_000

        q.dataType = '_Bool'
        for _ in range(samples):
            value = q.generateNumber()
            assert value in [0, 1]

        q.dataType = 'double'
        for _ in range(samples):
            value = q.generateNumber()
            assert isinstance(value, float)
            assert -1e6 <= value <= 1e6

    def test_generate_test_bool_output_is_strict_binary(self):
        q = QuestionN3(seed=300)
        q.operationType = 'sum'
        q.elementType = 'all'
        q.dataType = '_Bool'

        for seed in [10, 20, 30, 40, 50]:
            state = random.getstate()
            random.seed(seed)
            _, expected = q.generateTest(min_rand_len=3)
            random.setstate(state)
            assert expected in ['0', '1']

    def test_generate_test_double_output_has_six_digits(self):
        q = QuestionN3(seed=400)
        q.operationType = 'average'
        q.elementType = 'all'
        q.dataType = 'double'

        state = random.getstate()
        random.seed(123)
        _, expected = q.generateTest(min_rand_len=4)
        random.setstate(state)

        assert '.' in expected
        whole, fraction = expected.split('.', 1)
        assert whole.lstrip('-').isdigit()
        assert len(fraction) == 6
        assert fraction.isdigit()
