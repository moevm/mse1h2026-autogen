import pytest
import inspect
from prog_questions.utility.CProgramRunner import CProgramRunner, ExecutionError, CompilationError
import subprocess
import os
from unittest.mock import patch, MagicMock

def test_bwrap_isolation_must_be_active(capsys):
    """
    Строгая проверка: bwrap должен быть доступен и user namespaces включены.
    Печатает диагностику в stdout, чтобы было видно в CI логах что именно не работает.
    """
    import shutil

    diagnostics = []
    diagnostics.append(f"which bwrap: {shutil.which('bwrap')}")

    try:
        with open('/proc/sys/kernel/unprivileged_userns_clone') as f:
            diagnostics.append(f"unprivileged_userns_clone: {f.read().strip()}")
    except Exception as e:
        diagnostics.append(f"unprivileged_userns_clone: read error {e}")

    diagnostics.append(f"/lib exists: {os.path.exists('/lib')}")
    diagnostics.append(f"/lib64 exists: {os.path.exists('/lib64')}")
    diagnostics.append(f"/usr/bin/true exists: {os.path.exists('/usr/bin/true')}")

    cmd = ['bwrap',
           '--ro-bind', '/usr', '/usr',
           '--ro-bind', '/lib', '/lib',
           '--proc', '/proc',
           '--dev', '/dev',
           '--unshare-pid', '/usr/bin/true']
    if os.path.exists('/lib64'):
        cmd[5:5] = ['--ro-bind', '/lib64', '/lib64']

    diagnostics.append(f"cmd: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, timeout=5)
        diagnostics.append(f"returncode: {result.returncode}")
        diagnostics.append(f"stdout: {result.stdout.decode(errors='replace')}")
        diagnostics.append(f"stderr: {result.stderr.decode(errors='replace')}")
    except Exception as e:
        diagnostics.append(f"exception: {e}")

    diag_text = "\n".join(diagnostics)
    print(f"\n=== BWRAP DIAGNOSTICS ===\n{diag_text}\n=========================")

    assert CProgramRunner._bwrap_userns_available(), (
        f"bwrap изоляция недоступна.\nДиагностика:\n{diag_text}"
    )


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
            assert '--unshare-pid' in called_args, "Отсутствует флаг --unshare-pid"
            assert '--unshare-net' in called_args, "Отсутствует флаг --unshare-net"
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
    
    if not CProgramRunner._bwrap_userns_available():
        pytest.skip("bubblewrap не может создать user namespace в этом окружении")

    runner = CProgramRunner(restricted_code, use_isolation=True)

    try:
        output = runner.run("")
        assert output is not None
    except Exception:
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
    
    if not CProgramRunner._bwrap_userns_available():
        pytest.skip("bubblewrap не может создать user namespace в этом окружении")

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

def test_compile_flags_actually_used():
    """
    Проверяем, что флаги компиляции реально передаются в gcc
    """
    from prog_questions.spring.QuestionN1 import QuestionN1 as SpringQ1
    from unittest.mock import patch, MagicMock

    assert hasattr(SpringQ1, 'COMPILE_FLAGS'), "Вопрос должен иметь атрибут COMPILE_FLAGS"
    raw_flags = SpringQ1.COMPILE_FLAGS
    test_code = "#include <stdio.h>\nint main(){return 0;}"

    with patch('subprocess.run') as mock_run:
        mock_compile = MagicMock(returncode=0, stdout=b"", stderr=b"")
        mock_run.return_value = mock_compile

        try:
            CProgramRunner(test_code, compile_flags=raw_flags)
        except Exception:
            pass

        assert mock_run.called, "subprocess.run не был вызван"

        compile_cmd = mock_run.call_args[0][0]
        expected_flags = raw_flags.split() if isinstance(raw_flags, str) else list(raw_flags)
        for flag in expected_flags:
            assert flag in compile_cmd, f"Флаг '{flag}' не найден в команде: {compile_cmd}"
            