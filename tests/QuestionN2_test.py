from prog_questions import QuestionN2, Result, utility
from utility import moodleInit
import pytest

class TestQuestionN2Caesar:
    question = moodleInit(QuestionN2, seed=123, maxInputSize=100)

    def test_code_preload(self):
        utility.CProgramRunner(self.question.preloadedCode)

    def test_question_text(self): #Проверка, что в описании задачи упоминаются символы и длина
        assert 'не более' in self.question.questionText
        assert 'символов</b>' in self.question.questionText
        assert 'строку' in self.question.questionText

    def test_code_success_run(self): # Проверка корректной реализации шифра Цезаря
        q = QuestionN2(seed=999, maxInputSize=100)
        q.operation = 'caesar_cipher'
        
        assert q.test(r'''
            #include <stdio.h>
            #include <string.h>

            int main() {
                char text[101];
                
                // Читаем строку, fgets сохраняет символ новой строки \n
                if (fgets(text, sizeof(text), stdin) == NULL) return 0;

                for (int i = 0; text[i] != '\0'; i++) {
                    // Сдвиг строчных букв (a-z)
                    if (text[i] >= 'a' && text[i] <= 'z') {
                        text[i] = ((text[i] - 'a' + 1) % 26) + 'a';
                    }
                    // Сдвиг заглавных букв (A-Z)
                    else if (text[i] >= 'A' && text[i] <= 'Z') {
                        text[i] = ((text[i] - 'A' + 1) % 26) + 'A';
                    }
                    // Остальные символы (цифры, пробелы, \n) не меняются
                }
                
                // Выводим строку как есть (с \n внутри)
                printf("%s", text);
                return 0;
            }
        ''') == Result.Ok()

    def test_code_compile_error(self): # Проверка, что код с синтаксической ошибкой не компилируется
        with pytest.raises(utility.CompilationError):
            self.question.test(r'''
                #include <stdio.h>
                #include <string.h>

                int main() {
                    char text[101];
                    fgets(text, sizeof(text), stdin);

                    for (int i = 0; text[i] != '\0'; i++) {
                        if (text[i] >= 'a' && text[i] <= 'z') {
                            text[i] = ((text[i] - 'a' + 1) % 26) + 'a';
                        }
                        // Ошибка: пропущена закрывающая скобка функции main
                    return 0;
                }
            ''')

    def test_code_runtime_error(self): # Проверка кода, который компилируется, но работает неверно
        q = QuestionN2(seed=888, maxInputSize=100)
        q.operation = 'caesar_cipher'
        
        assert q.test(r'''
            #include <stdio.h>
            #include <string.h>

            int main() {
                char text[101];
                fgets(text, sizeof(text), stdin);

                // Ошибка: цикл выходит за пределы строки (i <= 150)
                for (int i = 0; i <= 150; i++) {
                    if (text[i] >= 'a' && text[i] <= 'z') {
                        text[i] = ((text[i] - 'a' + 5) % 26) + 'a';
                    }
                }
                
                printf("%s", text);
                return 0;
            }
        ''') != Result.Ok()

    def test_code_wrong_answer_no_shift(self): # Ожидается Result.Fail
        q = QuestionN2(seed=777, maxInputSize=100)
        q.operation = 'caesar_cipher'
        
        assert q.test(r'''
            #include <stdio.h>
            #include <string.h>

            int main() {
                char text[101];
                fgets(text, sizeof(text), stdin);
                
                // Ошибка: строка не шифруется, просто выводится
                printf("%s", text);
                return 0;
            }
        ''') != Result.Ok()

    def test_code_wrong_answer_wrong_shift(self): # Ожидается Result.Fail
        q = QuestionN2(seed=666, maxInputSize=100)
        q.operation = 'caesar_cipher'
        
        assert q.test(r'''
            #include <stdio.h>
            #include <string.h>

            int main() {
                char text[101];
                fgets(text, sizeof(text), stdin);

                for (int i = 0; text[i] != '\0'; i++) {
                    if (text[i] >= 'a' && text[i] <= 'z') {
                        // Ошибка: сдвиг на 2 вместо 1
                        text[i] = ((text[i] - 'a' + 2) % 26) + 'a';
                    }
                    else if (text[i] >= 'A' && text[i] <= 'Z') {
                        text[i] = ((text[i] - 'A' + 2) % 26) + 'A';
                    }
                }
                
                printf("%s", text);
                return 0;
            }
        ''') != Result.Ok()

    def test_code_wrong_answer_no_wraparound(self): # Ожидается Result.Fail
        q = QuestionN2(seed=555, maxInputSize=100)
        q.operation = 'caesar_cipher'
        
        assert q.test(r'''
            #include <stdio.h>
            #include <string.h>

            int main() {
                char text[101];
                fgets(text, sizeof(text), stdin);

                for (int i = 0; text[i] != '\0'; i++) {
                    if (text[i] >= 'a' && text[i] <= 'z') {
                        // Ошибка: нет модуля 26, z превратится в {
                        text[i] = text[i] + 1;
                    }
                    else if (text[i] >= 'A' && text[i] <= 'Z') {
                        text[i] = text[i] + 1;
                    }
                }
                
                printf("%s", text);
                return 0;
            }
        ''') != Result.Ok()