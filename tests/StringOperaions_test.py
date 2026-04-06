from prog_questions.utility.StringOperations import (
    generate_operations,
    generate_input_string,
    apply_operations,
    generate_text,
    DigitModuloStringOperation,
    CaseStringOperation,
    UnderscoreStringOperation,
    ReplaceSubstringStringOperation,
)


class TestStringOperations:
    def test_generate_operations_count(self):
        # Проверка того, что generate_operations создает ровно num_operations операций
        ops = generate_operations(seed=42, num_operations=3)
        assert len(ops) == 3


    def test_generate_operations_deterministic(self):
        # Проверка воспроизводимости
        ops1 = generate_operations(seed=10, num_operations=2)
        ops2 = generate_operations(seed=10, num_operations=2)
        texts1 = [op.get_text() for op in ops1]
        texts2 = [op.get_text() for op in ops2]
        assert texts1 == texts2


    def test_apply_operations_order(self):
        # Проверка того, что операции применяются последовательно в заданном порядке
        op1 = DigitModuloStringOperation()
        op1.divisor = 5
        op2 = ReplaceSubstringStringOperation()
        op2.old = "A"
        op2.new = "B"
        result = apply_operations("AA7", [op1, op2])
        assert result == "BB2"


    def test_generate_text_format(self):
        # Проверка того, что generate_text правильно нумерует операции
        ops = generate_operations(seed=1, num_operations=2)
        text = generate_text(ops)
        assert "1." in text
        assert "2." in text


    def test_generate_input_string_length(self):
        # Проверка того, что сгенерированная строка не превышает max_length
        ops = generate_operations(seed=5, num_operations=2)
        s = generate_input_string(ops, min_length=10, max_length=20)
        assert len(s) <= 20


    def test_digit_modulo_operation(self):
        # Проверка корректной замены цифр
        op = DigitModuloStringOperation()
        op.divisor = 3
        result = op.apply("a5b8c1")
        assert result == "a2b2c1"


    def test_case_string_operation_vowels_upper(self):
        # Проверка корректного перевода гласных в верхний регистр
        op = CaseStringOperation()
        op.is_upper = True
        op.is_vowel = True
        result = op.apply("hello")
        print(result)
        assert result == "hEllO"


    def test_case_string_operation_consonants_lower(self):
        # Проверка корректного перевода согласных в нижний регистр
        op = CaseStringOperation()
        op.is_upper = False
        op.is_vowel = False
        result = op.apply("HELLO")
        assert result == "hEllO"


    def test_underscore_operation(self):
        # Проверка корректной замены пробелов количеством символов '_'
        op = UnderscoreStringOperation()
        op.threshold = 5
        op.divisor = 10
        s = "___ A___"
        result = op.apply(s)
        assert result == "___6A___"


    def test_replace_substring_operation(self):
        # Проверка корректной замены подстроки
        op = ReplaceSubstringStringOperation()
        op.old = "AA"
        op.new = "BB"
        result = op.apply("AAAABB")
        assert result == "BBBBBB"
