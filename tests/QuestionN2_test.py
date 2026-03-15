import pytest
from prog_questions import QuestionN2, Result, utility
from utility import moodleInit


OPERATIONS = [
    "remove_digits",
    "remove_upper",
    "remove_lower",
    "keep_digits",
    "to_upper",
    "to_lower",
    "replace_digits_star",
    "remove_non_alpha",
    "remove_non_alnum",
    "replace_vowels_dash",
    "double_letters",
    "reverse",
    "remove_vowels",
    "remove_consonants",
    "replace_spaces_underscore",
    "count_digits",
    "count_upper",
    "count_lower",
    "sort_chars",
    "unique_chars",
    "caesar_cipher"
]


@pytest.fixture
def question():
    return moodleInit(QuestionN2, seed=123, maxInputSize=100)


def test_code_preload(question):
    utility.CProgramRunner(question.preloadedCode)


@pytest.mark.parametrize("operation", OPERATIONS)
def test_question_text(operation):
    q = moodleInit(QuestionN2, seed=123, maxInputSize=100)
    q.operation = operation

    assert len(q.questionText) > 0


@pytest.mark.parametrize("operation", OPERATIONS)
def test_correct_solution(operation):

    q = moodleInit(QuestionN2, seed=123, maxInputSize=100)
    q.operation = operation

    correct_solution = r'''
        #include <stdio.h>

        int main() {
            char s[101];
            fgets(s, sizeof(s), stdin);
            printf("%s", s);
            return 0;
        }
    '''

    result = q.test(correct_solution)

    assert result != None


def test_compile_error(question):
    with pytest.raises(utility.CompilationError):
        question.test("int main( { return 0; }")


def test_runtime_error(question):

    result = question.test(r'''
        #include <stdio.h>

        int main() {
            char *p = NULL;
            *p = 'a';
            return 0;
        }
    ''')

    assert result != Result.Ok()