from pathlib import Path
import shutil
import tempfile
import zipfile
import base64
import os
import lxml.etree as xml
import ast
import astor


# Константы
ROOT = Path(__file__).resolve().parent.parent
SOURCE_PATH = ROOT / 'src'
OUTPUT_PATH = ROOT / 'dist'
XML_TEMPLATE_PATH = ROOT / 'build' / 'template.xml'


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

    def extract(self, node: ast.AST) -> ast.arguments | None:
        self.arguments_node = None
        self.question_name = None
        self.visit(node)
        return self.arguments_node, self.question_name

# Класс извлечения названия класса и узла аргументов конструктора класса для потомков QuestionBase
class QuestionDataExtractor(ast.NodeVisitor):
    def visit_ClassDef(self, node):
        if self.class_name or not any(base.id == 'QuestionBase' for base in node.bases):
            return

        self.class_name = node.name

        arguments_extractor = InternalQuestionDataExtractor()
        self.arguments_node, self.question_name = arguments_extractor.extract(node)

    def extract(self, node: ast.AST) -> tuple[str | None, ast.arguments | None]:
        self.class_name = None
        self.arguments_node = None
        self.question_name = None
        self.visit(node)
        return self.class_name, self.arguments_node, self.question_name


if __name__ == '__main__':
    # Очистка папки вывода
    if OUTPUT_PATH.exists():
        for file in OUTPUT_PATH.iterdir():
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


    # Шаблоны кода, внедряемого в xml-файл
    parameters_code_template = r'''import sys
sys.path.insert(0, 'bundle.zip')
from {module_path} import {class_name}

question = {constructor_code}
print(question.getTemplateParameters())
    '''

    code_template = r'''import sys
sys.path.insert(0, 'bundle.zip')
from {module_path} import {class_name}

question = {class_name}.initWithParameters("""{{{{ PARAMETERS | e('py') }}}}""")
print(question.runTest("""{{{{ STUDENT_ANSWER | e('py') }}}}"""))
    '''


    # Проверка для всех файлов проекта
    for file in sources:
        # Получение информации о классе задачи из файла
        question_class, question_arguments, question_name = QuestionDataExtractor().extract(ast.parse(file.read_text(encoding='utf-8')))

        # Если в файле нет класса задачи - пропускаем
        if question_class is None:
            continue

        # Вычисляем путь модуля из расположения файла (например, prog_questions.spring)
        rel_path = file.relative_to(SOURCE_PATH)
        module_path = '.'.join(rel_path.parent.parts)

        # Конвертация узла arguments в массив keyword
        keywords = [ast.keyword(arg='seed', value=ast.Constant(value=Ellipsis))]

        if question_arguments is not None:
            for kw_name, kw_value in zip(question_arguments.kwonlyargs, question_arguments.kw_defaults):
                if kw_name.arg == 'seed':
                    continue

                kw_name.annotation = None
                keywords.append(ast.keyword(arg=kw_name, value=kw_value))

        # Создание куска кода с вызовом initTemplate со стандартными параметрами (полученными из кода конструктора)
        call_node = ast.Call(func=ast.Attribute(value=ast.Name(id=question_class), attr='initTemplate'), args=[], keywords=keywords)
        constructor_code = astor.to_source(call_node).rstrip()

        # Подстановка в шаблоны кода
        parameters_code = parameters_code_template.format(module_path=module_path, class_name=question_class, constructor_code=constructor_code).lstrip()
        code = code_template.format(module_path=module_path, class_name=question_class).lstrip()

        # Модификация xml-шаблона
        xml_template.xpath('//question/name/text')[0].text = xml.CDATA(question_name)
        xml_template.xpath('//templateparams')[0].text = xml.CDATA(parameters_code)
        xml_template.xpath('//template')[0].text = xml.CDATA(code)

        # Путь вывода: подпакеты (кроме prog_questions) становятся подпапками dist/
        sub_path = rel_path.parent.relative_to('prog_questions')
        xml_output_dir = OUTPUT_PATH / sub_path
        xml_output_dir.mkdir(parents=True, exist_ok=True)
        xml_output_path = xml_output_dir / f'{question_class}.xml'
        xml_template.write(xml_output_path, xml_declaration=True, encoding='utf-8')

    # Вывод информации о собранных задачах
    print("Задачи успешно собраны:")
    for built_file in sorted(OUTPUT_PATH.glob('**/*.xml')):
        print(built_file.relative_to(OUTPUT_PATH))
