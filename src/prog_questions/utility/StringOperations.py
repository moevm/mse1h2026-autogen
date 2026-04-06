import argparse
import random
from faker import Faker

VOWELS = 'AEIOUY'
CONSONANTS = 'BCDFGHJKLMNPQRSTVWXZ'

fake = Faker()


class StringOperation:
    # Базовый класс для операций над строками
    def __init__(self):
        pass

    def apply(self, s):
        # Применение операции к строке
        pass

    def get_text(self):
        # Получение текстового описания операции
        pass

    def good_example(self):
        # Генерация примера, где операция дает видимый результат
        pass

    def bad_example(self):
        # Генерация примера, где операция не меняет строку
        pass


class DigitModuloStringOperation(StringOperation):
    # Замена цифр на остаток от деления на случайное число
    def __init__(self):
        self.divisor = random.randint(2, 9)

    def apply(self, s):
        return ''.join(map(lambda x: str(int(x) % self.divisor) if x in '0123456789' else x, s))

    def get_text(self):
        return f"Замените все цифры в строке остатками их деления на {self.divisor}"

    def good_example(self):
        good_digits = list(map(str, range(self.divisor, 10)))
        bad_digits = list(map(str, range(0, self.divisor)))

        s = list(random.choices(good_digits, k=random.randint(1, 2)))
        s += list(random.choices(bad_digits, k=random.randint(1, 2)))
        random.shuffle(s)
        return ''.join(s)

    def bad_example(self):
        bad_digits = list(map(str, range(0, self.divisor)))
        return ''.join(random.choices(bad_digits, k=random.randint(2, 4)))


class CaseStringOperation(StringOperation):
    # Смена регистра у гласных или согласных букв
    def __init__(self):
        self.is_upper = random.choice([True, False])
        self.is_vowel = random.choice([True, False])

    def apply_to_char(self, s):
        return s.upper() if self.is_upper else s.lower()

    def apply(self, s):
        letters = VOWELS if self.is_vowel else CONSONANTS
        return ''.join(map(lambda x: self.apply_to_char(x) if x.upper() in letters else x, s))

    def get_text(self):
        letters = ''
        if self.is_vowel:
            letters = f'гласные {str(list(VOWELS))}'
        else:
            letters = f'согласные {str(list(CONSONANTS))}'
        target = 'верхний' if self.is_upper else 'нижний'
        return f"Перевести все {letters} в {target} регистр"

    def good_example(self):
        word = list(fake.word().upper())
        vowel_cnt = False
        consonant_cnt = False
        for i in range(len(word)):
            if word[i] in VOWELS:
                vowel_cnt = not vowel_cnt
                word[i] = word[i].lower() if vowel_cnt else word[i]
            elif word[i] in CONSONANTS:
                consonant_cnt = not consonant_cnt
                word[i] = word[i].lower() if consonant_cnt else word[i]
        return ''.join(word)

    def bad_example(self):
        word = fake.word()
        return word.upper() if random.choice([True, False]) else word


class UnderscoreStringOperation(StringOperation):
    # Замена пробелов на количество символов '_'
    def __init__(self):
        self.threshold = random.randint(5, 9)
        self.divisor = random.randint(self.threshold, 15)

    def apply(self, s):
        cnt = s.count('_')
        cnt = str(cnt if cnt <= self.threshold else cnt % self.divisor)
        return s.replace(' ', cnt)

    def get_text(self):
        return f"Замените каждый пробел на число символов “_” в исходной строке. Если число больше " \
            f"{self.threshold}, то укажите его остаток от деления на {self.divisor}"

    def good_example(self):
        return '_' * random.randint(1, 2)

    def bad_example(self):
        return self.good_example()


class ReplaceSubstringStringOperation(StringOperation):
    # Замена всех схождений одной подстроки на другую
    def __init__(self):
        self.old = fake.random_uppercase_letter() * random.randint(2, 4)
        self.new = fake.random_uppercase_letter() * random.randint(2, 4)

    def apply(self, s):
        return s.replace(self.old, self.new)

    def get_text(self):
        return f"Замените все подстроки {self.old} на подстроки {self.new}"

    def good_example(self):
        if random.choice([True, False]):
            return self.old * random.randint(1, 2) + self.old[0] * random.randrange(1, len(self.old))
        return self.new * random.randint(1, 4)

    def bad_example(self):
        if random.choice([True, False]):
            return self.old[0] * random.randrange(1, len(self.old))
        return self.new * random.randint(1, 4)


STRING_OPERATIONS = StringOperation.__subclasses__()


def generate_input_string(operations, min_length, max_length):
    # Генерация тестовой строки заданной длины
    target_length = random.randint(min_length, max_length)
    s = ''
    while len(s) <= target_length:
        if s and random.randint(1, 2) == 1:
            s += ' '

        operation = random.choice(operations)
        add = operation.bad_example() if (random.randint(1, 3) == 1) else operation.good_example()
        if (len(s) + len(add)) > target_length:
            break
        s += add
    return s


def apply_operations(string, operations):
    # Последовательное применение операций к строке
    for operation in operations:
        string = operation.apply(string)
    return string


def generate_operations(seed, num_operations):
    # Генерация списка случайных операций
    random.seed(seed)
    Faker.seed(seed)
    operations = list(map(lambda x: x(), random.sample(
        STRING_OPERATIONS, num_operations)))
    random.shuffle(operations)
    return operations


def generate_text(operations):
    # Генерация текста задания
    text = ''
    for i, operation in enumerate(operations):
        text += f"{i + 1}. {operation.get_text()}\n"
    return text
