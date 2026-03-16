from prog_questions import QuestionN5, Result, utility
from utility import moodleInit
import pytest

class TestQuestionN5:
    question = moodleInit(QuestionN5, seed=123, maxSentenceSize=100)

    def test_code_preload(self):
        utility.CProgramRunner(self.question.preloadedCode)

    def test_question_text(self):
        assert 'наибольшим' in self.question.questionText or 'наименьшим' in self.question.questionText
        assert ': строка' in self.question.questionText

    def test_code_success_run(self):
        self.question.metricBase = 'length'
        self.question.metricDirection = 'max'
        assert self.question.test(r'''
            #include <stdio.h>

            int main() {
                size_t n;
                scanf("%zu\n", &n);

                char sentence[101] = { 0 };
                char bestSentence[101] = { 0 };
                int bestMetric = 0;

                for (size_t i = 0; i < n; i++) {
                    fgets(sentence, sizeof(sentence), stdin);

                    char* ch = sentence;
                    while (*ch) {
                        if (*ch == '\n') {
                            *ch = '\0';
                            break;
                        }
                        ch++;
                    }

                    int metric = 0;
                    ch = sentence;
                    while (*ch) {
                        metric++;
                        ch++;
                    }

                    if (metric <= bestMetric) continue;

                    ch = sentence;
                    char* target = bestSentence;
                    while (*ch) {
                        *target = *ch;
                        ch++;
                        target++;
                    }
                    *target = '\0';
                    bestMetric = metric;
                }

                printf("%d: %s\n", bestMetric, bestSentence);
                return 0;
            }
        ''') == Result.Ok()

    def test_code_compile_error(self):
        with pytest.raises(utility.CompilationError):
            self.question.test(r'''
                #include <stdio.h>

                int main() {
                    size_t n;
                    scanf("%zu\n", &n);

                    char sentence[101] = { 0 };
                    char bestSentence[101] = { 0 };
                    int bestMetric = 0;

                    for (size_t i = 0; i < n; i++) {
                        fgets(sentence, sizeof(sentence), stdin);

                        char* ch = sentence;
                        while (*ch) {
                            if (*ch == '\n') {
                                *ch = '\0';
                                break;
                            }
                            ch++;
                        }

                        int metric = 0;
                        ch = sentence;
                        while (*ch) {
                            metric++;
                            ch++;
                        }

                        if (metric <= bestMetric) continue;

                        ch = sentence;
                        char* target = bestSentence;
                        while (*ch) {
                            *target = *ch
                            ch++;
                            target++;
                        }
                        *target = '\0';
                        bestMetric = metric;
                    }

                    printf("%d: %s\n", bestMetric, bestSentence);
                    return 0;
                }
            ''')

    def test_code_stringh_prohibit(self):
        with pytest.raises(utility.CompilationError):
            self.question.test(r'''
                #include <stdio.h>
                #include <string.h>

                int main() {
                    size_t n;
                    scanf("%zu\n", &n);

                    char sentence[101] = { 0 };
                    char bestSentence[101] = { 0 };
                    int bestMetric = 0;

                    for (size_t i = 0; i < n; i++) {
                        fgets(sentence, sizeof(sentence), stdin);

                        char* ch = sentence;
                        while (*ch) {
                            if (*ch == '\n') {
                                *ch = '\0';
                                break;
                            }
                            ch++;
                        }

                        int metric = 0;
                        ch = sentence;
                        while (*ch) {
                            metric++;
                            ch++;
                        }

                        if (metric <= bestMetric) continue;

                        ch = sentence;
                        char* target = bestSentence;
                        while (*ch) {
                            *target = *ch;
                            ch++;
                            target++;
                        }
                        *target = '\0';
                        bestMetric = metric;
                    }

                    printf("%d: %s\n", bestMetric, bestSentence);
                    return 0;
                }

                #undef _STRING_H
            ''')

    def test_code_runtime_error(self):
        self.question.metricBase = 'length'
        self.question.metricDirection = 'max'
        assert self.question.test(r'''
            #include <stdio.h>

            int main() {
                size_t n;
                scanf("%zu\n", &n);

                char sentence[101] = { 0 };
                char bestSentence[101] = { 0 };
                int bestMetric = 0;

                for (size_t i = 0; i < n; i++) {
                    fgets(sentence, sizeof(sentence), stdin);

                    char* ch = sentence;
                    while (*ch) {
                        if (*ch == '\n') {
                            *ch = '\0';
                            break;
                        }
                        ch++;
                    }

                    int metric = 0;
                    while (*ch) {
                        metric++;
                        ch++;
                    }

                    if (metric <= bestMetric) continue;

                    char* target = bestSentence;
                    while (*ch) {
                        *target = *ch;
                        ch++;
                        target++;
                    }
                    *target = '\0';
                    bestMetric = metric;
                }

                printf("%d: %s\n", bestMetric, bestSentence);
                return 0;
            }
        ''') != Result.Ok()

    def test_code_wrong_answer(self):
        self.question.metricBase = 'length'
        self.question.metricDirection = 'max'
        assert self.question.test(r'''
            #include <stdio.h>

            int main() {
                size_t n;
                scanf("%zu\n", &n);

                char sentence[2] = { 0 };
                char bestSentence[2] = { 0 };
                int bestMetric = 0;

                for (size_t i = 0; i < n; i++) {
                    fgets(sentence, sizeof(sentence), stdin);

                    char* ch = sentence;
                    while (*ch) {
                        if (*ch == '\n') {
                            *ch = '\0';
                            break;
                        }
                        ch++;
                    }

                    int metric = 0;
                    ch = sentence;
                    while (*ch) {
                        metric++;
                        ch++;
                    }

                    if (metric <= bestMetric) continue;

                    ch = sentence;
                    char* target = bestSentence;
                    while (*ch) {
                        *target = *ch;
                        ch++;
                        target++;
                    }
                    *target = '\0';
                    bestMetric = metric;
                }

                printf("%d: %s\n", bestMetric, bestSentence);
                return 0;
            }
        ''') != Result.Ok()


class TestQuestionN5_Metrics:
    question = moodleInit(QuestionN5, seed=456, maxSentenceSize=100)

    def test_metric_length_max(self):
        """Тест метрики: длина строки (макс)"""
        self.question.metricBase = 'length'
        self.question.metricDirection = 'max'
        assert self.question.test(r'''
            #include <stdio.h>

            int main() {
                size_t n;
                scanf("%zu\n", &n);

                char sentence[101] = { 0 };
                char bestSentence[101] = { 0 };
                int bestMetric = -1;

                for (size_t i = 0; i < n; i++) {
                    fgets(sentence, sizeof(sentence), stdin);

                    char* ch = sentence;
                    while (*ch) {
                        if (*ch == '\n') {
                            *ch = '\0';
                            break;
                        }
                        ch++;
                    }

                    int metric = 0;
                    ch = sentence;
                    while (*ch) {
                        metric++;
                        ch++;
                    }

                    if (metric <= bestMetric) continue;

                    ch = sentence;
                    char* target = bestSentence;
                    while (*ch) {
                        *target = *ch;
                        ch++;
                        target++;
                    }
                    *target = '\0';
                    bestMetric = metric;
                }

                printf("%d: %s\n", bestMetric, bestSentence);
                return 0;
            }
        ''') == Result.Ok()
        

    def test_metric_length_min(self):
        """Тест метрики: длина строки (мин)"""
        self.question.metricBase = 'length'
        self.question.metricDirection = 'min'
        assert self.question.test(r'''
            #include <stdio.h>

            int main() {
                size_t n;
                scanf("%zu\n", &n);

                // Увеличен размер буфера
                char sentence[256] = { 0 };
                char bestSentence[256] = { 0 };
                int bestMetric = -1;
                int first = 1;

                for (size_t i = 0; i < n; i++) {
                    fgets(sentence, sizeof(sentence), stdin);

                    char* ch = sentence;
                    while (*ch) {
                        if (*ch == '\n') {
                            *ch = '\0';
                            break;
                        }
                        ch++;
                    }

                    int metric = 0;
                    ch = sentence;
                    while (*ch) {
                        metric++;
                        ch++;
                    }

                    if (!first && metric >= bestMetric) continue;

                    ch = sentence;
                    char* target = bestSentence;
                    while (*ch) {
                        *target = *ch;
                        ch++;
                        target++;
                    }
                    *target = '\0';
                    bestMetric = metric;
                    first = 0;
                }

                printf("%d: %s\n", bestMetric, bestSentence);
                return 0;
            }
        ''') == Result.Ok()

    def test_metric_words_max(self):
        """Тест метрики: количество слов (макс)"""
        self.question.metricBase = 'words'
        self.question.metricDirection = 'max'
        assert self.question.test(r'''
            #include <stdio.h>

            int main() {
                size_t n;
                scanf("%zu\n", &n);

                char sentence[101] = { 0 };
                char bestSentence[101] = { 0 };
                int bestMetric = -1;

                for (size_t i = 0; i < n; i++) {
                    fgets(sentence, sizeof(sentence), stdin);

                    char* ch = sentence;
                    while (*ch) {
                        if (*ch == '\n') {
                            *ch = '\0';
                            break;
                        }
                        ch++;
                    }

                    int metric = 0;
                    int inWord = 0;
                    ch = sentence;
                    while (*ch) {
                        if (*ch != ' ' && *ch != '.') {
                            if (!inWord) {
                                metric++;
                                inWord = 1;
                            }
                        } else {
                            inWord = 0;
                        }
                        ch++;
                    }

                    if (metric <= bestMetric) continue;

                    ch = sentence;
                    char* target = bestSentence;
                    while (*ch) {
                        *target = *ch;
                        ch++;
                        target++;
                    }
                    *target = '\0';
                    bestMetric = metric;
                }

                printf("%d: %s\n", bestMetric, bestSentence);
                return 0;
            }
        ''') == Result.Ok()
        
    def test_metric_words_min(self):
        """Тест метрики: количество слов (мин)"""
        self.question.metricBase = 'words'
        self.question.metricDirection = 'min'
        assert self.question.test(r'''
            #include <stdio.h>

            int main() {
                size_t n;
                scanf("%zu\n", &n);

                // Увеличен размер буфера
                char sentence[256] = { 0 };
                char bestSentence[256] = { 0 };
                int bestMetric = -1;
                int first = 1;

                for (size_t i = 0; i < n; i++) {
                    fgets(sentence, sizeof(sentence), stdin);

                    char* ch = sentence;
                    while (*ch) {
                        if (*ch == '\n') {
                            *ch = '\0';
                            break;
                        }
                        ch++;
                    }

                    int metric = 0;
                    int inWord = 0;
                    ch = sentence;
                    while (*ch) {
                        if (*ch != ' ' && *ch != '.') {
                            if (!inWord) {
                                metric++;
                                inWord = 1;
                            }
                        } else {
                            inWord = 0;
                        }
                        ch++;
                    }

                    if (!first && metric >= bestMetric) continue;

                    ch = sentence;
                    char* target = bestSentence;
                    while (*ch) {
                        *target = *ch;
                        ch++;
                        target++;
                    }
                    *target = '\0';
                    bestMetric = metric;
                    first = 0;
                }

                printf("%d: %s\n", bestMetric, bestSentence);
                return 0;
            }
        ''') == Result.Ok()

    def test_metric_vowel_count_max(self):
        """Тест метрики: количество гласных"""
        self.question.metricBase = 'vowel_count'
        self.question.metricDirection = 'max'
        assert self.question.test(r'''
            #include <stdio.h>

            int isVowel(char c) {
                if (c >= 'A' && c <= 'Z') c = c + 32;
                return c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u';
            }

            int main() {
                size_t n;
                scanf("%zu\n", &n);

                char sentence[101] = { 0 };
                char bestSentence[101] = { 0 };
                int bestMetric = -1;

                for (size_t i = 0; i < n; i++) {
                    fgets(sentence, sizeof(sentence), stdin);

                    char* ch = sentence;
                    while (*ch) {
                        if (*ch == '\n') {
                            *ch = '\0';
                            break;
                        }
                        ch++;
                    }

                    int metric = 0;
                    ch = sentence;
                    while (*ch) {
                        if (isVowel(*ch)) {
                            metric++;
                        }
                        ch++;
                    }

                    if (metric <= bestMetric) continue;

                    ch = sentence;
                    char* target = bestSentence;
                    while (*ch) {
                        *target = *ch;
                        ch++;
                        target++;
                    }
                    *target = '\0';
                    bestMetric = metric;
                }

                printf("%d: %s\n", bestMetric, bestSentence);
                return 0;
            }
        ''') == Result.Ok()

    def test_metric_digit_count_max(self):
        """Тест метрики: количество цифр"""
        self.question.metricBase = 'digit_count'
        self.question.metricDirection = 'max'
        assert self.question.test(r'''
            #include <stdio.h>

            int main() {
                size_t n;
                scanf("%zu\n", &n);

                char sentence[101] = { 0 };
                char bestSentence[101] = { 0 };
                int bestMetric = -1;

                for (size_t i = 0; i < n; i++) {
                    fgets(sentence, sizeof(sentence), stdin);

                    char* ch = sentence;
                    while (*ch) {
                        if (*ch == '\n') {
                            *ch = '\0';
                            break;
                        }
                        ch++;
                    }

                    int metric = 0;
                    ch = sentence;
                    while (*ch) {
                        if (*ch >= '0' && *ch <= '9') {
                            metric++;
                        }
                        ch++;
                    }

                    if (metric <= bestMetric) continue;

                    ch = sentence;
                    char* target = bestSentence;
                    while (*ch) {
                        *target = *ch;
                        ch++;
                        target++;
                    }
                    *target = '\0';
                    bestMetric = metric;
                }

                printf("%d: %s\n", bestMetric, bestSentence);
                return 0;
            }
        ''') == Result.Ok()
        
    def test_metric_uppercase_count_max(self):
        """Тест метрики: количество заглавных букв"""
        self.question.metricBase = 'uppercase_count'
        self.question.metricDirection = 'max'
        assert self.question.test(r'''
            #include <stdio.h>

            int main() {
                size_t n;
                scanf("%zu\n", &n);

                char sentence[101] = { 0 };
                char bestSentence[101] = { 0 };
                int bestMetric = -1;

                for (size_t i = 0; i < n; i++) {
                    fgets(sentence, sizeof(sentence), stdin);

                    char* ch = sentence;
                    while (*ch) {
                        if (*ch == '\n') {
                            *ch = '\0';
                            break;
                        }
                        ch++;
                    }

                    int metric = 0;
                    ch = sentence;
                    while (*ch) {
                        if (*ch >= 'A' && *ch <= 'Z') {
                            metric++;
                        }
                        ch++;
                    }

                    if (metric <= bestMetric) continue;

                    ch = sentence;
                    char* target = bestSentence;
                    while (*ch) {
                        *target = *ch;
                        ch++;
                        target++;
                    }
                    *target = '\0';
                    bestMetric = metric;
                }

                printf("%d: %s\n", bestMetric, bestSentence);
                return 0;
            }
        ''') == Result.Ok()

    def test_metric_space_count_max(self):
        """Тест метрики: количество пробелов"""
        self.question.metricBase = 'space_count'
        self.question.metricDirection = 'max'
        assert self.question.test(r'''
            #include <stdio.h>

            int main() {
                size_t n;
                scanf("%zu\n", &n);

                char sentence[101] = { 0 };
                char bestSentence[101] = { 0 };
                int bestMetric = -1;

                for (size_t i = 0; i < n; i++) {
                    fgets(sentence, sizeof(sentence), stdin);

                    char* ch = sentence;
                    while (*ch) {
                        if (*ch == '\n') {
                            *ch = '\0';
                            break;
                        }
                        ch++;
                    }

                    int metric = 0;
                    ch = sentence;
                    while (*ch) {
                        if (*ch == ' ') {
                            metric++;
                        }
                        ch++;
                    }

                    if (metric <= bestMetric) continue;

                    ch = sentence;
                    char* target = bestSentence;
                    while (*ch) {
                        *target = *ch;
                        ch++;
                        target++;
                    }
                    *target = '\0';
                    bestMetric = metric;
                }

                printf("%d: %s\n", bestMetric, bestSentence);
                return 0;
            }
        ''') == Result.Ok()

    def test_metric_special_chars_max(self):
        """Тест метрики: количество спецсимволов"""
        self.question.metricBase = 'special_chars'
        self.question.metricDirection = 'max'
        assert self.question.test(r'''
            #include <stdio.h>

            int isSpecialChar(char c) {
                if (c == ' ' || c == '\n' || c == '\r') return 0;
                if (c >= 'a' && c <= 'z') return 0;
                if (c >= 'A' && c <= 'Z') return 0;
                if (c >= '0' && c <= '9') return 0;
                return 1;
            }

            int main() {
                size_t n;
                scanf("%zu\n", &n);

                char sentence[101] = { 0 };
                char bestSentence[101] = { 0 };
                int bestMetric = -1;

                for (size_t i = 0; i < n; i++) {
                    fgets(sentence, sizeof(sentence), stdin);

                    char* ch = sentence;
                    while (*ch) {
                        if (*ch == '\n') {
                            *ch = '\0';
                            break;
                        }
                        ch++;
                    }

                    int metric = 0;
                    ch = sentence;
                    while (*ch) {
                        if (isSpecialChar(*ch)) {
                            metric++;
                        }
                        ch++;
                    }

                    if (metric <= bestMetric) continue;

                    ch = sentence;
                    char* target = bestSentence;
                    while (*ch) {
                        *target = *ch;
                        ch++;
                        target++;
                    }
                    *target = '\0';
                    bestMetric = metric;
                }

                printf("%d: %s\n", bestMetric, bestSentence);
                return 0;
            }
        ''') == Result.Ok()

    def test_metric_consonant_count_max(self):
        """Тест метрики: количество согласных"""
        self.question.metricBase = 'consonant_count'
        self.question.metricDirection = 'max'
        assert self.question.test(r'''
            #include <stdio.h>

            int isVowel(char c) {
                if (c >= 'A' && c <= 'Z') c = c + 32;
                return c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u';
            }

            int isConsonant(char c) {
                if (c >= 'a' && c <= 'z') return !isVowel(c);
                if (c >= 'A' && c <= 'Z') return !isVowel(c);
                return 0;
            }

            int main() {
                size_t n;
                scanf("%zu\n", &n);

                char sentence[101] = { 0 };
                char bestSentence[101] = { 0 };
                int bestMetric = -1;

                for (size_t i = 0; i < n; i++) {
                    fgets(sentence, sizeof(sentence), stdin);

                    char* ch = sentence;
                    while (*ch) {
                        if (*ch == '\n') {
                            *ch = '\0';
                            break;
                        }
                        ch++;
                    }

                    int metric = 0;
                    ch = sentence;
                    while (*ch) {
                        if (isConsonant(*ch)) {
                            metric++;
                        }
                        ch++;
                    }

                    if (metric <= bestMetric) continue;

                    ch = sentence;
                    char* target = bestSentence;
                    while (*ch) {
                        *target = *ch;
                        ch++;
                        target++;
                    }
                    *target = '\0';
                    bestMetric = metric;
                }

                printf("%d: %s\n", bestMetric, bestSentence);
                return 0;
            }
        ''') == Result.Ok()

    def test_metric_punctuation_count_max(self):
        """Тест метрики: количество знаков препинания"""
        self.question.metricBase = 'punctuation_count'
        self.question.metricDirection = 'max'
        assert self.question.test(r'''
            #include <stdio.h>

            int isPunctuation(char c) {
                return c == '.' || c == ',' || c == ';' || c == ':' || 
                       c == '!' || c == '?' || c == '-' || c == '(' || 
                       c == ')' || c == '[' || c == ']' || c == '{' || 
                       c == '}' || c == '"' || c == '\'';
            }

            int main() {
                size_t n;
                scanf("%zu\n", &n);

                char sentence[101] = { 0 };
                char bestSentence[101] = { 0 };
                int bestMetric = -1;

                for (size_t i = 0; i < n; i++) {
                    fgets(sentence, sizeof(sentence), stdin);

                    char* ch = sentence;
                    while (*ch) {
                        if (*ch == '\n') {
                            *ch = '\0';
                            break;
                        }
                        ch++;
                    }

                    int metric = 0;
                    ch = sentence;
                    while (*ch) {
                        if (isPunctuation(*ch)) {
                            metric++;
                        }
                        ch++;
                    }

                    if (metric <= bestMetric) continue;

                    ch = sentence;
                    char* target = bestSentence;
                    while (*ch) {
                        *target = *ch;
                        ch++;
                        target++;
                    }
                    *target = '\0';
                    bestMetric = metric;
                }

                printf("%d: %s\n", bestMetric, bestSentence);
                return 0;
            }
        ''') == Result.Ok()

    def test_metric_longest_word_max(self):
        """Тест метрики: длина самого длинного слова"""
        self.question.metricBase = 'longest_word'
        self.question.metricDirection = 'max'
        assert self.question.test(r'''
            #include <stdio.h>

            int main() {
                size_t n;
                scanf("%zu\n", &n);

                char sentence[101] = { 0 };
                char bestSentence[101] = { 0 };
                int bestMetric = -1;

                for (size_t i = 0; i < n; i++) {
                    fgets(sentence, sizeof(sentence), stdin);

                    char* ch = sentence;
                    while (*ch) {
                        if (*ch == '\n') {
                            *ch = '\0';
                            break;
                        }
                        ch++;
                    }

                    int metric = 0;
                    int currentLen = 0;
                    ch = sentence;
                    while (*ch) {
                        if (*ch != ' ' && *ch != '.' && *ch != ',' && 
                            *ch != '!' && *ch != '?') {
                            currentLen++;
                            if (currentLen > metric) {
                                metric = currentLen;
                            }
                        } else {
                            currentLen = 0;
                        }
                        ch++;
                    }

                    if (metric <= bestMetric) continue;

                    ch = sentence;
                    char* target = bestSentence;
                    while (*ch) {
                        *target = *ch;
                        ch++;
                        target++;
                    }
                    *target = '\0';
                    bestMetric = metric;
                }

                printf("%d: %s\n", bestMetric, bestSentence);
                return 0;
            }
        ''') == Result.Ok()
