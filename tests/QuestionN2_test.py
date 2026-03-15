from prog_questions import QuestionN2, Result, utility
from utility import moodleInit
import pytest

class TestQuestionN2:
    question = moodleInit(QuestionN2, seed=123, maxInputSize=100)

    def test_code_preload(self):
        utility.CProgramRunner(self.question.preloadedCode)

    def test_question_text(self):
        assert 'не более' in self.question.questionText
        assert 'символов</b>' in self.question.questionText
        assert 'строку' in self.question.questionText

    def test_code_success_run(self):
        q = QuestionN2(seed=999, maxInputSize=100)
        q.operation = 'remove_digits'
        assert q.test(r'''
            #include <stdio.h>
            #include <string.h>

            int main() {
                char text[101] = { 0 };
                char output[101] = { 0 };

                fgets(text, sizeof(text), stdin);

                char* ptr1 = text;
                char* ptr2 = output;
                while (*ptr1) {
                    if (!strchr("0123456789", *ptr1)) {
                        *ptr2 = *ptr1;
                        ptr2++;
                    }
                    ptr1++;
                }

                printf("%s\n", output);
                return 0;
            }
        ''') == Result.Ok()

    def test_code_compile_error(self):
        with pytest.raises(utility.CompilationError):
            self.question.test(r'''
                #include <stdio.h>
                #include <string.h>

                int main() {
                    char text[101] = { 0 };
                    char output[101] = { 0 };

                    fgets(text, sizeof(text), stdin);

                    char* ptr1 = text;
                    char* ptr2 = output;
                    while (*ptr1) {
                        if (!strchr("0123456789", *ptr1)) {
                            *ptr2 = *ptr1;
                            ptr2++;

                        ptr1++;
                    }

                    printf("%s\n", output);
                    return 0;
                }
            ''')

    def test_code_runtime_error(self):
        assert self.question.test(r'''
            #include <stdio.h>
            #include <string.h>

            int main() {
                char text[101] = { 0 };
                char output[101] = { 0 };

                fgets(text, sizeof(text), stdin);

                char* ptr1 = text;
                char* ptr2 = output;
                while (*ptr1) {
                    if (!strchr("0123456789", *ptr1)) {
                        *ptr2 = *ptr1;
                        ptr2++;
                    }
                    ptr2++;
                }

                printf("%s\n", output);
                return 0;
            }
        ''') != Result.Ok()

    def test_code_wrong_answer(self):
        assert self.question.test(r'''
            #include <stdio.h>
            #include <string.h>

            int main() {
                char text[101] = { 0 };
                char output[101] = { 0 };

                fgets(text, sizeof(text), stdin);

                char* ptr1 = text;
                char* ptr2 = output;
                while (*ptr1) {
                    if (!strchr("01456789", *ptr1)) {
                        *ptr2 = *ptr1;
                        ptr2++;
                    }
                    ptr1++;
                }

                printf("%s\n", output);
                return 0;
            }
        ''') != Result.Ok()