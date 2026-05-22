import pytest
from prog_questions.QuestionBase import Result

def test_result_fail_contains_debug_info():
    """
    Ответ выводится в формате grader.
    Ответ проверки понятен и содержит в себе входные, выходные и ожидаемые данные
    """

    fail_res = Result.Fail(
        input="1 2 3",
        expected="6",
        got="5"
    )
    
    assert hasattr(fail_res, 'input'), "Result.Fail должен иметь поле 'input'"
    assert hasattr(fail_res, 'expected'), "Result.Fail должен иметь поле 'expected'"
    assert hasattr(fail_res, 'got'), "Result.Fail должен иметь поле 'got'"
    assert fail_res.input == "1 2 3", f"Входные данные не совпадают: {fail_res.input}"
    assert fail_res.expected == "6", f"Ожидаемый ответ не совпадает: {fail_res.expected}"
    assert fail_res.got == "5", f"Фактический ответ не совпадает: {fail_res.got}"
    assert isinstance(fail_res, Result.Fail), "Объект должен быть экземпляром Result.Fail"
