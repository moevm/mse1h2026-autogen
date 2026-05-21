import importlib
import inspect
import os
import random
import re
import signal
import sys
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src" / "prog_questions"
SPRING_DIR = SRC_DIR / "spring"
TEST_TIMEOUT_SECONDS = 3

PLACEHOLDER_C_CODE_SNIPPET = """
#include <stdio.h>
int main() {
    return 0;
}
"""

PLACEHOLDER_CPP_CODE_SNIPPET = """
#include <iostream>
using namespace std;
int main() {
    return 0;
}
"""

PLACEHOLDER_REGEX = "[0-9]+"

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Test execution timed out")


def find_question_classes():
    classes = []
    modules_to_check = [
        "prog_questions.QuestionN1",
        "prog_questions.QuestionN2",
        "prog_questions.QuestionN3",
        "prog_questions.QuestionN4",
        "prog_questions.QuestionN5",
        "prog_questions.spring.QuestionN1",
        "prog_questions.spring.QuestionN2",
        "prog_questions.spring.QuestionN3",
        "prog_questions.spring.QuestionN4",
        "prog_questions.spring.QuestionN5",
    ]

    for module_name in modules_to_check:
        try:
            module = importlib.import_module(module_name)
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if re.match(r"QuestionN\d+", name):
                    if hasattr(obj, 'questionName'):
                        classes.append(obj)
        except ImportError:
            pass
    return classes


ALL_QUESTION_CLASSES = find_question_classes()

@pytest.mark.parametrize("question_class", ALL_QUESTION_CLASSES)
def test_question_functionality_and_style(question_class):
    """Tests functionality, style, and temp file location with RANDOM seed."""
    
    q_name = question_class.__name__
    is_spring = 'spring' in str(question_class.__module__)
    
    current_seed = random.randint(1, 1000000)
    instance = question_class(seed=current_seed)


    if q_name == 'QuestionN1' and is_spring:
        placeholder_code = PLACEHOLDER_REGEX
    elif q_name in ['QuestionN1', 'QuestionN3'] and not is_spring:
        placeholder_code = PLACEHOLDER_C_CODE_SNIPPET
    elif q_name == 'QuestionN4' and not is_spring:
        placeholder_code = PLACEHOLDER_CPP_CODE_SNIPPET
    elif q_name in ['QuestionN2', 'QuestionN5'] and not is_spring:
        placeholder_code = PLACEHOLDER_C_CODE_SNIPPET
    elif q_name in ['QuestionN2', 'QuestionN5'] and is_spring:
        placeholder_code = PLACEHOLDER_C_CODE_SNIPPET
    elif q_name in ['QuestionN3', 'QuestionN4'] and is_spring:
        placeholder_code = PLACEHOLDER_CPP_CODE_SNIPPET
    else:
        placeholder_code = PLACEHOLDER_C_CODE_SNIPPET

    initial_files = set(Path(".").iterdir())

    assert hasattr(instance, 'test'), f"Question class {q_name} does not have a 'test' method."

    original_temp_dir = tempfile.gettempdir()
    tempfile.tempdir = os.getcwd() 

    try:
        if os.name == 'posix': 
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(TEST_TIMEOUT_SECONDS)
            try:
                result = instance.test(placeholder_code)
            finally:
                signal.alarm(0) 
                signal.signal(signal.SIGALRM, old_handler) 
        else: 
            result = instance.test(placeholder_code)

    except Exception as e:
        if is_spring and q_name == 'QuestionN1' and ('regcomp' in str(e) or 'regexec' in str(e)):
            pytest.skip(f"Spring Q1 requires regex library which is missing on this Windows environment (Seed: {current_seed}): {e}")
        else:
            pytest.fail(f"Question {q_name} (Seed: {current_seed}) raised an exception: {e}")

    finally:
        tempfile.tempdir = original_temp_dir

    html_content = instance.questionText
    assert html_content is not None, f"questionText for {q_name} (Seed: {current_seed}) is None"

    example_table_found = bool(re.search(r'<table[^>]*class=["\']coderunnerexamples\s*["\']', html_content))
    example_header_found = bool(re.search(r'<\s*b\s*>.*?Пример.*?<\s*/\s*b\s*>', html_content, re.IGNORECASE | re.DOTALL))
    
    assert example_table_found or example_header_found, f"Example table/header not found in questionText for {q_name} (Seed: {current_seed})"

    final_files = set(Path(".").iterdir())
    new_files = final_files - initial_files
    suspicious_new_files = [f for f in new_files if f.parent == Path(".") and f.name not in ['.pytest_cache', 'pytest.ini']] 
    assert not suspicious_new_files, f"Unexpected files created in project root during test of {q_name} (Seed: {current_seed}): {suspicious_new_files}"
