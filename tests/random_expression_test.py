import pytest 
from prog_questions.utility.RandomExpression import get_expression, is_brackets_balanced
import re

class TestRandomExpression:
    def test_brackets_balanced_simple(self):
        assert is_brackets_balanced("(a + b)") is True
    
    def test_brackets_balanced_nested(self):
        assert is_brackets_balanced("((a + b) * c)") is True

    def test_brackets_balanced_unclosed(self):
        assert is_brackets_balanced("(a + b") is False 

    def test_brackets_balanced_unopened(self):
        assert is_brackets_balanced("a + b)") is False

    def test_brackets_balanced_wrong_order(self):
        assert is_brackets_balanced(")a+b(") is False
    
    def test_brackets_balanced_empty_string(self):
        assert is_brackets_balanced("") is True 

    def test_get_expression_determinism(self):
        # Одинаковый seed даёт одинаковый результат
        expr1 = get_expression(["x", "y"], ["+"], 3, 42)
        expr2 = get_expression(["x", "y"], ["+"], 3, 42)
        assert expr1 == expr2

    def test_get_expression_different_seeds(self):
        # Разные seed дают разные результаты
        expr1 = get_expression(["x", "y", "z"], ["+", "-"], 5, 42)
        expr2 = get_expression(["x", "y", "z"], ["+", "-"], 5, 43)
        assert expr1 != expr2

    def test_get_expression_operation_count(self):
        # Проверяется, что количество операций совпадает с параметром length 
        length = 5 
        ops = ["+"]
        expr = get_expression(["x"], ops, length, 1)
        assert expr.count("+") == 5

    def test_all_variables_used(self):
        # При all_variables=True в выражении используются все переменные
        vars_list = ["a", "b", "c", "d"]
        expr = get_expression(vars_list, ["+"], 3, 42, all_variables=True)
        for v in vars_list:
            assert v in expr

    def test_get_expression_minuses_threshold_full(self):
        # При minuses_threshold=1.0 все переменные в выражении с минусом
        expr = get_expression(["x", "y"], ["+"], 2, 42, minuses_threshold=1.0)
        vars_in_expr = re.findall(r'\(-[xy]\)', expr)
        assert len(vars_in_expr) == 2 + 1

    def test_get_expression_minuses_threshold_zero(self):
        # При minuses_threshold=0 все переменные в выражении без минуса
        expr = get_expression(["x", "y"], ["+"], 4, 42, minuses_threshold=0)
        assert "(-" not in expr 

    def test_get_expression_brackets_threshold_full(self):
        # При brackets_threshold=1.0 в выражении есть скобки и они сбалансированы
        expr = get_expression(["x", "y"], ["+"], 5, 42, brackets_threshold=1.0)
        assert "(" in expr
        assert ")" in expr
        assert is_brackets_balanced(expr) is True 
    
    def test_get_expression_brackets_threshold_zero(self):
        # При brackets_threshold=0 в выражении нет скобок (кроме унарных минусов)
        expr = get_expression(["x", "y"], ["+"], 4, 42, brackets_threshold=0)
        assert "(" not in expr
        assert ")" not in expr

    def test_get_expression_length_zero(self):
        # При length=0 функция возвращает ровно одну переменную
        expr = get_expression(["x", "y"], ["+"], 0, 42)
        assert expr in ["x", "y"]

    def test_value_err(self, monkeypatch):
        # Если выражение не сгенерировалось за 3 попытки, вызывается исключение 
        monkeypatch.setattr("prog_questions.utility.RandomExpression.is_brackets_balanced", lambda x: False)
        with pytest.raises(ValueError, match="Can not generate expression"):
            get_expression(["x"], ["+"], 2, 42)
