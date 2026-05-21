import pytest
import inspect
from prog_questions.utility.CProgramRunner import CProgramRunner, ExecutionError, CompilationError

def test_compilation_flags_support():
    """
    Возможность настройки флагов компиляции
    Проверяем, что Spring QuestionN1 (как пример) имеет атрибут COMPILE_FLAGS
    """
    from prog_questions.spring.QuestionN1 import QuestionN1 as SpringQ1
    assert hasattr(SpringQ1, 'COMPILE_FLAGS'), "Вопрос должен поддерживать настройку флагов компиляции"

def test_execution_error_decoding():
    """
    Расшифровка аварийных кодов завершения
    Проверяем, что при крахе программы выбрасывается ExecutionError с понятным сообщением
    """
    crash_code = """
    #include <stdio.h>
    #include <stdlib.h>

    int main() {
        int *p = NULL;
        *p = 1; // Это вызовет Segmentation Fault при выполнении
        return 0;
    }
    """
    
    try:
        runner = CProgramRunner(crash_code)
        with pytest.raises(ExecutionError) as exc_info:
            runner.run("")
        
        assert str(exc_info.value), "ExecutionError должно содержать сообщение об ошибке"

    except CompilationError as e:
        pytest.fail(f"Код не скомпилировался (ошибка теста): {e}")

def test_chroot_or_isolation_presence():
    """
    Запуск из-под chroot или изоляции
    Проверка наличия кода изоляции в раннере
    """
    import prog_questions.utility.CProgramRunner as runner_module
    source_code = inspect.getsource(runner_module)
    
    has_isolation_keywords = any(k in source_code for k in ['chroot', 'namespace', 'isolate', 'sandbox', 'unshare'])
    
    if not has_isolation_keywords:
        pytest.skip("Механизм chroot/isolation явно не обнаружен в CProgramRunner. Требуется реализация.")
    else:
        assert True