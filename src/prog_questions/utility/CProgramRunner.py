import subprocess
import os
import tempfile
import shutil
import sys

class CompilationError(Exception):
    """Ошибка компиляции C-кода"""
    pass


class ExecutionError(Exception):
    """Ошибка выполнения скомпилированной программы"""

    def __init__(self, message: str, exit_code: int):
        super().__init__(message)
        self.exit_code = exit_code


class EnvironmentError(Exception):
    """Ошибка окружения (файловая система, ресурсы и т.п.)"""
    pass


class InternalError(Exception):
    """Внутренняя непредвиденная ошибка в работе CProgramRunner"""
    pass


class ExitCodeHandler:
    """Обработчик кодов завершения и сигналов"""

    def __init__(self):
        self.signal_names = {
            2: "SIGINT (Interrupt)",
            3: "SIGQUIT (Quit)",
            4: "SIGILL (Illegal Instruction)",
            5: "SIGTRAP (Trap)",
            6: "SIGABRT (Abort)",
            7: "SIGBUS (Bus Error)",
            8: "SIGFPE (Floating Point Exception)",
            9: "SIGKILL (Kill)",
            10: "SIGUSR1 (User Signal 1)",
            11: "SIGSEGV (Segmentation Violation)",
            12: "SIGUSR2 (User Signal 2)",
            13: "SIGPIPE (Broken Pipe)",
            14: "SIGALRM (Alarm)",
            15: "SIGTERM (Termination)",
            24: "SIGXCPU (CPU Time Limit Exceeded)",
            25: "SIGXFSZ (File Size Limit Exceeded)"
        }

        self.exit_codes = {
            0: "Успешное завершение",
            1: "Общая ошибка",
            126: "Команда не может быть выполнена",
            127: "Команда не найдена",
            255: "Код завершения вне допустимого диапазона"
        }

    def get_exit_message(self, exit_code) -> str:
        """Преобразование кода завершения в текстовое сообщение"""
        if exit_code < 0 or 128 <= exit_code < 160:
            signal_number = exit_code if exit_code > 0 else -exit_code
            signal_name = self.signal_names.get(signal_number, f"[{signal_number}]")
            return f"Программа завершена сигналом {signal_name}"
        else:
            return self.exit_codes.get(exit_code, f"Неизвестный код завершения {exit_code}")


class CProgramRunner:
    """Класс для компиляции и выполнения C-кода"""

    def __init__(self, c_code: str, use_chroot: bool = False):
        """
        Инициализация с компиляцией переданного C-кода
        :param c_code: Исходный код на C в виде строки
        :param use_chroot: Флаг использования изоляции через chroot
        """
        self.c_code = c_code
        self.use_chroot = use_chroot
        self.exit_code_handler = ExitCodeHandler()
        self.chroot_dir = None

        try:
            self.tmp_dir = tempfile.TemporaryDirectory(dir='.')

            if self.use_chroot:
                self.chroot_dir = os.path.join(self.tmp_dir.name, 'chroot_env')
                os.makedirs(self.chroot_dir, exist_ok=True)
             
        except Exception as e:
            raise EnvironmentError(f"Не удалось создать временную директорию: {e}")

        try:
            self.executable_path = self._compile()

            if self.use_chroot and self.chroot_dir:
                self._prepare_chroot_env()
        except CompilationError:
            raise
        except InternalError:
            raise

    def _compile(self) -> str:
        """Компиляция кода в исполняемый файл, возвращает путь к исполняемому файлу"""
        try:
            src_path = os.path.join(self.tmp_dir.name, 'program.c')
            with open(src_path, 'w', encoding='utf-8') as f:
                f.write(self.c_code)

            exec_path = os.path.join(self.tmp_dir.name, 'program')
            compile_result = subprocess.run(
                ['gcc', src_path, '-o', exec_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            if compile_result.returncode != 0:
                error_msg = compile_result.stderr.decode('utf-8', errors='replace')
                raise CompilationError(error_msg)

            os.chmod(exec_path, 0o755)
            return exec_path

        except CompilationError:
            raise
        except Exception as e:
            raise InternalError(f"Внутренняя ошибка при компиляции: {e}")

    def _get_dependencies(self, binary_path: str) -> list:
        """Получает список зависимых библиотек через ldd"""
        try:
            result = subprocess.run(['ldd', binary_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                return []
            
            libs = []
            for line in result.stdout.splitlines():
                if '=>' in line:
                    parts = line.strip().split('=>')
                    if len(parts) == 2:
                        lib_path = parts[1].strip().split('(')[0].strip()
                        if os.path.exists(lib_path):
                            libs.append(lib_path)
                elif '/ld-linux' in line:
                    lib_path = line.strip().split('(')[0].strip()
                    if os.path.exists(lib_path):
                        libs.append(lib_path)
            return libs
        except Exception:
            return []

    def _prepare_chroot_env(self):
        """Подготовка минимального окружения для chroot"""
        if not self.chroot_dir:
            return

        bin_name = os.path.basename(self.executable_path)
        chroot_bin_path = os.path.join(self.chroot_dir, bin_name)
        shutil.copy2(self.executable_path, chroot_bin_path)
        libs = self._get_dependencies(self.executable_path)
        
        for lib_path in libs:
            lib_dir = os.path.dirname(lib_path)
            target_dir = os.path.join(self.chroot_dir, lib_dir.lstrip('/'))
            os.makedirs(target_dir, exist_ok=True)
            
            target_lib = os.path.join(target_dir, os.path.basename(lib_path))
            if not os.path.exists(target_lib):
                shutil.copy2(lib_path, target_lib)
        
        ld_paths = ['/lib64/ld-linux-x86-64.so.2', '/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2']
        for ld_path in ld_paths:
            if os.path.exists(ld_path):
                target_ld_dir = os.path.join(self.chroot_dir, os.path.dirname(ld_path).lstrip('/'))
                os.makedirs(target_ld_dir, exist_ok=True)
                target_ld = os.path.join(target_ld_dir, os.path.basename(ld_path))
                if not os.path.exists(target_ld):
                    shutil.copy2(ld_path, target_ld)

    def run(self, input_data: str = "", timeout: int = 3) -> str:
        """
        Запуск скомпилированной программы
        :param input_data: Входные данные для программы
        :param timeout: Максимальное время выполнения программы в секундах
        :return: Вывод программы
        """
        if not self.executable_path or not os.path.isfile(self.executable_path):
            raise EnvironmentError("Исполняемый файл не скомпилирован или отсутствует")

        try:
            cmd = []
            cwd = None
            
            if self.use_chroot and self.chroot_dir:
                bin_name = os.path.basename(self.executable_path)
                cmd = ['chroot', '--userspec=1000:1000', self.chroot_dir, f'./{bin_name}']
                cwd = None 
            else:
                # Обычный запуск
                cmd = [self.executable_path]
                cwd = None

            run_result = subprocess.run(
                cmd,
                input=input_data.encode('utf-8'),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                cwd=cwd
            )

            exit_message = self.exit_code_handler.get_exit_message(run_result.returncode)
            if run_result.returncode != 0:
                raise ExecutionError(exit_message, run_result.returncode)

            try:
                output = run_result.stdout.decode('utf-8')
            except UnicodeDecodeError as e:
                raise ExecutionError(f"Ошибка декодирования вывода ({e})", run_result.returncode)

            return output.strip()

        except subprocess.TimeoutExpired:
            raise ExecutionError(f"Превышено время выполнения ({timeout} с)", 1)
        except ExecutionError:
            raise
        except Exception as e:
            raise InternalError(f"Внутренняя ошибка при выполнении программы: {e}")

    def __del__(self):
        """Очистка временных файлов при удалении объекта"""
        try:
            if hasattr(self, 'tmp_dir') and self.tmp_dir:
                self.tmp_dir.cleanup()
        except Exception:
            pass
