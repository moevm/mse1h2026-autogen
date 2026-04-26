from prog_questions.spring import QuestionN1, Result
from utility import moodleInit

class BaseTestQuestionN1:

    def test_code_preload(self):
        assert isinstance(self.question.preloadedCode, str)

    def test_code_invalid_regex(self):
        q = QuestionN1(seed=self.invalid_seed)
        q.variant = self.variant
        q.sub_variant = self.sub_variant
        assert q.test(self.invalid_regex) != Result.Ok()

    def test_code_success_run(self):
        q = QuestionN1(seed=self.success_seed)
        q.variant = self.variant
        q.sub_variant = self.sub_variant
        assert q.test(self.correct_regex) == Result.Ok()


class TestQuestionN1HttpMethod(BaseTestQuestionN1):
    question = moodleInit(QuestionN1, seed=101)
    variant = 'http_method'
    sub_variant = 'method'

    invalid_seed = 201
    invalid_regex = r'^\[[[invalid regex'

    success_seed = 201 
    correct_regex = (
        r'^\[[^]]+\][[:space:]]+'
        r'(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS|TRACE|CONNECT)'
        r'[[:space:]]'
    )

    def setup_method(self):
        self.question.variant = 'http_method'
        self.question.sub_variant = 'method'

    # Некорректное решение - выводит всю строку
    def test_code_wrong_answer_prints_all(self):
        q = QuestionN1(seed=203)
        q.variant = 'http_method'
        q.sub_variant = 'method'

        assert q.test(r'^\[[^]]+\][[:space:]]+(.+)') != Result.Ok()

    # Некорректное решение - нет ограничения на методы
    def test_code_wrong_answer_includes_fake_methods(self):
        q = QuestionN1(seed=204)
        q.variant = 'http_method'
        q.sub_variant = 'method'

        assert q.test(r'^\[[^]]+\][[:space:]]+([A-Z]+)[[:space:]]') != Result.Ok()


class TestQuestionN1Email(BaseTestQuestionN1):
    question = moodleInit(QuestionN1, seed=102)

    variant = 'email'
    sub_variant = 'full_email'

    invalid_seed = 211
    invalid_regex = r'[invalid'

    success_seed = 211 
    correct_regex = (
        r'[A-Za-z0-9]([A-Za-z0-9._-]*[A-Za-z0-9])?'
        r'@'
        r'[A-Za-z0-9][A-Za-z0-9.-]*'
        r'\.[A-Za-z]{2,4}'
    )

    def setup_method(self):
        self.question.variant = 'email'
        self.question.sub_variant = 'full_email'

    # Некорректное решение - нет проверки длины зоны
    def test_code_wrong_answer_no_zone_length_check(self):
        q = QuestionN1(seed=213)
        q.variant = 'email'
        q.sub_variant = 'full_email'

        assert q.test(
            r'[A-Za-z0-9][A-Za-z0-9._-]*@[A-Za-z0-9][A-Za-z0-9.-]*\.[A-Za-z]+'
        ) != Result.Ok()

    # Некорректное решение - нет проверки домена
    def test_code_wrong_answer_matches_no_domain(self):
        q = QuestionN1(seed=214)
        q.variant = 'email'
        q.sub_variant = 'full_email'

        assert q.test(r'[A-Za-z0-9._-]+@[A-Za-z]{2,4}') != Result.Ok()

    def test_code_wrong_answer_dot(self):
        q = QuestionN1(seed=215)
        q.variant = 'email'
        q.sub_variant = 'full_email'

        assert q.test(r'[A-Za-z0-9._-]+@[A-Za-z0-9][A-Za-z0-9.-]*\.[A-Za-z]{2, 4}') != Result.Ok()

    # Некорректное решение - имя в email с точкой в конце
    def test_code_wrong_answer_dot_at_end_of_name(self):
        q = QuestionN1(seed=216)
        q.variant = 'email'
        q.sub_variant = 'full_email'
        assert q.test(
            r'[A-Za-z0-9][A-Za-z0-9._-]*'
            r'@'
            r'[A-Za-z0-9][A-Za-z0-9.-]*'
            r'\.[A-Za-z]{2,4}'
        ) != Result.Ok()


class TestQuestionN1DateInFilename(BaseTestQuestionN1):
    question = moodleInit(QuestionN1, seed=103)

    variant = 'date_in_filename'
    sub_variant = 'as_is'

    invalid_seed = 221
    invalid_regex = r'([0-9]{4}-[0-9]{2}-[0-9]{2}'

    success_seed = 221 
    correct_regex = (
        r'[0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{2}-[0-9]{2}-[0-9]{4}'
    )

    def setup_method(self):
        self.question.variant = 'date_in_filename'
        self.question.sub_variant = 'as_is'

    # Некорректное решение - нет поиска даты после префикса
    def test_code_wrong_answer_date_at_start_only(self):
        q = QuestionN1(seed=223)
        q.variant = 'date_in_filename'
        q.sub_variant = 'as_is'

        assert q.test(
            r'^([0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{2}-[0-9]{2}-[0-9]{4})'
        ) != Result.Ok()

    # Некорректное решение - нет всех форматов даты
    def test_code_wrong_answer_only_iso_format(self):
        q = QuestionN1(seed=224)
        q.variant = 'date_in_filename'
        q.sub_variant = 'as_is'

        assert q.test(
            r'(^|[^0-9])([0-9]{4}-[0-9]{2}-[0-9]{2})([^0-9]|$)'
        ) != Result.Ok()


class TestQuestionN1Version(BaseTestQuestionN1):
    question = moodleInit(QuestionN1, seed=104)

    variant = 'version'
    sub_variant = 'full_version'

    invalid_seed = 231
    invalid_regex = r'[0-9]+\.[0-9]+{bad'

    success_seed = 231
    correct_regex = (r'([0-9]+\.[0-9]+(\.[0-9]+)?)')

    def setup_method(self):
        self.question.variant = 'version'
        self.question.sub_variant = 'full_version'

    # Некорректное решение - выводит всю строку
    def test_code_wrong_answer_prints_line(self):
        q = QuestionN1(seed=233)
        q.variant = 'version'
        q.sub_variant = 'full_version'

        assert q.test(r'(^|[^0-9\.])(.+)([^0-9\.]|$)') != Result.Ok()

    # Некорректное решение - нет границ поиска версии
    def test_code_wrong_answer_no_boundary_check(self):
        q = QuestionN1(seed=234)
        q.variant = 'version'
        q.sub_variant = 'full_version'

        assert q.test(r'[0-9]+\.[0-9]+') != Result.Ok()


class TestQuestionN1UrlPath(BaseTestQuestionN1):
    question = moodleInit(QuestionN1, seed=105)

    variant = 'url_path'
    sub_variant = 'path'

    invalid_seed = 241
    invalid_regex = r'^https?://[unclosed'

    success_seed = 241
    correct_regex = (r'^https?://[^/[:space:]]+(/[[:graph:]]*)')

    def setup_method(self):
        self.question.variant = 'url_path'
        self.question.sub_variant = 'path'

    # Некорректное решение - выводит весь URL
    def test_code_wrong_answer_prints_full_url(self):
        q = QuestionN1(seed=243)
        q.variant = 'url_path'
        q.sub_variant = 'path'

        assert q.test(r'^(https?://[^[:space:]]+)') != Result.Ok()

    # Некорректное решение - выводит схему и домен
    def test_code_wrong_answer_outputs_url_without_path(self):
        q = QuestionN1(seed=244)
        q.variant = 'url_path'
        q.sub_variant = 'path'

        assert q.test(r'^(https?://[^/[:space:]]+/[^[:space:]]*)') != Result.Ok()