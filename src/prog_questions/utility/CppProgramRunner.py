import os
import sys
import subprocess
from .CProgramRunner import CProgramRunner, CompilationError, InternalError

class CppProgramRunner(CProgramRunner):
    """Раннер для компиляции и выполнения C++-кода"""

    def _compile(self) -> str:
        try:
            src_path = os.path.join(self.tmp_dir.name, 'program.cpp')
            with open(src_path, 'w', encoding='utf-8') as f:
                f.write(self.c_code)

            exec_ext = '.exe' if sys.platform == 'win32' else ''
            exec_path = os.path.join(self.tmp_dir.name, f'program{exec_ext}')

            compile_result = subprocess.run(
                ['g++', src_path, '-std=c++17', '-o', exec_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            if compile_result.returncode != 0:
                error_msg = compile_result.stderr.decode('utf-8', errors='replace')
                raise CompilationError(error_msg)

            if not os.path.isfile(exec_path):
                raise InternalError("Компиляция прошла, но файл не создан")

            return exec_path

        except CompilationError:
            raise
        except FileNotFoundError:
            raise CompilationError("g++ не найден")
        except Exception as e:
            raise InternalError(f"Ошибка компиляции: {e}")