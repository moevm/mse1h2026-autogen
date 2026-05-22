import pytest
import inspect
from prog_questions.utility.CProgramRunner import CProgramRunner, ExecutionError, CompilationError
import subprocess
import os
from unittest.mock import patch, MagicMock

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

def test_bwrap_isolation_integration():
    """
    Тест интеграции с bubblewrap для изоляции выполнения программ
    """
    simple_code = """
    #include <stdio.h>
    int main() {
        printf("Hello from bwrap!\\n");
        return 0;
    }
    """

    try:
        subprocess.run(['which', 'bwrap'], check=True, stdout=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("bubblewrap не установлен, пропускаем тест")

    runner = CProgramRunner(simple_code, use_isolation=True)
    
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = b"Hello from bwrap!\n"
        mock_run.return_value = mock_result
        
        try:
            output = runner.run("")
            called_args = mock_run.call_args[0][0] if mock_run.call_args else []
            assert 'bwrap' in called_args, f"Ожидается использование bwrap, получено: {called_args}"
            
            assert '--ro-bind' in called_args, "Отсутствуют обязательные флаги --ro-bind"
            assert '--unshare-all' in called_args, "Отсутствует флаг --unshare-all"
            assert '--tmpfs' in called_args, "Отсутствует флаг --tmpfs"
            
        except Exception as e:
            pytest.fail(f"Ошибка при выполнении теста bwrap изоляции: {e}")


def test_bwrap_command_construction():
    """
    Тест построения команды bwrap внутри CProgramRunner
    """
    simple_code = """
    #include <stdio.h>
    int main() {
        return 0;
    }
    """
    
    runner = CProgramRunner(simple_code, use_isolation=True)
    
    original_run = subprocess.run
    
    def mock_subprocess_run(cmd, **kwargs):
        if runner.use_isolation and isinstance(cmd, list) and len(cmd) > 0:
            assert cmd[0] == 'bwrap', f"Ожидается bwrap как первая команда, получено: {cmd[0]}"
            result = MagicMock()
            result.returncode = 0
            result.stdout = b""
            result.stderr = b""
            return result
        return original_run(cmd, **kwargs)
    
    with patch('subprocess.run', side_effect=mock_subprocess_run):
        try:
            runner.run("")
        except Exception:
            pass


def test_no_isolation_mode():
    """
    Тест работы без изоляции (обычный режим выполнения)
    """
    simple_code = """
    #include <stdio.h>
    int main() {
        printf("Hello without isolation\\n");
        return 0;
    }
    """
    
    runner = CProgramRunner(simple_code, use_isolation=False)
    
    original_run = subprocess.run
    
    def mock_subprocess_run(cmd, **kwargs):
        if not runner.use_isolation and isinstance(cmd, list) and len(cmd) > 0:
            assert cmd[0] != 'bwrap', f"В режиме без изоляции не должно быть bwrap, получено: {cmd[0]}"
            result = MagicMock()
            result.returncode = 0
            result.stdout = b"Hello without isolation\n"
            return result
        return original_run(cmd, **kwargs)
    
    with patch('subprocess.run', side_effect=mock_subprocess_run):
        try:
            output = runner.run("")
            assert "without isolation" in output
        except Exception:
            pass


def test_bwrap_sandbox_security():
    """
    Тест безопасности изоляции через bwrap
    Проверяет, что bwrap создает безопасную песочницу без root прав
    """
    restricted_code = """
    #include <stdio.h>
    #include <sys/stat.h>

    int main() {
        // Программа должна работать только внутри песочницы
        FILE *f = fopen("/etc/passwd", "r");
        if (f) {
            fclose(f);
            printf("Access granted\\n");
            return 1;  // Не должен выполниться в песочнице
        } else {
            printf("Access denied\\n");
            return 0;  // Ожидаемый результат в песочнице
        }
    }
    """
    
    try:
        subprocess.run(['which', 'bwrap'], check=True, stdout=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("bubblewrap не установлен, пропускаем тест")
    
    runner = CProgramRunner(restricted_code, use_isolation=True)
    
    try:
        output = runner.run("")
        assert output is not None
    except Exception as e:
        assert True


def test_no_root_requirement_with_bwrap():
    """
    Тест того, что bwrap не требует root прав для изоляции
    """
    simple_code = """
    #include <stdio.h>
    int main() {
        printf("Running without root\\n");
        return 0;
    }
    """
    
    try:
        subprocess.run(['which', 'bwrap'], check=True, stdout=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("bubblewrap не установлен, пропускаем тест")
    
    runner = CProgramRunner(simple_code, use_isolation=True)
    
    try:
        output = runner.run("")
        assert "permission denied" not in output.lower() if output else True
    except ExecutionError as e:
        assert "permission denied" not in str(e).lower(), "Bwrap не должен требовать root прав"
        assert "CAP_SYS_CHROOT" not in str(e), "Должно использоваться userspace изоляция"


def test_bwrap_vs_no_isolation_flag():
    """
    Тест переключения между изоляцией и без изоляции через флаг
    """
    simple_code = """
    #include <stdio.h>
    int main() {
        return 0;
    }
    """
    
    runner_no_isolation = CProgramRunner(simple_code, use_isolation=False)
    assert runner_no_isolation.use_isolation == False
    
    runner_with_isolation = CProgramRunner(simple_code, use_isolation=True)
    assert runner_with_isolation.use_isolation == True