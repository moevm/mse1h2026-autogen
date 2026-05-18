from pathlib import Path
import shutil
import tempfile
import zipfile
import base64
import os
import lxml.etree as xml
import ast
import sys
import copy
import json


# Константы
ROOT = Path(__file__).resolve().parent.parent
SOURCE_PATH = ROOT / 'src'
OUTPUT_PATH = ROOT / 'dist'
OUTPUT_DEBUG_PATH = OUTPUT_PATH / 'debug'
XML_TEMPLATE_PATH = ROOT / 'build' / 'template.xml'

BUILD_DEBUG = '--debug' in sys.argv

DEBUG_TEMPLATEPARAMS = r'''
import sys
import json
import traceback
import re

sys.path.insert(0, 'bundle.zip')

import prog_questions
from prog_questions.QuestionBase import QuestionBase

namespace = {{k: v for k, v in vars(prog_questions).items() if not k.startswith('__')}}
namespace['__name__'] = 'prog_questions.debug_module'
namespace['__package__'] = 'prog_questions'
namespace['QuestionBase'] = QuestionBase
namespace['__builtins__'] = __builtins__

CLASS_SOURCE = """{class_source}"""
TARGET_CLASS_NAME = "{class_name}"

CLASS_SOURCE = re.sub(r'from\s+\.+([\w\.]+)', r'from prog_questions.\1', CLASS_SOURCE)
CLASS_SOURCE = re.sub(r'from\s+\.+\s+import', r'from prog_questions import', CLASS_SOURCE)

try:
    compiled = compile(CLASS_SOURCE, 'prog_questions/debug_module.py', 'exec')
    exec(compiled, namespace)

    DebugClass = namespace.get(TARGET_CLASS_NAME)

    if DebugClass is None or not (isinstance(DebugClass, type) and issubclass(DebugClass, QuestionBase)):
        raise ValueError(f"Класс {{TARGET_CLASS_NAME}} не найден или не наследует QuestionBase")

    import sys as _sys
    import inspect

    argvData = {{p.split('=')[0]: p.split('=')[1] for p in _sys.argv[1:] if '=' in p}}

    sig = inspect.signature(DebugClass.__init__)
    valid_params = sig.parameters.keys()

    kwargs = {{}}
    for k, v in argvData.items():
        if k in valid_params:
            if k == 'seed':
                kwargs[k] = int(v)
            elif k == 'is_simple_task':
                kwargs[k] = v.lower() in ('true', '1', 'yes')
            else:
                kwargs[k] = v

    if 'seed' not in kwargs:
        kwargs['seed'] = 42

    question = DebugClass(**kwargs)

    params_dict = json.loads(question.getTemplateParameters())
    params_dict['DEBUG_SOURCE'] = CLASS_SOURCE
    print(json.dumps(params_dict))

except SyntaxError as e:
    error_msg = f'Строка {{e.lineno}}: {{e.msg}}\n{{e.text}}'
    print(json.dumps({{
        'QUESTION_TEXT': f'<h4 style="color:red">Синтаксическая ошибка</h4><pre>{{error_msg}}</pre>',
        'PRELOADED_CODE': '',
        'SEED': 42,
        'PARAMETERS': '{{}}',
        'DEBUG_SOURCE': CLASS_SOURCE
    }}))

except Exception:
    print(json.dumps({{
        'QUESTION_TEXT': f'<h4 style="color:red">Ошибка</h4><pre>{{traceback.format_exc()}}</pre>',
        'PRELOADED_CODE': '',
        'SEED': 42,
        'PARAMETERS': '{{}}',
        'DEBUG_SOURCE': CLASS_SOURCE
    }}))
'''

code_template = r'''import sys
sys.path.insert(0, 'bundle.zip')
from {module_path} import {class_name}

question = {class_name}.initWithParameters("""{{{{ PARAMETERS | e('py') }}}}""")
print(question.runTest("""{{{{ STUDENT_ANSWER | e('py') }}}}"""))
'''

debug_code_template = r'''import sys
import re
sys.path.insert(0, 'bundle.zip')

import prog_questions
from prog_questions.QuestionBase import QuestionBase

namespace = {{k: v for k, v in vars(prog_questions).items() if not k.startswith('__')}}
namespace['__name__'] = 'prog_questions.debug_module'
namespace['__package__'] = 'prog_questions'
namespace['QuestionBase'] = QuestionBase
namespace['__builtins__'] = __builtins__

CLASS_SOURCE = """{{{{ DEBUG_SOURCE | e('py') }}}}"""
CLASS_SOURCE = re.sub(r'from\s+\.+([\w\.]+)', r'from prog_questions.\1', CLASS_SOURCE)
CLASS_SOURCE = re.sub(r'from\s+\.+\s+import', r'from prog_questions import', CLASS_SOURCE)

compiled = compile(CLASS_SOURCE, 'prog_questions/debug_module.py', 'exec')
exec(compiled, namespace)
DebugClass = namespace.get("{class_name}")

question = DebugClass.initWithParameters("""{{{{ PARAMETERS | e('py') }}}}""")
print(question.runTest("""{{{{ STUDENT_ANSWER | e('py') }}}}"""))
'''


# Класс извлечения узла аргументов из конструктора класса и имени задачи
class InternalQuestionDataExtractor(ast.NodeVisitor):
    def visit_FunctionDef(self, node):
        if node.name != '__init__':
            return
        self.arguments_node = node.args

    def visit_Assign(self, node):
        if len(node.targets) < 1 or not isinstance(node.targets[0], ast.Name) or node.targets[0].id != 'questionName' or not isinstance(node.value, ast.Constant):
            return
        self.question_name = node.value.value

    def visit_AnnAssign(self, node):
        if not isinstance(node.target, ast.Name) or node.target.id != 'questionName' or not isinstance(node.value, ast.Constant):
            return
        self.question_name = node.value.value

    def extract(self, node: ast.AST) -> tuple[ast.arguments | None, str | None]:
        self.arguments_node = None
        self.question_name = None
        self.visit(node)
        return self.arguments_node, self.question_name

# Класс извлечения названия класса и узла аргументов конструктора класса для потомков QuestionBase
class QuestionDataExtractor(ast.NodeVisitor):
    def visit_ClassDef(self, node):
        if self.class_name:
            return

        is_question_class = False
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == 'QuestionBase':
                is_question_class = True
            elif isinstance(base, ast.Attribute) and base.attr == 'QuestionBase':
                is_question_class = True

        if not is_question_class:
            return

        self.class_name = node.name
        arguments_extractor = InternalQuestionDataExtractor()
        self.arguments_node, self.question_name = arguments_extractor.extract(node)

    def extract(self, node: ast.AST) -> tuple[str | None, ast.arguments | None, str | None]:
        self.class_name = None
        self.arguments_node = None
        self.question_name = None
        self.visit(node)
        return self.class_name, self.arguments_node, self.question_name


if __name__ == '__main__':
    # Очистка папки вывода
    if BUILD_DEBUG:
        if OUTPUT_DEBUG_PATH.exists():
            shutil.rmtree(OUTPUT_DEBUG_PATH)
        OUTPUT_DEBUG_PATH.mkdir(parents=True, exist_ok=True)
    else:
        if OUTPUT_PATH.exists():
            for file in OUTPUT_PATH.iterdir():
                if file == OUTPUT_DEBUG_PATH:
                    continue
                if file.is_dir():
                    shutil.rmtree(file)
                else:
                    file.unlink()
        else:
            OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    # Получение base64 от zip-архива всех файлов проекта
    sources = [*SOURCE_PATH.glob('**/*.py')]
    bundle_tempfile = tempfile.NamedTemporaryFile(delete=False)

    with zipfile.ZipFile(bundle_tempfile.name, 'w', zipfile.ZIP_DEFLATED) as bundle_file:
        for file in sources:
            bundle_file.write(file, file.relative_to(SOURCE_PATH))

    with open(bundle_tempfile.name, 'rb') as f:
        bundle_base64 = base64.b64encode(f.read()).decode('ascii')

    bundle_tempfile.close()
    os.unlink(bundle_tempfile.name)

    # Загрузка xml-шаблона задачи и создание записи об zip-архиве
    with XML_TEMPLATE_PATH.open('r', encoding='utf-8') as xml_file:
        xml_parser = xml.XMLParser(strip_cdata=False)
        xml_template = xml.parse(xml_file, xml_parser)

    xml_template.xpath('//file')[0].text = bundle_base64

    # Шаблон параметров для initTemplate
    parameters_code_template = r'''import sys
sys.path.insert(0, 'bundle.zip')
from {module_path} import {class_name}

question = {constructor_code}
print(question.getTemplateParameters())
'''

    # Проверка для всех файлов проекта
    for file in sources:
        question_class, question_arguments, question_name = QuestionDataExtractor().extract(ast.parse(file.read_text(encoding='utf-8')))

        if question_class is None:
            continue

        rel_path = file.relative_to(SOURCE_PATH)
        sub_path = rel_path.parent.relative_to('prog_questions')

        if BUILD_DEBUG:
            source_code = file.read_text(encoding='utf-8')
            escaped_source = source_code.replace('\\', '\\\\').replace('"""', '\\"\\"\\"')

            debug_templateparams = DEBUG_TEMPLATEPARAMS.format(
                class_source=escaped_source,
                class_name=question_class
            ).lstrip()
            
            debug_code = debug_code_template.format(
                class_name=question_class
            ).lstrip()

            debug_xml = copy.deepcopy(xml_template)
            debug_xml.xpath('//templateparams')[0].text = xml.CDATA(debug_templateparams)
            
            debug_xml.xpath('//template')[0].text = xml.CDATA(debug_code)
            
            folder_context = "autumn" if str(sub_path) == "." else str(sub_path)
            debug_moodle_name = f'[DEBUG] {folder_context} - {question_name}'
            debug_xml.xpath('//question/name/text')[0].text = xml.CDATA(debug_moodle_name)

            debug_output_dir = OUTPUT_DEBUG_PATH / sub_path
            debug_output_dir.mkdir(parents=True, exist_ok=True)
            
            debug_output_path = debug_output_dir / f'{question_class}_debug.xml'
            debug_xml.write(debug_output_path, xml_declaration=True, encoding='utf-8')
        else:
            module_path = '.'.join(rel_path.parent.parts)
            keywords = [ast.keyword(arg='seed', value=ast.Constant(value=Ellipsis))]
            if question_arguments is not None:
                for kw_name, kw_value in zip(question_arguments.kwonlyargs, question_arguments.kw_defaults):
                    if kw_name.arg == 'seed':
                        continue

                    keywords.append(ast.keyword(arg=kw_name.arg, value=kw_value))

            call_node = ast.Call(func=ast.Attribute(value=ast.Name(id=question_class), attr='initTemplate'), args=[], keywords=keywords)
            constructor_code = ast.unparse(call_node).rstrip()

            parameters_code = parameters_code_template.format(module_path=module_path, class_name=question_class, constructor_code=constructor_code).lstrip()
            code = code_template.format(module_path=module_path, class_name=question_class).lstrip()

            current_xml = copy.deepcopy(xml_template)
            current_xml.xpath('//question/name/text')[0].text = xml.CDATA(question_name)
            current_xml.xpath('//templateparams')[0].text = xml.CDATA(parameters_code)
            current_xml.xpath('//template')[0].text = xml.CDATA(code)

            xml_output_dir = OUTPUT_PATH / sub_path
            xml_output_dir.mkdir(parents=True, exist_ok=True)
            xml_output_path = xml_output_dir / f'{question_class}.xml'
            current_xml.write(xml_output_path, xml_declaration=True, encoding='utf-8')

    mode = "DEBUG" if BUILD_DEBUG else "BASIC"
    print(f"Задачи успешно собраны в режиме {mode}:")
    base_to_print = OUTPUT_DEBUG_PATH if BUILD_DEBUG else OUTPUT_PATH
    for built_file in sorted(base_to_print.glob('**/*.xml')):
        print(built_file.relative_to(base_to_print))