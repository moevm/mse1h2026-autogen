import pytest
from prog_questions.utility.generators.RandomConditionLoop import (
    ELSE_NUMBER_RANGE,
    LOGICAL_OPERATORS,
    MATH_OPERATORS,
    THEN_NUMBER_RANGE,
    THRESHOLD_RANGE,
    Task,
)

class RandomConditionLoop:
    def test_task_is_deterministic_for_same_seed():
        #одинаковый seed дает одинаковый результат
        task1 = Task(array_length=5, condition_length=3, seed=123)
        task2 = Task(array_length=5, condition_length=3, seed=123)

        assert task1.text == task2.text
        assert task1.code == task2.code
        assert task1.threshold == task2.threshold
        assert task1.then_number == task2.then_number
        assert task1.else_number == task2.else_number

    def test_task_is_different_for_different_seed():
        #разный seed дает разный результат
        task1 = Task(array_length=5, condition_length=3, seed=123)
        task2 = Task(array_length=5, condition_length=3, seed=124)

        assert task1.text != task2.text
        assert task1.code != task2.code
        assert task1.threshold != task2.threshold
        assert task1.then_number != task2.then_number
        assert task1.else_number != task2.else_number

    def test_task_values_are_in_expected_ranges():
        #тест, что значения находятся в допустимом диапазоне
        task = Task(array_length=10, condition_length=4, seed=42)

        assert THRESHOLD_RANGE[0] <= task.threshold <= THRESHOLD_RANGE[1]
        assert THEN_NUMBER_RANGE[0] <= task.then_number <= THEN_NUMBER_RANGE[1]
        assert ELSE_NUMBER_RANGE[0] <= task.else_number <= ELSE_NUMBER_RANGE[1]

    def test_generated_text_contains_known_operators():
        #тест, что текст содержит допустимые операторы
        task = Task(array_length=5, condition_length=2, seed=1)

        assert any(op in task.text for op in LOGICAL_OPERATORS)
        assert any(op in task.text for op in MATH_OPERATORS)

    def test_generated_code_contains_if_and_else():
        #тест, что код содержит необходимые строчки
        task = Task(array_length=5, condition_length=3, seed=99)

        assert "if" in task.code
        assert "else" in task.code
        assert "arr[i]" in task.code
        assert "prev" in task.code

    def test_text_contains_required_sections():
        #тест, что текст содержит необходимые строчки
        task = Task(array_length=5, condition_length=3, seed=5)

        assert "ЕСЛИ" in task.text
        assert "ТО" in task.text
        assert "ИНАЧЕ" in task.text

    def test_array_length_one():
        #тест, что содрежит текст, когда длина массива равна 1
        task = Task(array_length=1, condition_length=1, seed=1)

        assert "arr[0]" in task.text