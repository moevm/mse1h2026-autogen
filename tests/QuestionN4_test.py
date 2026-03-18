from prog_questions import QuestionN4, Result
from utility import moodleInit
import random


class TestQuestionN4:
    question = moodleInit(QuestionN4, seed=123)

    def test_preloaded_code(self):
        # студент вводит ответ, не код
        assert self.question.preloadedCode == ''

    def test_question_text(self):
        # текст задания должен содержать ключевые элементы
        assert 'Размеры массива' in self.question.questionText
        assert 'плоских' in self.question.questionText
        assert 'Вопрос' in self.question.questionText

    def test_correct_answer(self):
        # правильный ответ должен засчитываться
        random.seed(self.question.seed)
        _, expectedOutput = self.question.generateTest()
        assert self.question.test(expectedOutput) == Result.Ok()

    def test_correct_answer_with_extra_spaces(self):
        # лишние пробелы по краям не должны мешать — issue #150
        random.seed(self.question.seed)
        _, expectedOutput = self.question.generateTest()
        assert self.question.test('  ' + expectedOutput + '  ') == Result.Ok()

    def test_wrong_answer(self):
        # неверный ответ не должен засчитываться
        assert self.question.test('9999999\n9999999\n') != Result.Ok()

    def test_convert_index_3d(self):
        # arr[10][20][30], индекс [1][2][3] = 1*20*30 + 2*30 + 3 = 663
        dims = [10, 20, 30]
        assert self.question.convert_index([1, 2, 3], dims) == 663

    def test_convert_index_zero(self):
        # нулевой индекс всегда даёт плоский индекс 0
        dims = [10, 20, 30]
        assert self.question.convert_index([0, 0, 0], dims) == 0
