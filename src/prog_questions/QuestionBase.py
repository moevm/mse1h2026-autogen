from abc import ABC, abstractmethod
from typing import final
from dataclasses import dataclass
from types import EllipsisType
import sys
import json
from .utility import CommentMetric, CompilationError, EnvironmentError, InternalError


@final
class Result(ABC):
    @dataclass(frozen=True)
    class Ok:
        '''
        Успешный результат запуска проверки кода
        '''
        pass

    @dataclass(frozen=True)
    class Fail:
        '''
        Тест-кейс не пройден во время проверки кода.

        '''
        input: str
        '''
        Входные данные
        '''
        expected: str
        '''
        Ожидаемый вывод
        '''
        got: str
        '''
        Полученный вывод
        '''


class QuestionBase(ABC):
    questionName: str = ''
    '''
    Название вопроса
    '''

    def __init__(self, *, seed: int, **parameters):
        self.seed = seed
        self.parameters = parameters

    @classmethod
    def initTemplate(cls, *, seed: int | EllipsisType | None = None, **parameters):
        '''
        Инициализация в параметрах шаблона Twig
        seed - сид вопроса. Если равен None или Ellipsis, то берётся тот, что предоставляет Moodle.
        parameters - любые параметры, необходимые для настройки (сложность, въедливость и т.п.).
        Ввиду особенностей coderunner и простоты реализации, параметры могут быть типами,
        поддерживающимися JSON (int, float, str, bool, None, array, dict)
        '''
        if seed is None or seed is Ellipsis:
            argvData = { parameter.split('=')[0]: parameter.split('=')[1] for parameter in sys.argv[1:] }
            seed = int(argvData['seed'])

        return cls(seed=seed, **parameters)

    @classmethod
    def initWithParameters(cls, parameters: str):
        '''
        Инициализация в основном шаблоне, после инициализации параметров шаблона Twig.
        Подразумевается использование только в связке с Twig параметром PARAMETERS.
        '''
        return cls(**json.loads(parameters))

    def getTemplateParameters(self) -> str:
        '''
        Возвращает параметры в формате JSON для шаблонизатора Twig
        '''
        return json.dumps({
            'QUESTION_TEXT': self.questionText,
            'PRELOADED_CODE': self.preloadedCode,
            'SEED': self.seed,
            'PARAMETERS': json.dumps(self.parameters | { 'seed': self.seed }),
        })

    @property
    @abstractmethod
    def questionText(self) -> str:
        '''
        Задание/текст вопроса
        '''
        ...

    @property
    @abstractmethod
    def preloadedCode(self) -> str:
        '''
        Код, который подгружается в поле редактирования кода
        '''
        ...

    @abstractmethod
    def test(self, code: str) -> Result.Ok | Result.Fail:
        '''
        Логика проверки кода
        code - код, отправленный студентом на проверку
        Возвращаемое значение - Result.Ok - всё хорошо, Result.Fail - не прошёл тест-кейс
        Вызывает исключения: CompilationError, InternalError, EnvironmentError
        '''
        ...

    def runTest(self, code: str) -> str:
        '''
        Запуск проверки кода и подсчёта процента коментариев в коде
        code - код, отправленный студентом на проверку
        Возвращаемое значение - JSON в виде строки для отображения результата шаблону-комбинатору
        '''

        success = False
        output = {}

        try:
            result = self.test(code)
            success = result == Result.Ok()

            if success:
                output['prologuehtml'] = '<h4>Всё хорошо</h4>'
                #commentsPercent = CommentMetric(code).get_comment_percentage()
                #output['epiloguehtml'] = f'<p>Процент комментариев: {commentsPercent}%</p>'
            else:
                output['prologuehtml'] = '<h4>Тесты не пройдены</h4>'
                output['testresults'] = [['iscorrect', 'Ввод', 'Ожидаемый', 'Получено', 'iscorrect'], [success, result.input, result.expected, result.got, success]]

        except CompilationError as e:
            output['prologuehtml'] = f"<h4>Ошибка компиляции</h4><p>{str(e).replace(chr(10),'<br>')}</p>"

        except (InternalError, EnvironmentError) as e:
            output['prologuehtml'] = f'<h4>Ошибка сервера (попробуйте позже)</h4><p style="font-family: monospace;">{str(e)}</p>'

        except Exception:
            output['prologuehtml'] = f'<h4>Ошибка задания</h4><p>Пожалуйста, свяжитесь с преподавателем (seed задания: {self.seed})</p>'

        output['fraction'] = 1.0 if success else 0.0
        return json.dumps(output)
