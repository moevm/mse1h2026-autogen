from ..QuestionBase import QuestionBase, Result
from ..utility import CProgramRunner, ExecutionError
import random
import re
import time

HTTP_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS', 'TRACE', 'CONNECT']
# Методы для генерации строк, которые не должны попасть в вывод
FAKE_METHODS = ['GETAWAY', 'FETCH', 'SUBMIT', 'SEND', 'RETRIEVE', 'REMOVE', 'PUSH', 'DOWNLOAD', 'UPLOAD']

VALID_ZONES = ['ru', 'com', 'org', 'net', 'edu', 'gov', 'io', 'info', 'biz', 'name']
# Доменные зоны неподходящего размера для некорректных email
INVALID_ZONES = ['x', 'media', 'travel', 'international']

# Суффиксы имён файлов резервных копий
FILE_SUFFIXES = ['.img', '.tar.gz', '.zip', '.bak', '.tar', '.gz', '.dump', '.sql']
FILE_PREFIXES = ['backup', 'report', 'project', 'data', 'archive', 'snapshot', 'db']

# Форматы дат
DATE_FORMATS = ['YYYY-MM-DD', 'MM-DD-YYYY', 'DD-MM-YYYY']

# Утилиты с версиями
UTILS = ['nginx', 'OpenSSL', 'git', 'Python', 'curl', 'bash', 'gcc', 'perl', 'ruby', 'php']

# Форматы строк с версиями
VERSION_TEMPLATES = [
    '{name} version: {name}/{version}',
    '{name} {version} {extra}',
    '{name} version {version}',
    '{name} {version} ({extra})',
    '{name} {version}',
]
# Некорректные строки без версии
NO_VERSION_LINES = [
    '{name}: no version info',
    '{name}: version unknown',
    '{name} (not installed)',
]

# URL-схемы
URL_SCHEMES = ['https', 'http']
URL_DOMAINS = [
    'example.com', 'site.ru', 'shop.org', 'files.corp.net',
    'api.service.io', 'cdn.media.biz', 'docs.example.edu'
]
URL_PATHS = [
    '/api/v1/users', '/about', '/catalog/item?id=42', '/data/backup.tar',
    '/login', '/search?q=hello', '/img/logo.png', '/docs/readme',
    '/v2/orders/123', '/health', '/metrics?format=json'
]


def random_ip(rng: random.Random) -> str:
    return '.'.join(str(rng.randint(0, 255)) for _ in range(4))

def random_date_str(rng: random.Random) -> str:
    year = rng.randint(2000, 2026)
    month = rng.randint(1, 12)
    day = rng.randint(1, 31)
    return f'{year:04d}-{month:02d}-{day:02d}'

def random_path(rng: random.Random) -> str:
    segments = rng.randint(1, 3)
    parts = [''.join(rng.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=rng.randint(3, 8))) for _ in range(segments)]
    return '/' + '/'.join(parts)

def random_version(rng: random.Random, include_patch: bool = None) -> str:
    major = rng.randint(1, 15)
    minor = rng.randint(0, 99)
    if include_patch is None:
        include_patch = rng.random() < 0.6
    if include_patch:
        patch = rng.randint(0, 20)
        return f'{major}.{minor}.{patch}'
    return f'{major}.{minor}'


class QuestionN1(QuestionBase):
    questionName = 'Задание 1, Регулярные выражения'
    COMPILE_FLAGS = '-Wall -Werror -Wreturn-type -g -fsanitize=address,undefined'

    def __init__(self, *, seed, maxLines: int = 10):
        super().__init__(seed=seed)
        self.maxLines = maxLines

        rng = random.Random(self.seed)
        self.variant = rng.choice([
            'http_method',       # 1.1 - HTTP-метод из строки лога
            'email',             # 1.2 - email
            'date_in_filename',  # 1.3 - дата в имени файла
            'version',           # 1.4 - версия программы
            'url_path',          # 1.5 - путь из URL
        ])
        _sub_variants = {
            'http_method':      ['method', 'ip', 'status', 'time'],
            'email':            ['full_email', 'domain', 'username'],
            'date_in_filename': ['as_is', 'normalize_iso'],
            'version':          ['full_version', 'major_minor'],
            'url_path':         ['path', 'scheme', 'domain'],
        }
        self.sub_variant = rng.choice(_sub_variants[self.variant])

    def _apply(self, line: str) -> str | None:
        is_whole_match_variant = self.sub_variant in ['full_email', 'full_version', 'as_is', 'normalize_iso']

        def get_res(m):
            if not m: return None
            
            if m.lastindex is None or m.lastindex == 0:
                if self.variant == 'email' and self.sub_variant != 'full_email':
                    full = m.group(0)
                    if '@' in full:
                        parts = full.split('@', 1)
                        return parts[1] if self.sub_variant == 'domain' else parts[0]

                if self.variant == 'url_path':
                    full = m.group(0)
                    if '://' in full:
                        sch_end = full.find('://')
                        scheme = full[:sch_end]
                        rest = full[sch_end+3:]
                        slash_pos = rest.find('/')
                        if slash_pos == -1:
                            domain, path = rest, ""
                        else:
                            domain, path = rest[:slash_pos], rest[slash_pos:]

                        if self.sub_variant == 'scheme': return scheme
                        if self.sub_variant == 'domain': return domain
                        if self.sub_variant == 'path':   return path if path else None
            if m.lastindex is not None and m.lastindex >= 1:
                # Если есть группа, совпадающая со всем вхождением, берём её
                for i in range(1, m.lastindex + 1):
                    if m.group(i) == m.group(0):
                        return m.group(i)

                # Если это вариант, где ожидается совпадение целиком, игнорируем внутренние группы
                if is_whole_match_variant:
                    return m.group(0)

                # Иначе берём первую непустую группу 
                res_group = None
                for i in range(1, m.lastindex + 1):
                    if m.group(i) is not None:
                        res_group = m.group(i)
                return res_group
            return m.group(0)

        match self.variant:
            case 'http_method':
                m = re.search(
                    r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]\s+'
                    r'(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS|TRACE|CONNECT)\s+'
                    r'\S+\s+from\s+(\d+\.\d+\.\d+\.\d+)\s+status=(\d+)',
                    line
                )
                if not m: return None
                match self.sub_variant:
                    case 'method':  return m.group(2)
                    case 'ip':      return m.group(3)
                    case 'status':  return m.group(4)
                    case 'time':    return m.group(1)
 
            case 'email':
                emails = []
                pos = 0
                while True:
                    m = re.search(r'[A-Za-z0-9](?:[A-Za-z0-9._\-]*[A-Za-z0-9])?'
                                r'@[A-Za-z0-9][A-Za-z0-9.\-]*\.[A-Za-z]{2,4}(?!\w)', line[pos:])
                    if not m: break
                    
                    match_end = pos + m.end()
                    
                    after = line[match_end] if match_end < len(line) else ' '
                    if not after.isalpha():
                        out = get_res(m)
                        if out: emails.append(out)
                    
                    pos = match_end
                    if m.end() == 0: pos += 1
                    if pos >= len(line): break
                return '\n'.join(emails) if emails else None
 
            case 'date_in_filename':
                m = re.search(r'(\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4})', line)
                return get_res(m)
 
            case 'version':
                m = re.search(r'(\d+\.\d+)(\.\d+)?', line)
                return get_res(m)
 
            case 'url_path':
                m = re.search(r'^(?:https?|ftp)://[^/\s]+(/.*)?', line)
                if not m: return None
                return get_res(m)

    def applyToInput(self, lines: list[str]) -> str:
        results = []
        for line in lines:
            out = self._apply(line.rstrip('\n'))
            if out is not None:
                results.append(out)
        return '\n'.join(results)

    def _gen_http_lines(self, rng: random.Random, n: int, good: bool) -> list[str]:
        lines = []
        for _ in range(n):
            date = f'[{rng.randint(2000,2026):04d}-{rng.randint(1,12):02d}-{rng.randint(1,28):02d} ' \
                   f'{rng.randint(0,23):02d}:{rng.randint(0,59):02d}:{rng.randint(0,59):02d}]'
            ip = random_ip(rng)
            status = rng.choice([200, 201, 301, 302, 400, 401, 403, 404, 500])
            path = random_path(rng)
            if self.sub_variant == 'method':
                if good or rng.random() < 0.5:
                    method = rng.choice(HTTP_METHODS)
                else:
                    method = rng.choice(FAKE_METHODS)
            else:
                method = rng.choice(HTTP_METHODS)
                if not good and rng.random() < 0.5:
                    lines.append(f'{date} {method} {path} {ip} code={status}')
                    continue
            lines.append(f'{date} {method} {path} from {ip} status={status}')
        return lines

    def _gen_email_lines(self, rng: random.Random, n: int, good: bool) -> list[str]:
        lines = []
        prefixes = ['Корпоративная почта:', 'Поддержка:', 'Свяжитесь:', 'Адрес:', 'Для обратной связи:']
        for _ in range(n):
            prefix = rng.choice(prefixes)
            if good or rng.random() < 0.5:
                name_len = rng.randint(3, 10)
                name = ''.join(rng.choices('abcdefghijklmnopqrstuvwxyz0123456789._-', k=name_len)).strip('._-')
                domain = ''.join(rng.choices('abcdefghijklmnopqrstuvwxyz', k=rng.randint(3, 8)))
                zone = rng.choice(VALID_ZONES)
                email = f'{name}@{domain}.{zone}'
            else:
                choice = rng.randint(0, 4)
                if choice == 0:
                    email = f'@nodomain'
                elif choice == 1:
                    name = ''.join(rng.choices('abcdefghijklmnopqrstuvwxyz', k=5))
                    email = f'{name}@'
                elif choice == 2:
                    name = ''.join(rng.choices('abcdefghijklmnopqrstuvwxyz', k=5))
                    domain = ''.join(rng.choices('abcdefghijklmnopqrstuvwxyz', k=rng.randint(3, 8)))
                    email = f'{name}@{domain}.x'
                elif choice == 3:
                    domain = ''.join(rng.choices('abcdefghijklmnopqrstuvwxyz', k=rng.randint(3, 8)))
                    zone = rng.choice(VALID_ZONES)
                    name = '.' + ''.join(rng.choices('abcdefghijklmnopqrstuvwxyz', k=5))
                    email = f'{name}@{domain}.{zone}'
                else:  
                    domain = ''.join(rng.choices('abcdefghijklmnopqrstuvwxyz', k=rng.randint(3, 8)))
                    zone = rng.choice(VALID_ZONES)
                    name = ''.join(rng.choices('abcdefghijklmnopqrstuvwxyz', k=5)) + '.'
                    email = f'{name}@{domain}.{zone}'
            lines.append(f'{prefix} {email}'.strip())
        return lines

    def _gen_filename_lines(self, rng: random.Random, n: int, good: bool) -> list[str]:
        lines = []
        no_date = ['README.md', 'project_final.zip', 'config.yaml', 'Makefile', 'notes.txt']
        for _ in range(n):
            if good or rng.random() < 0.5:
                year = rng.randint(2000, 2026)
                month = rng.randint(1, 12)
                day = rng.randint(1, 28)
                fmt = rng.choice(DATE_FORMATS)
                if fmt == 'YYYY-MM-DD':
                    date_str = f'{year:04d}-{month:02d}-{day:02d}'
                elif fmt == 'MM-DD-YYYY':
                    date_str = f'{month:02d}-{day:02d}-{year:04d}'
                else:
                    date_str = f'{day:02d}-{month:02d}-{year:04d}'
                prefix = rng.choice(FILE_PREFIXES)
                suffix = rng.choice(FILE_SUFFIXES)
                sep = rng.choice(['_', '-', ''])
                lines.append(f'{prefix}{sep}{date_str}{suffix}')
            else:
                lines.append(rng.choice(no_date))
        return lines

    def _gen_version_lines(self, rng: random.Random, n: int, good: bool) -> list[str]:
        lines = []
        extras = ['12 Jan 2022', 'main, Feb 5 2021', 'x86_64-pc-linux-gnu', 'stable']
        for _ in range(n):
            name = rng.choice(UTILS)
            if good or rng.random() < 0.5:
                version = random_version(rng)
                tmpl = rng.choice(VERSION_TEMPLATES)
                extra = rng.choice(extras)
                lines.append(tmpl.format(name=name, version=version, extra=extra).strip())
            else:
                tmpl = rng.choice(NO_VERSION_LINES)
                lines.append(tmpl.format(name=name))
        return lines

    def _gen_url_lines(self, rng: random.Random, n: int, good: bool) -> list[str]:
        lines = []
        for _ in range(n):
            scheme = rng.choice(URL_SCHEMES)
            domain = rng.choice(URL_DOMAINS)
            if good or rng.random() < 0.5:
                path = rng.choice(URL_PATHS)
                lines.append(f'{scheme}://{domain}{path}')
            else:
                lines.append(f'{scheme}://{domain}')
        return lines

    def _generate_lines(self, rng: random.Random, n: int, good: bool) -> list[str]:
        match self.variant:
            case 'http_method':     return self._gen_http_lines(rng, n, good)
            case 'email':           return self._gen_email_lines(rng, n, good)
            case 'date_in_filename':return self._gen_filename_lines(rng, n, good)
            case 'version':         return self._gen_version_lines(rng, n, good)
            case 'url_path':        return self._gen_url_lines(rng, n, good)

    def _validate_c_regex_syntax(self, student_input: str) -> str | None:
        pcre_only = re.search(r'(?<!\\)\\[dwsDbBwWS]', student_input)
        if pcre_only:
            return f"Используйте C-строковый синтаксис: \\\\d вместо \\d, [0-9] вместо \\d"
        return None

    def generateGoodTest(self, rng: random.Random | None = None) -> tuple[str, str]:
        if rng is None:
            rng = random.Random(self.seed)
        n = rng.randint(3, self.maxLines)
        lines = self._generate_lines(rng, n, good=True)
        input_text = '\n'.join(lines) + '\n'
        output_text = self.applyToInput(lines)
        return input_text, output_text
 
    def generateBadTest(self, rng: random.Random | None = None) -> tuple[str, str]:
        if rng is None:
            rng = random.Random(self.seed + 1)
        n = rng.randint(3, self.maxLines)
        lines = self._generate_lines(rng, n, good=False)
        input_text = '\n'.join(lines) + '\n'
        output_text = self.applyToInput(lines)
        return input_text, output_text


    @property
    def questionText(self) -> str:
        save_max = self.maxLines
        self.maxLines = 6

        rng_good = random.Random(self.seed)
        goodTest = self.generateGoodTest(rng_good)

        rng_bad = random.Random(self.seed + 1)
        badTest = self.generateBadTest(rng_bad)

        self.maxLines = save_max

        table = f'''
            <table class="coderunnerexamples">
                <thead>
                    <tr>
                        <th class="header c0" style="" scope="col">Входные данные</th>
                        <th class="header c2 lastcol" style="" scope="col">Результат</th>
                    </tr>
                </thead>
                <tbody>
                    <tr class="r0 lastrow">
                            <td class="cell  c1" style=""><pre class="tablecell">{goodTest[0]}</pre></td>
                        <td class="cell  c1" style=""><pre class="tablecell">{goodTest[1]}</pre></td>
                    </tr>
                    <tr class="r0 lastrow">
                            <td class="cell  c1" style=""><pre class="tablecell">{badTest[0]}</pre></td>
                        <td class="cell  c1" style=""><pre class="tablecell">{badTest[1]}</pre></td>
                    </tr>
                </tbody>
            </table>
        '''

        _what_to_extract = {
            ('http_method', 'method'): (
                'HTTP-метод (<code>GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS, TRACE, CONNECT</code>).<br>',
                '<b>Строки с неизвестными методами не выводятся.</b>'
            ),
            ('http_method', 'ip'): (
                'IP-адрес клиента.', ''
            ),
            ('http_method', 'status'): (
                'Код статуса (число после <code>status=</code>).', ''
            ),
            ('http_method', 'time'): (
                'Дату и время запроса (содержимое квадратных скобок, без самих скобок).', ''
            ),
        }

        http_what, http_group_hint = _what_to_extract.get(
            ('http_method', self.sub_variant),
            ('HTTP-метод.', '')
        )
 
        _email_what = {
            'full_email': ('полный адрес электронной почты', 'Каждое совпадение выводится на отдельной строке.'),
            'domain': ('только доменную часть адреса (после <code>@</code>)', ''),
            'username': ('только имя пользователя (до <code>@</code>)', ''),
        }

        email_what, email_group_hint = _email_what.get(self.sub_variant, ('email-адрес', ''))
 
        _url_what = {
            'path': ('путь - часть URL начиная с <code>/</code> после домена. URL без пути не выводятся.', ''),
            'scheme': ('схему URL (<code>http</code> или <code>https</code>).', ''),
            'domain': ('доменное имя (между <code>://</code> и следующим <code>/</code>).', ''),
        }

        url_what, url_group_hint = _url_what.get(self.sub_variant, ('путь.', ''))
 
        _date_what = {
            'as_is': ('дату в том формате, в котором она записана в имени файла.', ''),
            'normalize_iso': ('дату в формате <b>YYYY-MM-DD</b> (если она в другом формате - программа её нормализует). ', 'Строки без даты не выводятся.'),
        }

        date_what, date_group_hint = _date_what.get(self.sub_variant, ('дату.', ''))
 
        _version_what = {
            'full_version': ('полный номер версии (<b>X.Y</b> или <b>X.Y.Z</b>).', ''),
            'major_minor':  ('старшие компоненты версии вида <b>X.Y</b>.', ''),
        }

        version_what, version_group_hint = _version_what.get(self.sub_variant, ('версию.', ''))
 
        variant_texts = {
            'http_method': f'''
                <h3>Извлечение поля из лога HTTP-сервера</h3>
                <p>В логах сервера каждая строка имеет формат:<br>
                <code>[YYYY-MM-DD HH:MM:SS] МЕТОД /путь from IP status=КОД</code><br>
                Напишите регулярное выражение, которое извлекает: <b>{http_what}</b></p>
                <p><b>Язык:</b> C (компилируется
                <code>g++ -Wall -Werror -Wreturn-type -g -fsanitize=address,undefined solution.c -o solution</code>).
                Используйте соответствующий синтаксис. {http_group_hint}</p>
                <p>Пример:</p>{table}
            ''',
            'email': f'''
                <h3>Извлечение данных из email-адреса</h3>
                <p>В тексте встречаются адреса электронной почты. Напишите регулярное выражение, которое
                извлекает <b>{email_what}</b>.<br>
                Формат адреса: <b>имя@домен.зона</b>, где имя состоит из латинских букв, цифр,
                точек, дефисов и подчёркиваний (не начинается и не заканчивается точкой);
                зона - от 2 до 4 латинских букв.</p>
                <p><b>Язык:</b> C (компилируется
                <code>g++ -Wall -Werror -Wreturn-type -g -fsanitize=address,undefined solution.c -o solution</code>).
                Используйте соответствующий синтаксис. {email_group_hint}</p>
                <p>Пример:</p>{table}
            ''',
            'date_in_filename': f'''
                <h3>Извлечение даты из имени файла</h3>
                <p>Каждая строка - одно имя файла резервной копии. Напишите регулярное выражение,
                которое извлекает <b>{date_what}</b><br>
                Допустимые форматы: <b>YYYY-MM-DD</b>, <b>MM-DD-YYYY</b>, <b>DD-MM-YYYY</b>.
                {date_group_hint}</p>
                <p><b>Язык:</b> C (компилируется
                <code>g++ -Wall -Werror -Wreturn-type -g -fsanitize=address,undefined solution.c -o solution</code>).
                Используйте соответствующий синтаксис.</p>
                <p>Пример:</p>{table}
            ''',
            'version': f'''
                <h3>Извлечение версии программы</h3>
                <p>Утилиты при запуске печатают версию в разных форматах. Напишите регулярное выражение,
                которое извлекает <b>{version_what}</b>
                Строки без версии не выводятся.</p>
                <p><b>Язык:</b> C (компилируется
                <code>g++ -Wall -Werror -Wreturn-type -g -fsanitize=address,undefined solution.c -o solution</code>).
                Используйте соответствующий синтаксис. {version_group_hint}</p>
                <p>Пример:</p>{table}
            ''',
            'url_path': f'''
                <h3>Извлечение компонента из URL</h3>
                <p>В таблице редиректов хранятся полные URL вида <code>схема://домен/путь</code>.
                Напишите регулярное выражение, которое извлекает <b>{url_what}</b></p>
                <p><b>Язык:</b> C (компилируется
                <code>g++ -Wall -Werror -Wreturn-type -g -fsanitize=address,undefined solution.c -o solution</code>).
                Используйте соответствующий синтаксис. {url_group_hint}</p>
                <p>Пример:</p>{table}
            ''',
        }
 
        return variant_texts[self.variant]

    _C_TEMPLATE_SINGLE = """
    #include <stdio.h>
    #include <regex.h>
    #include <string.h>

    void print_match(const char *line, regmatch_t *m, int nsub, const char *variant, const char *sub_variant, int is_whole) {{
        int g = 0;
        int start = m[0].rm_so;
        int end = m[0].rm_eo;

        if (strcmp(variant, "email") == 0 && strcmp(sub_variant, "full_email") != 0 && nsub == 0) {{
            const char *at = strchr(line + start, '@');
            if (at) {{
                if (strcmp(sub_variant, "domain") == 0) {{
                    start = (at - line) + 1;
                }} else {{
                    end = (at - line);
                }}
                goto print;
            }}
        }}

        if (strcmp(variant, "url_path") == 0 && nsub == 0) {{
            const char *sep = strstr(line + start, "://");
            if (sep) {{
                const char *sch_end = sep;
                const char *rest = sep + 3;
                const char *slash = strchr(rest, '/');
                
                if (strcmp(sub_variant, "scheme") == 0) {{
                    end = (sch_end - line);
                }} else if (strcmp(sub_variant, "domain") == 0) {{
                    start = (rest - line);
                    if (slash && slash < line + m[0].rm_eo) end = (slash - line);
                    else end = m[0].rm_eo;
                }} else if (strcmp(sub_variant, "path") == 0) {{
                    if (slash && slash < line + m[0].rm_eo) {{
                        start = (slash - line);
                        end = m[0].rm_eo;
                    }} else {{
                        return; 
                    }}
                }}
                goto print;
            }}
        }}

        if (nsub > 0) {{
            for (int i = 1; i <= nsub && i < 8; i++) {{
                if (m[i].rm_so == m[0].rm_so && m[i].rm_eo == m[0].rm_eo) {{
                    g = i;
                    goto found;
                }}
            }}
            if (is_whole) {{
                g = 0;
            }} else {{
                for (int i = 1; i <= nsub && i < 8; i++) {{
                    if (m[i].rm_so != -1) {{
                        g = i;
                    }}
                }}
            }}
        }}
    found:
        start = m[g].rm_so;
        end = m[g].rm_eo;

    print:
        if (strcmp(variant, "date_in_filename") == 0 && strcmp(sub_variant, "normalize_iso") == 0) {{
            char date[64];
            int len = end - start;
            if (len > 63) len = 63;
            if (len < 0) len = 0;
            strncpy(date, line + start, len);
            date[len] = '\\0';
            
            int y, m_val, d;
            if (sscanf(date, "%d-%d-%d", &y, &m_val, &d) == 3 && y > 100) {{
                printf("%04d-%02d-%02d\\n", y, m_val, d);
            }} else if (sscanf(date, "%d-%d-%d", &m_val, &d, &y) == 3) {{
                printf("%04d-%02d-%02d\\n", y, m_val, d);
            }} else {{
                fwrite(line + start, 1, len, stdout);
                putchar('\\n');
            }}
        }} else {{
            fwrite(line + start, 1, end - start, stdout);
            putchar('\\n');
        }}
    }}

    int main() {{
        char line[4096];
        regex_t re;
        regmatch_t m[8];

        if (regcomp(&re, "{regex}", REG_EXTENDED) != 0) {{
            fprintf(stderr, "regex compilation failed\\n");
            return 1;
        }}

        while (fgets(line, sizeof(line), stdin)) {{
            size_t len = strlen(line);
            if (len > 0 && line[len-1] == '\\n') line[len-1] = '\\0';

            if (regexec(&re, line, 8, m, 0) == 0) {{
                print_match(line, m, re.re_nsub, "{variant}", "{sub_variant}", {is_whole});
            }}
        }}
        regfree(&re);
        return 0;
    }}
    """

    _C_TEMPLATE_MULTI_EMAIL = """
    #include <stdio.h>
    #include <regex.h>
    #include <string.h>

    int main() {{
        char line[4096];
        regex_t re;
        regmatch_t m[8];

        if (regcomp(&re, "{regex}", REG_EXTENDED) != 0) {{
            fprintf(stderr, "regex compilation failed\\n");
            return 1;
        }}

        while (fgets(line, sizeof(line), stdin)) {{
            size_t len = strlen(line);
            if (len > 0 && line[len-1] == '\\n') line[len-1] = '\\0';

            char *pos = line;
            while (regexec(&re, pos, 8, m, 0) == 0) {{
                char after = pos[m[0].rm_eo];
                if (!((after >= 'A' && after <= 'Z') ||
                    (after >= 'a' && after <= 'z'))) {{
                    
                    int start = m[0].rm_so;
                    int end = m[0].rm_eo;

                    if (strcmp("{variant}", "email") == 0 && strcmp("{sub_variant}", "full_email") != 0 && re.re_nsub == 0) {{
                        const char *at = strchr(pos + start, '@');
                        if (at) {{
                            if (strcmp("{sub_variant}", "domain") == 0) {{
                                start = (at - pos) + 1;
                            }} else {{
                                end = (at - pos);
                            }}
                            goto print_multi;
                        }}
                    }}

                    int g = 0;
                    if (re.re_nsub > 0) {{
                        for (int i = 1; i <= (int)re.re_nsub && i < 8; i++) {{
                            if (m[i].rm_so == m[0].rm_so && m[i].rm_eo == m[0].rm_eo) {{
                                g = i;
                                goto found_multi;
                            }}
                        }}
                        if ({is_whole}) {{
                            g = 0;
                        }} else {{
                            for (int i = 1; i <= (int)re.re_nsub && i < 8; i++) {{
                                if (m[i].rm_so != -1) {{
                                    g = i;
                                }}
                            }}
                        }}
                    }}
                found_multi:
                    start = m[g].rm_so;
                    end = m[g].rm_eo;
                
                print_multi:
                    fwrite(pos + start, 1, end - start, stdout);
                    putchar('\\n');
                }}
                int skip = m[0].rm_eo;
                if (skip == 0) skip = 1;
                pos += skip;
                if (*pos == '\\0') break;
            }}
        }}
        regfree(&re);
        return 0;
    }}
    """

    # Оборачивает regex студента в C-программу
    def _wrap_regex_in_c(self, student_regex: str) -> str:
        escaped = student_regex.replace('\\', '\\\\').replace('"', '\\"')
        is_whole = 1 if self.sub_variant in ['full_email', 'full_version', 'as_is', 'normalize_iso'] else 0

        if (self.variant == 'email'):
            return self._C_TEMPLATE_MULTI_EMAIL.format(
                regex=escaped, 
                is_whole=is_whole,
                variant=self.variant,
                sub_variant=self.sub_variant
            )

        return self._C_TEMPLATE_SINGLE.format(
            regex=escaped, 
            variant=self.variant, 
            sub_variant=self.sub_variant,
            is_whole=is_whole
        )


    @property 
    def preloadedCode(self):
        return ""
    
    # Запускает тест и возвращает Fail при несовпадении, иначе None
    def _run_test(self, program: CProgramRunner, program_input: str, expected: str) -> Result.Ok | Result.Fail | None:
        try:
            result = program.run(program_input)
            result_norm   = '\n'.join(l.rstrip() for l in result.rstrip('\n').splitlines())
            expected_norm = '\n'.join(l.rstrip() for l in expected.rstrip('\n').splitlines())
            if result_norm != expected_norm:
                return Result.Fail(program_input, expected, result)
        except ExecutionError as e:
            return Result.Fail(program_input, expected, str(e))
        return None

    def test(self, code: str) -> Result.Ok | Result.Fail:
        syntax_error = self._validate_c_regex_syntax(code.strip())
        if syntax_error:
            return Result.Fail('', '', syntax_error)

        c_code = self._wrap_regex_in_c(code.strip())
        program = CProgramRunner(c_code)

        rng_good = random.Random(self.seed)
        for _ in range(3):
            inp, out = self.generateGoodTest(rng_good)
            fail = self._run_test(program, inp, out)
            if fail:
                return fail

        rng_bad = random.Random(self.seed + 1)
        for _ in range(3):
            inp, out = self.generateBadTest(rng_bad)
            fail = self._run_test(program, inp, out)
            if fail:
                return fail

        rng_random = random.Random(int(time.time()))
        for _ in range(30):
            if rng_random.random() < 0.6:
                inp, out = self.generateGoodTest(rng_random)
            else:
                inp, out = self.generateBadTest(rng_random)
            fail = self._run_test(program, inp, out)
            if fail:
                return fail

        return Result.Ok()