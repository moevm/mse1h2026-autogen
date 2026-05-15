from ..QuestionBase import QuestionBase, Result
from ..utility import CProgramRunner, ExecutionError, CompilationError
import random
import string
import os
import subprocess
import tempfile


class QuestionN5(QuestionBase):
    questionName = 'Задание 5. Работа с директорией и файловой системой'

    # Возможные типы заданий
    TASK_DELETE_RENAME    = 'delete_rename'
    TASK_READ_HEX         = 'read_hex'
    TASK_OVERWRITE_BYTES  = 'overwrite_bytes'
    TASK_FILE_STATS       = 'file_stats'
    TASK_MERGE_FILES      = 'merge_files'
    TASK_LIST_DIRECTORY   = 'list_directory'
    TASK_COUNT_LINES      = 'count_lines_in_dir'

    TASK_TYPES = [
        TASK_DELETE_RENAME,
        TASK_READ_HEX,
        TASK_OVERWRITE_BYTES,
        TASK_FILE_STATS,
        TASK_MERGE_FILES,
        TASK_LIST_DIRECTORY,
        TASK_COUNT_LINES,
    ]

    # Параметры генерации содержимого файлов
    MIN_FILE_SIZE   = 50
    MAX_FILE_SIZE   = 100
    MIN_LINES       = 3
    MAX_LINES       = 8
    MIN_LINE_LEN    = 5
    MAX_LINE_LEN    = 40

    # Количество проверочных запусков
    FIXED_TESTS_COUNT  = 5
    RANDOM_TESTS_COUNT = 10

    def __init__(self, *, seed, taskType: str = ''):
        super().__init__(seed=seed, taskType=taskType)
        random.seed(self.seed)

        # Если тип задания не задан или не распознан — выбираем случайно
        if taskType in self.TASK_TYPES:
            self.taskType = taskType
        else:
            self.taskType = random.choice(self.TASK_TYPES)

    def _make_random_filename(self, prefix='file', ext='.txt'):
        """
        Генерирует случайное имя файла вида prefix_NNNN.ext.
        """
        number = random.randint(1000, 9999)
        return f"{prefix}_{number}{ext}"

    def _make_random_text(self, length):
        """
        Генерирует случайную строку из букв и цифр заданной длины.
        """
        chars = string.ascii_letters + string.digits
        return ''.join(random.choices(chars, k=length))

    def _make_random_file_content(self, min_lines=None, max_lines=None):
        """
        Генерирует случайный текст из нескольких строк.
        Каждая строка заканчивается символом переноса.
        """
        if min_lines is None:
            min_lines = self.MIN_LINES
        if max_lines is None:
            max_lines = self.MAX_LINES

        lines = []
        num_lines = random.randint(min_lines, max_lines)
        for _ in range(num_lines):
            line_len = random.randint(self.MIN_LINE_LEN, self.MAX_LINE_LEN)
            line = self._make_random_text(line_len)
            lines.append(line)

        # Соединяем строки через \n и добавляем \n в конце
        content = '\n'.join(lines) + '\n'
        return content

    def _run_program_with_files(self, abs_exec_path, stdin_data, initial_files, initial_dirs=None, initial_symlinks=None, timeout=5):
        """
        Запускает скомпилированную программу в изолированной временной директории.

        Перед запуском создаёт все нужные файлы, директории и симлинки.
        После запуска собирает содержимое всех файлов в словарь.

        Возвращает кортеж (stdout_строка, словарь_файлов_после_запуска).
        """
        with tempfile.TemporaryDirectory(dir='.') as work_dir:

            # Создаём директории, если они нужны
            if initial_dirs:
                for dir_path in initial_dirs:
                    full_dir = os.path.join(work_dir, dir_path)
                    os.makedirs(full_dir, exist_ok=True)

            # Создаём файлы с нужным содержимым
            for relative_path, content in initial_files.items():
                full_path = os.path.join(work_dir, relative_path)
                parent_dir = os.path.dirname(full_path)
                if parent_dir:
                    os.makedirs(parent_dir, exist_ok=True)
                if isinstance(content, bytes):
                    with open(full_path, 'wb') as f:
                        f.write(content)
                else:
                    with open(full_path, 'w') as f:
                        f.write(content)

            # Создаём симлинки: ключ — путь к ссылке, значение — цель (относительная)
            if initial_symlinks:
                for link_path, target in initial_symlinks.items():
                    full_link = os.path.join(work_dir, link_path)
                    os.symlink(target, full_link)

            # Запускаем программу
            run_result = subprocess.run(
                [abs_exec_path],
                input=stdin_data.encode('utf-8'),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=work_dir,
                timeout=timeout,
            )

            # Проверяем код возврата
            if run_result.returncode != 0:
                error_text = run_result.stderr.decode('utf-8', errors='replace').strip()
                message = f"Программа завершена с кодом {run_result.returncode}"
                if error_text:
                    message += f": {error_text}"
                raise ExecutionError(message, run_result.returncode)

            stdout_text = run_result.stdout.decode('utf-8').replace('\r\n', '\n').strip()

            # Читаем все файлы, которые остались в рабочей директории
            result_files = {}
            for root, subdirs, filenames in os.walk(work_dir):
                for filename in filenames:
                    full_path = os.path.join(root, filename)
                    relative = os.path.relpath(full_path, work_dir).replace('\\', '/')
                    with open(full_path, 'rb') as f:
                        result_files[relative] = f.read()

            return stdout_text, result_files

    def _generate_delete_rename_test(self):
        """
        Генерирует тест для задания: удалить файл и переименовать другой.

        Входные данные: три имени файлов (удаляемый, старое имя, новое имя).
        Ожидаемый вывод: ok/error для каждой операции.
        """
        to_delete = self._make_random_filename('todel')
        old_name  = self._make_random_filename('old')
        new_name  = self._make_random_filename('new')

        # Генерируем содержимое файлов
        delete_content = self._make_random_text(30).encode()
        old_content    = self._make_random_text(30).encode()

        stdin_data = f"{to_delete}\n{old_name}\n{new_name}\n"

        initial_files = {
            to_delete: delete_content,
            old_name:  old_content,
        }

        # После работы программы: to_delete и old_name не должны существовать,
        # new_name должен содержать то, что было в old_name
        expected_stdout    = "ok\nok"
        expected_files     = {new_name: old_content}
        files_must_not_exist = [to_delete, old_name]

        return stdin_data, initial_files, [], expected_stdout, expected_files, files_must_not_exist, False

    def _generate_read_hex_test(self):
        """
        Генерирует тест для задания: читать N байт из файла и выводить в hex.

        Размер группы: 1, 2, 4 или 8 байт (little-endian).
        """
        # Выбираем размер группы и количество байт кратное ему
        group_size = random.choice([1, 2, 4, 8])
        count      = random.randint(1, 8) * group_size

        # Файл должен быть достаточно большим
        file_size = random.randint(count + 32, count + 96)
        offset    = random.randint(0, file_size - count)

        filename = self._make_random_filename('data', '.bin')
        content  = bytes(random.randint(0, 255) for _ in range(file_size))

        # Вычисляем ожидаемый вывод
        chunk = content[offset:offset + count]
        hex_parts = []
        for i in range(0, len(chunk), group_size):
            group_bytes = chunk[i:i + group_size]
            value = int.from_bytes(group_bytes, 'little')
            if group_size == 1:
                hex_parts.append('%02x' % value)
            elif group_size == 2:
                hex_parts.append('%04x' % value)
            elif group_size == 4:
                hex_parts.append('%08x' % value)
            else:
                hex_parts.append('%016x' % value)

        expected_stdout = ' '.join(hex_parts)
        stdin_data = f"{filename}\n{offset}\n{count}\n{group_size}\n"

        return stdin_data, {filename: content}, [], expected_stdout, {}, [], False

    def _generate_overwrite_bytes_test(self):
        """
        Генерирует тест для задания: перезаписать байты в файле по смещению.

        Вывод программы не проверяется — проверяем только содержимое файла.
        """
        file_size  = random.randint(self.MIN_FILE_SIZE, self.MAX_FILE_SIZE)
        original   = self._make_random_text(file_size)
        offset     = random.randint(0, file_size - 10)
        write_data = self._make_random_text(random.randint(4, 10))

        filename = self._make_random_filename('cfg', '.txt')

        # Вычисляем ожидаемое содержимое файла после перезаписи
        content_bytes = bytearray(original.encode())
        write_bytes   = write_data.encode()
        end_pos       = min(offset + len(write_bytes), file_size)
        content_bytes[offset:end_pos] = write_bytes[:end_pos - offset]

        stdin_data     = f"{filename}\n{offset}\n{write_data}\n"
        initial_files  = {filename: original.encode()}
        # Вывода нет — None означает «не проверять stdout»
        expected_stdout = None
        expected_files  = {filename: bytes(content_bytes)}

        return stdin_data, initial_files, [], expected_stdout, expected_files, [], False

    def _generate_file_stats_test(self):
        """
        Генерирует тест для задания: вывести статистику файла.

        Программа должна вывести: размер в байтах, кол-во строк, длину самой длинной строки.
        """
        # Генерируем строки случайной длины
        num_lines = random.randint(self.MIN_LINES, 10)
        lines = []
        for _ in range(num_lines):
            line_len = random.randint(self.MIN_LINE_LEN, self.MAX_LINE_LEN)
            lines.append(self._make_random_text(line_len))

        content  = '\n'.join(lines) + '\n'
        filename = self._make_random_filename('stats', '.txt')

        # Вычисляем ожидаемые значения
        file_size   = len(content.encode())
        line_count  = content.count('\n')
        longest_len = max(len(line) for line in lines)

        expected_stdout = f"{file_size}\n{line_count}\n{longest_len}"
        stdin_data      = f"{filename}\n"

        return stdin_data, {filename: content.encode()}, [], expected_stdout, {}, [], False

    def _generate_merge_files_test(self):
        """
        Генерирует тест для задания: дописать содержимое одного файла в конец другого.

        Программа должна вывести итоговый размер файла dst в байтах.
        """
        src_name = self._make_random_filename('src', '.txt')
        dst_name = self._make_random_filename('dst', '.txt')

        src_content = self._make_random_file_content().encode()
        dst_content = self._make_random_file_content().encode()

        # После объединения dst содержит свои данные + данные src
        merged_content  = dst_content + src_content
        expected_stdout = str(len(merged_content))

        stdin_data    = f"{src_name}\n{dst_name}\n"
        initial_files = {src_name: src_content, dst_name: dst_content}
        expected_files = {dst_name: merged_content}

        return stdin_data, initial_files, [], expected_stdout, expected_files, [], False

    def _generate_list_directory_test(self):
        """
        Генерирует тест для задания: вывести содержимое директории с типами записей.

        Вывод: имя [file|dir|link], отсортировано лексикографически.
        """
        dir_name = f"mydir_{random.randint(100, 999)}"
        extensions = ['.txt', '.md', '.c', '.h']

        # Генерируем несколько файлов с уникальными именами
        file_names_set = set()
        for _ in range(random.randint(2, 5)):
            ext  = random.choice(extensions)
            name = self._make_random_filename('f', ext)
            file_names_set.add(name)
        file_names = list(file_names_set)

        # Генерируем несколько поддиректорий
        num_subdirs = random.randint(1, 3)
        sub_dirs    = [f"subdir_{i}" for i in range(num_subdirs)]

        # Формируем начальные файлы и директории
        initial_files = {}
        for fn in file_names:
            initial_files[f"{dir_name}/{fn}"] = b"content"

        initial_dirs = [dir_name] + [f"{dir_name}/{sd}" for sd in sub_dirs]

        # Добавляем один симлинк, указывающий на первый файл
        link_name = f"link_{random.randint(1000, 9999)}"
        initial_symlinks = {f"{dir_name}/{link_name}": file_names[0]}

        # Ожидаемый вывод: все записи отсортированы, с типом
        all_entries = sorted(file_names + sub_dirs + [link_name])
        file_set    = set(file_names)
        link_set    = {link_name}
        output_lines = []
        for entry in all_entries:
            if entry in link_set:
                output_lines.append(f"{entry} [link]")
            elif entry in file_set:
                output_lines.append(f"{entry} [file]")
            else:
                output_lines.append(f"{entry} [dir]")

        expected_stdout = '\n'.join(output_lines)
        stdin_data      = f"{dir_name}\n"

        return stdin_data, initial_files, initial_dirs, expected_stdout, {}, [], False, initial_symlinks

    def _generate_count_lines_test(self):
        """
        Генерирует тест для задания: подсчитать строки в каждом файле директории.

        Вывод: имя_файла: количество_строк, отсортировано по имени.
        """
        dir_name = f"texts_{random.randint(100, 999)}"

        # Генерируем несколько файлов
        num_files = random.randint(2, 5)
        file_data = {}
        for i in range(num_files):
            fname   = f"file{i:02d}.txt"
            content = self._make_random_file_content(min_lines=2, max_lines=6)
            count   = content.count('\n')
            file_data[fname] = (content, count)

        initial_files = {}
        for fname, (content, _) in file_data.items():
            initial_files[f"{dir_name}/{fname}"] = content.encode()

        # Вывод отсортирован по имени файла
        output_lines = []
        for fname, (_, count) in sorted(file_data.items()):
            output_lines.append(f"{fname}: {count}")

        expected_stdout = '\n'.join(output_lines)
        stdin_data      = f"{dir_name}\n"

        return stdin_data, initial_files, [dir_name], expected_stdout, {}, [], True

    def generateTest(self):
        """
        Генерирует тестовый набор данных в зависимости от типа задания.

        Возвращает кортеж:
          (stdin, начальные_файлы, начальные_директории,
           ожидаемый_stdout, ожидаемые_файлы_после, удалённые_файлы, сортировать_вывод)
        """
        if self.taskType == self.TASK_DELETE_RENAME:
            return self._generate_delete_rename_test()
        elif self.taskType == self.TASK_READ_HEX:
            return self._generate_read_hex_test()
        elif self.taskType == self.TASK_OVERWRITE_BYTES:
            return self._generate_overwrite_bytes_test()
        elif self.taskType == self.TASK_FILE_STATS:
            return self._generate_file_stats_test()
        elif self.taskType == self.TASK_MERGE_FILES:
            return self._generate_merge_files_test()
        elif self.taskType == self.TASK_LIST_DIRECTORY:
            return self._generate_list_directory_test()
        else:
            return self._generate_count_lines_test()

    def _check_test_case(self, abs_exec_path, test_data):
        """
        Запускает один тестовый случай и возвращает Result.Fail при несоответствии,
        или None если всё в порядке.
        """
        stdin_data, initial_files, initial_dirs, expected_stdout, expected_files, must_not_exist, sort_output, *rest = test_data
        initial_symlinks = rest[0] if rest else {}

        # Запускаем программу
        try:
            actual_stdout, result_files = self._run_program_with_files(
                abs_exec_path, stdin_data, initial_files, initial_dirs, initial_symlinks
            )
        except ExecutionError as e:
            return Result.Fail(stdin_data, expected_stdout or '', str(e))

        # Проверяем stdout (если он важен для этого задания)
        if expected_stdout is not None:
            if sort_output:
                # Для заданий, где порядок вывода не важен — сортируем обе стороны
                actual_sorted   = '\n'.join(sorted(actual_stdout.splitlines()))
                expected_sorted = '\n'.join(sorted(expected_stdout.splitlines()))
                if actual_sorted != expected_sorted:
                    return Result.Fail(stdin_data, expected_stdout, actual_stdout)
            else:
                if actual_stdout != expected_stdout:
                    return Result.Fail(stdin_data, expected_stdout, actual_stdout)

        # Проверяем содержимое файлов, которые должны существовать
        for fname, expected_content in expected_files.items():
            normalized = fname.replace('\\', '/')
            actual_content = result_files.get(normalized)
            if actual_content is None:
                return Result.Fail(
                    stdin_data,
                    f"{fname}: (файл должен существовать)",
                    "(файл отсутствует)"
                )
            if actual_content != expected_content:
                return Result.Fail(
                    stdin_data,
                    f"{fname}:\n{expected_content!r}",
                    f"{fname}:\n{actual_content!r}"
                )

        # Проверяем, что удалённые файлы действительно исчезли
        for fname in must_not_exist:
            normalized = fname.replace('\\', '/')
            if normalized in result_files:
                return Result.Fail(
                    stdin_data,
                    f"{fname}: (файл должен быть удалён)",
                    "(файл существует)"
                )

        return None

    def test(self, code: str) -> Result.Ok | Result.Fail:
        """
        Компилирует и проверяет код студента на нескольких тестовых случаях.
        """
        program  = CProgramRunner(code)
        abs_exec = os.path.abspath(program.executable_path)

        # Сначала прогоняем детерминированные тесты (воспроизводимые)
        random.seed(self.seed)
        for _ in range(self.FIXED_TESTS_COUNT):
            fail = self._check_test_case(abs_exec, self.generateTest())
            if fail is not None:
                return fail

        # Затем дополнительные тесты с другим сидом для расширения покрытия
        random.seed(self.seed + 1)
        for _ in range(self.RANDOM_TESTS_COUNT):
            fail = self._check_test_case(abs_exec, self.generateTest())
            if fail is not None:
                return fail

        return Result.Ok()

    def _get_task_condition(self) -> str:
        if self.taskType == self.TASK_DELETE_RENAME:
            return '''<p>Удалите файл <b>to_delete</b>, затем переименуйте <b>old_name</b> в <b>new_name</b>.</p>
<p>Для каждой операции выведите <code>ok</code> при успехе или <code>error</code> при ошибке.</p>
<p><b>Важно:</b> используйте функции <code>remove</code> и <code>rename</code>.</p>'''

        elif self.taskType == self.TASK_READ_HEX:
            return '''<p>Прочитайте <b>N</b> байт из файла с позиции <b>offset</b>, интерпретируйте их группами
по <b>group_size</b> байт (little-endian) и выведите каждую группу как hex-число через пробел.</p>
<p>Форматы: 1 байт → <code>%02x</code>, 2 байта → <code>%04x</code>,
4 байта → <code>%08x</code>, 8 байт → <code>%016x</code>.</p>
<p><b>Важно:</b> <b>N</b> всегда кратно <b>group_size</b>. Используйте <code>fopen</code>,
<code>fseek</code> с <code>SEEK_SET</code>, <code>fread</code>.</p>'''

        elif self.taskType == self.TASK_OVERWRITE_BYTES:
            return '''<p>Запишите содержимое строки <b>data</b> в файл начиная с позиции <b>offset</b>,
перезаписав существующие байты. Остальное содержимое файла не должно изменяться.</p>
<p><b>Важно:</b> откройте файл в режиме <code>"r+"</code>, используйте <code>fseek</code>
с <code>SEEK_SET</code> и <code>fwrite</code>. Вывод не требуется.</p>'''

        elif self.taskType == self.TASK_FILE_STATS:
            return '''<p>Выведите три характеристики файла:</p>
<ol>
    <li>Размер файла в байтах (через <code>fseek(SEEK_END)</code> + <code>ftell</code>)</li>
    <li>Количество строк (количество символов <code>\\n</code>)</li>
    <li>Длина самой длинной строки (без символа <code>\\n</code>)</li>
</ol>
<p><b>Важно:</b> используйте <code>fseek</code>, <code>ftell</code> и <code>fgets</code>.</p>'''

        elif self.taskType == self.TASK_MERGE_FILES:
            return '''<p>Допишите содержимое файла <b>src</b> в конец файла <b>dst</b>
(не удаляя существующее содержимое). Выведите итоговый размер файла <b>dst</b> в байтах.</p>
<p><b>Важно:</b> используйте <code>fopen(dst, "ab")</code>, <code>fread</code>, <code>fwrite</code>.</p>'''

        elif self.taskType == self.TASK_LIST_DIRECTORY:
            return '''<p>Выведите все записи в директории (кроме <code>.</code> и <code>..</code>)
в лексикографическом порядке, по одной на строку в формате:
<code>имя [тип]</code>, где тип — <code>file</code>, <code>dir</code> или <code>link</code>.</p>
<p><b>Важно:</b> для определения типа используйте <code>lstat</code> (не <code>stat</code>) —
она не разыменовывает символические ссылки. Используйте <code>opendir</code>, <code>readdir</code>.</p>'''

        else:
            return '''<p>Для каждого обычного файла в директории (не рекурсивно) подсчитайте количество строк
(количество символов <code>\\n</code>).</p>
<p>Выведите результаты в формате: <code>имя: количество</code> (по одному на строку, порядок любой).</p>
<p><b>Важно:</b> используйте <code>opendir</code>, <code>readdir</code>, <code>stat</code>, <code>fgets</code>.</p>'''

    def _get_input_format(self) -> str:
        base = '<p><b>Формат входных данных:</b></p><ul>'

        if self.taskType == self.TASK_DELETE_RENAME:
            base += '<li>Строка <b>to_delete</b> — имя файла для удаления</li>'
            base += '<li>Строка <b>old_name</b> — текущее имя файла</li>'
            base += '<li>Строка <b>new_name</b> — новое имя файла</li>'

        elif self.taskType == self.TASK_READ_HEX:
            base += '<li>Строка <b>filename</b> — имя бинарного файла</li>'
            base += '<li>Целое число <b>offset</b> — смещение от начала файла (в байтах)</li>'
            base += '<li>Целое число <b>N</b> — количество байт для чтения</li>'
            base += '<li>Целое число <b>group_size</b> — размер группы (1, 2, 4 или 8)</li>'

        elif self.taskType == self.TASK_OVERWRITE_BYTES:
            base += '<li>Строка <b>filename</b> — имя файла</li>'
            base += '<li>Целое число <b>offset</b> — смещение от начала файла (в байтах)</li>'
            base += '<li>Строка <b>data</b> — данные для записи</li>'

        elif self.taskType == self.TASK_FILE_STATS:
            base += '<li>Строка <b>filename</b> — имя текстового файла</li>'

        elif self.taskType == self.TASK_MERGE_FILES:
            base += '<li>Строка <b>src</b> — имя файла-источника</li>'
            base += '<li>Строка <b>dst</b> — имя файла-приёмника</li>'

        elif self.taskType == self.TASK_LIST_DIRECTORY:
            base += '<li>Строка <b>dirname</b> — имя директории</li>'

        else:
            base += '<li>Строка <b>dirname</b> — имя директории</li>'

        base += '</ul>'
        return base

    def _get_output_format(self) -> str:
        if self.taskType == self.TASK_DELETE_RENAME:
            return ('<p><b>Формат выходных данных:</b></p>'
                    '<p>Две строки: <code>ok</code> или <code>error</code> для каждой операции (удаление, переименование).</p>')
        elif self.taskType == self.TASK_READ_HEX:
            return ('<p><b>Формат выходных данных:</b></p>'
                    '<p>Hex-числа через пробел в одну строку.</p>')
        elif self.taskType == self.TASK_OVERWRITE_BYTES:
            return ('<p><b>Формат выходных данных:</b></p>'
                    '<p>Вывод не требуется. Проверяется содержимое файла после работы программы.</p>')
        elif self.taskType == self.TASK_FILE_STATS:
            return ('<p><b>Формат выходных данных:</b></p>'
                    '<p>Три строки: размер в байтах, количество строк, длина самой длинной строки.</p>')
        elif self.taskType == self.TASK_MERGE_FILES:
            return ('<p><b>Формат выходных данных:</b></p>'
                    '<p>Одно число — итоговый размер файла <b>dst</b> в байтах.</p>')
        elif self.taskType == self.TASK_LIST_DIRECTORY:
            return ('<p><b>Формат выходных данных:</b></p>'
                    '<p>По одной записи на строку: <code>имя [тип]</code>, отсортировано лексикографически.</p>')
        else:
            return ('<p><b>Формат выходных данных:</b></p>'
                    '<p>По одной записи на строку: <code>имя: количество</code>.</p>')

    def _get_example(self) -> tuple:
        examples = {
            self.TASK_DELETE_RENAME: (
                'to_delete.txt\nold.txt\nnew.txt',
                'ok\nok',
            ),
            self.TASK_READ_HEX: (
                'data.bin\n4\n8\n2',
                '3f1a 92b0 c401 58de',
            ),
            self.TASK_OVERWRITE_BYTES: (
                'config.txt\n5\nNEWDATA',
                '(нет вывода)',
            ),
            self.TASK_FILE_STATS: (
                'data.txt',
                '42\n3\n18',
            ),
            self.TASK_MERGE_FILES: (
                'src.txt\ndst.txt',
                '87',
            ),
            self.TASK_LIST_DIRECTORY: (
                './mydir',
                'notes.txt [file]\nreport.md [file]\nsrc [dir]',
            ),
            self.TASK_COUNT_LINES: (
                './texts',
                'a.txt: 5\nb.txt: 3\nnotes.txt: 7',
            ),
        }
        return examples[self.taskType]

    @property
    def questionText(self) -> str:
        titles = {
            self.TASK_DELETE_RENAME:  'Удаление и переименование файла',
            self.TASK_READ_HEX:      'Чтение байт из файла в hex-формате',
            self.TASK_OVERWRITE_BYTES:'Перезапись байт по позиции',
            self.TASK_FILE_STATS:    'Статистика файла',
            self.TASK_MERGE_FILES:   'Объединение файлов',
            self.TASK_LIST_DIRECTORY: 'Список содержимого директории',
            self.TASK_COUNT_LINES:   'Подсчёт строк в файлах директории',
        }
        title = titles[self.taskType]

        is_dir_task = self.taskType in (self.TASK_LIST_DIRECTORY, self.TASK_COUNT_LINES)
        if is_dir_task:
            api_hint = ('Для работы с директориями используйте POSIX-функции '
                        '(<code>opendir</code>, <code>readdir</code>, <code>stat</code>/<code>lstat</code>).')
        else:
            api_hint = ('Для работы с файлами используйте стандартные функции C '
                        '(<code>fopen</code>, <code>fclose</code>, <code>fseek</code>, '
                        '<code>fread</code>, <code>fwrite</code>, <code>rename</code>, <code>remove</code>).')

        ex_in, ex_out = self._get_example()

        return f'''
<p>Язык: <b>C</b> (компиляция <code>gcc</code>). {api_hint}</p>

{self._get_task_condition()}
{self._get_input_format()}
{self._get_output_format()}

<b>Пример</b>
<table class="coderunnerexamples">
    <thead>
        <tr>
            <th class="header c0" scope="col">Входные данные</th>
            <th class="header c1 lastcol" scope="col">Результат</th>
        </tr>
    </thead>
    <tbody>
        <tr class="r0 lastrow">
            <td class="cell c0"><pre class="tablecell">{ex_in}</pre></td>
            <td class="cell c1 lastcol"><pre class="tablecell">{ex_out}</pre></td>
        </tr>
    </tbody>
</table>
'''

    @property
    def preloadedCode(self) -> str:
        """
        Шаблон кода, который видит студент при открытии задания.
        """
        return '\n'.join([
            '#include <stdio.h>',
            '#include <stdlib.h>',
            '',
            'int main() {',
            '',
            '    return 0;',
            '}',
        ])
