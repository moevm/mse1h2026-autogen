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
                        text[i] = ((text[i] - 'a' + 1) % 26) + 'a';
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

class TestQuestionN2MirrorAlphabet:
    """Тесты для операции Зеркальный алфавит (a↔z, b↔y, A↔Z, B↔Y)"""

    def test_code_preload(self):
        """Проверка, что шаблон кода компилируется"""
        q = QuestionN2(seed=123, maxInputSize=100, operation='mirror_alphabet')
        utility.CProgramRunner(q.preloadedCode)

    def test_question_text(self):
        """Проверка текста задания для зеркального алфавита"""
        q = QuestionN2(seed=123, maxInputSize=100, operation='mirror_alphabet')
        assert 'не более' in q.questionText
        assert 'символов</b>' in q.questionText
        assert 'зеркальное отображение' in q.questionText
        assert 'a↔z' in q.questionText or 'a<->z' in q.questionText or 'z' in q.questionText

    def test_code_success_run(self):
        """Проверка корректной реализации зеркального алфавита"""
        q = QuestionN2(seed=999, maxInputSize=100, operation='mirror_alphabet')
        
        assert q.test(r'''
            #include <stdio.h>
            #include <string.h>

            int main() {
                char text[101];
                
                // Читаем строку, fgets сохраняет символ новой строки \n
                if (fgets(text, sizeof(text), stdin) == NULL) return 0;

                for (int i = 0; text[i] != '\0'; i++) {
                    // Зеркальное отображение строчных букв (a↔z, b↔y, ...)
                    if (text[i] >= 'a' && text[i] <= 'z') {
                        text[i] = 'a' + 'z' - text[i];
                    }
                    // Зеркальное отображение заглавных букв (A↔Z, B↔Y, ...)
                    else if (text[i] >= 'A' && text[i] <= 'Z') {
                        text[i] = 'A' + 'Z' - text[i];
                    }
                    // Остальные символы (цифры, пробелы, \n) не меняются
                }
                
                // Выводим строку как есть (с \n внутри)
                printf("%s", text);
                return 0;
            }
        ''') == Result.Ok()

    def test_code_compile_error(self):
        """Проверка ошибки компиляции"""
        q = QuestionN2(seed=111, maxInputSize=100, operation='mirror_alphabet')
        
        with pytest.raises(utility.CompilationError):
            q.test(r'''
                #include <stdio.h>
                #include <string.h>

                int main() {
                    char text[101];
                    fgets(text, sizeof(text), stdin);

                    for (int i = 0; text[i] != '\0'; i++) {
                        if (text[i] >= 'a' && text[i] <= 'z') {
                            text[i] = 'a' + 'z' - text[i];
                        }
                    // Ошибка: пропущена закрывающая скобка функции main
                return 0;
                }
            ''')

    def test_code_runtime_error(self):
        """Проверка ошибки выполнения (выход за границы массива)"""
        q = QuestionN2(seed=888, maxInputSize=100, operation='mirror_alphabet')
        
        assert q.test(r'''
            #include <stdio.h>
            #include <string.h>

            int main() {
                char text[101];
                fgets(text, sizeof(text), stdin);

                // Ошибка: цикл выходит за пределы строки (i <= 150)
                for (int i = 0; i <= 150; i++) {
                    if (text[i] >= 'a' && text[i] <= 'z') {
                        text[i] = 'a' + 'z' - text[i];
                    }
                }
                
                printf("%s", text);
                return 0;
            }
        ''') != Result.Ok()

    def test_code_wrong_answer_no_mirror(self):
        """Проверка: код не выполняет зеркальное отображение (просто копирует)"""
        q = QuestionN2(seed=777, maxInputSize=100, operation='mirror_alphabet')
        
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

    def test_code_wrong_answer_caesar_instead(self):
        """Проверка: вместо зеркального алфавита применён шифр Цезаря (сдвиг на 1)"""
        q = QuestionN2(seed=666, maxInputSize=100, operation='mirror_alphabet')
        
        assert q.test(r'''
            #include <stdio.h>
            #include <string.h>

            int main() {
                char text[101];
                fgets(text, sizeof(text), stdin);

                for (int i = 0; text[i] != '\0'; i++) {
                    if (text[i] >= 'a' && text[i] <= 'z') {
                        // Ошибка: сдвиг на 1 вместо зеркального отображения
                        text[i] = ((text[i] - 'a' + 1) % 26) + 'a';
                    }
                    else if (text[i] >= 'A' && text[i] <= 'Z') {
                        text[i] = ((text[i] - 'A' + 1) % 26) + 'A';
                    }
                }
                
                printf("%s", text);
                return 0;
            }
        ''') != Result.Ok()

    def test_code_wrong_answer_reverse_string(self):
        """Проверка: вместо замены букв строка просто переворачивается"""
        q = QuestionN2(seed=555, maxInputSize=100, operation='mirror_alphabet')
        
        assert q.test(r'''
            #include <stdio.h>
            #include <string.h>

            int main() {
                char text[101];
                fgets(text, sizeof(text), stdin);
                
                // Ошибка: строка переворачивается вместо зеркальной замены букв
                int len = strlen(text);
                if (len > 0 && text[len-1] == '\n') len--;
                
                for (int i = 0; i < len / 2; i++) {
                    char tmp = text[i];
                    text[i] = text[len - 1 - i];
                    text[len - 1 - i] = tmp;
                }
                
                printf("%s", text);
                return 0;
            }
        ''') != Result.Ok()

    def test_mirror_boundary_cases(self):
        """Проверка граничных случаев (a↔z, A↔Z) напрямую"""
        q = QuestionN2(seed=444, maxInputSize=100, operation='mirror_alphabet')
        
        # Проверка логики напрямую через applyOperation
        assert q.applyOperation('a') == 'z'
        assert q.applyOperation('z') == 'a'
        assert q.applyOperation('A') == 'Z'
        assert q.applyOperation('Z') == 'A'
        assert q.applyOperation('b') == 'y'
        assert q.applyOperation('y') == 'b'
        assert q.applyOperation('abc') == 'zyx'
        assert q.applyOperation('ABC') == 'ZYX'
        assert q.applyOperation('a1z') == 'z1a'  # цифры не меняются
        assert q.applyOperation('!@#') == '!@#'  # спецсимволы не меняются
        
        # Проверка, что двойное применение возвращает исходную строку
        assert q.applyOperation(q.applyOperation('Hello123')) == 'Hello123'
        assert q.applyOperation(q.applyOperation('abcXYZ')) == 'abcXYZ'