import random 

def is_brackets_balanced(text: str, brackets: str = "()") -> bool: 
    # Проверка, сбалансированы ли скобки в строке 
    opening, closing = brackets[::2], brackets[1::2]
    stack = []
    for character in text: 
        if character in opening:
            stack.append(opening.index(character))
        elif character in closing:
            if stack and stack[-1] == closing.index(character):
                stack.pop() 
            else: 
                return False 
    return len(stack) == 0

def get_bracket(rng: random.Random, brackets_threshold: float, is_open: bool = True) -> str: 
    # С заданной вероятностью возвращается скобка 
    if is_open: 
        return "(" if rng.random() < brackets_threshold else ""
    return ")" if rng.random() < brackets_threshold else ""

def get_var(
    rng: random.Random, cur_vars: list, vars: list, 
    minus_symbol: str, minuses_threshold: float, all_variables: bool
) -> str:
    # Выбирается переменная, при необходимости к ней добавляется унарный минус 
    need_minus = rng.random() < minuses_threshold
    var = rng.choice(cur_vars)

    if all_variables:
        cur_vars.remove(var)
        if len(cur_vars) == 0:
            cur_vars.extend(vars)
    return f"({minus_symbol}{var})" if need_minus else var 

def get_expression(
    vars: list, operations: list, length: int, random_seed: int,
    minuses_threshold: float = 0, brackets_threshold: float = 0,
    minus_symbol: str = "-", all_variables: bool = False
) -> str: 
    # Генерируется случайное математическое выражение
    rng = random.Random(random_seed)
    cur_vars = vars.copy()

    # Совершается максимум 3 попытки генерации выражения
    for _ in range(3):
        expression = ""
        stack = 0 

        bracket = get_bracket(rng, brackets_threshold)
        expression += bracket
        stack += (bracket != "")
        
        expression += get_var(rng, cur_vars, vars, minus_symbol, minuses_threshold, all_variables)

        for i in range(length):
            expression += f" {rng.choice(operations)} "

            if i != length - 1:
                bracket = get_bracket(rng, brackets_threshold)
                expression += bracket
                stack += (bracket != "")

            expression += get_var(rng, cur_vars, vars, minus_symbol, minuses_threshold, all_variables)

            if bracket == "":
                cur_stack = stack 
                for _ in range(cur_stack):
                    bracket = get_bracket(rng, brackets_threshold, is_open=False)
                    expression += bracket
                    stack -= (bracket != "")
            
        if stack > 0:
            expression += ")" * stack

        if is_brackets_balanced(expression):
            return expression

    raise ValueError("Can not generate expression")
