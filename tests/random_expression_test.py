import pytest 
from prog_questions.utility.random_expressions import get_expression, is_brackets_balanced
import re

def test_brackets_balanced():
    assert is_brackets_balanced("(a + b)") is True
    assert is_brackets_balanced("((a + b) * c)") is True
    assert is_brackets_balanced("(a + b") is False 
    assert is_brackets_balanced("a + b)") is False
    assert is_brackets_balanced(")a+b(") is False
    assert is_brackets_balanced("") is True 

def test_get_expression_determinism():
    # Проверяется, что одинаковые seed ведет к одинаковому результату
    expr1 = get_expression(["x", "y"], ["+"], 3, 42)
    expr2 = get_expression(["x", "y"], ["+"], 3, 42)
    assert expr1 == expr2

def test_get_expression_different():
    # Проверяется, что различные seed ведут к разным результатам
    expr1 = get_expression(["x", "y", "z"], ["+", "-"], 5, 42)
    expr2 = get_expression(["x", "y", "z"], ["+", "-"], 5, 43)
    assert expr1 != expr2

def test_get_expression_length():
    # Проверяется, что количество операций совпадает с параметром length 
    length = 5 
    ops = ["+"]
    expr = get_expression(["x"], ops, length, 1)
    assert expr.count("+") == 5

def test_all_variables_used():
    # Проверяется, что при all_variables=True используются все перменные
    vars_list = ["a", "b", "c", "d"]
    expr = get_expression(vars_list, ["+"], 3, 42, all_variables=True)
    for v in vars_list:
        assert v in expr

def test_minuses_threshold():
    # Проверяется, что при minuses_threshold=1.0 все переменные с минусом
    expr = get_expression(["x", "y"], ["+"], 2, 42, minuses_threshold=1.0)
    vars_in_expr = re.findall(r'\(-[xy]\)', expr)
    assert len(vars_in_expr) == 2 + 1

def test_brackets_threshold():
    # Проверяется, что если brackets_threshold > 0 в выражении присутствуют скобки
    expr = get_expression(["x", "y"], ["+"], 5, 42, brackets_threshold=1.0)
    assert "(" in expr
    assert ")" in expr
    assert is_brackets_balanced(expr) is True 

def test_value_err(monkeypatch):
    # Проверяется, что если выражение не сгенерировалось за 3 попытки, вызывается исключение 
    monkeypatch.setattr("prog_questions.utility.random_expressions.is_brackets_balanced", lambda x: False)
    with pytest.raises(ValueError, match="Can not generate expression"):
        get_expression(["x"], ["+"], 2, 42)