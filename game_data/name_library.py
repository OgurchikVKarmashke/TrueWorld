# name_library.py
import random

# РАСШИРЕННЫЙ СПИСОК КОРЕЙСКИХ ФАМИЛИЙ
SURNAMES = [
    "Ким", "Ли", "Пак", "Чон", "Кан", "Чо", "Юн", "Чан", "Им", "Син",
    "Со", "Хан", "Сон", "Рю", "Бэк", "Квон", "Хван", "Ан", "Сок", "Мин",
    "О", "Нам", "Тхэ", "Хон", "Дан", "Пэк", "Сим", "Ём", "Джи", "Рим",
    "То", "Ма", "Пан", "Сан", "Тан", "Чин", "Хём", "Ян", "Ван", "Лим"
]

# РАСШИРЕННЫЙ СПИСОК КОРЕЙСКИХ СЛОГОВ
MALE_SYLLABLES = [
    "Хён", "Мин", "Джун", "Су", "Хо", "Вон", "Сок", "Хван", "Чан", "Сон",
    "Дин", "Гю", "Бом", "Дэ", "Джин", "Тхэ", "Ки", "Сан", "Ён", "Хви",
    "Джэ", "Сын", "Иль", "Хи", "Гон", "Бин", "Дук", "Хан", "Син", "Чхоль"
]

FEMALE_SYLLABLES = [
    "Хи", "Ми", "На", "Ри", "А", "Ин", "Ё", "Джа", "Сы", "Ха",
    "Ын", "Чжи", "Ён", "Су", "Ли", "Си", "Бо", "Ра", "Дан", "Хва",
    "Чин", "Сун", "Ок", "Хэ", "Вон", "Джу", "Мён", "Сон", "Хян", "Гён"
]

NEUTRAL_SYLLABLES = [
    "Вон", "Сок", "Хён", "Мин", "Джун", "Су", "Хо", "Чан", "Сон", "Дин",
    "Гю", "Бом", "Дэ", "Джин", "Тхэ", "Сан", "Ён", "Хви", "Джэ", "Сын"
]

def generate_korean_name(gender=None):
    """Генерирует случайное корейское имя с учетом пола"""
    surname = random.choice(SURNAMES)
    
    if gender is None:
        gender = random.choice(['male', 'female'])
    
    if gender == 'male':
        syllables = MALE_SYLLABLES
    else:
        syllables = FEMALE_SYLLABLES
    
    # 70% - два слога, 30% - один слог
    if random.random() < 0.7:
        name_part1 = random.choice(syllables)
        name_part2 = random.choice(syllables)
        # Убедимся, что слоги разные
        while name_part2 == name_part1:
            name_part2 = random.choice(syllables)
        return f"{surname} {name_part1} {name_part2}"
    else:
        return f"{surname} {random.choice(syllables)}"

def generate_korean_name_with_meaning():
    """Генерирует имя со значением"""
    surname = random.choice(SURNAMES)
    
    # Списки слогов со значениями
    meaningful_syllables = {
        "Хён": "мудрый", "Мин": "яркий", "Джун": "правдивый",
        "Су": "долговечный", "Хо": "хороший", "Вон": "первый",
        "Сок": "камень", "Хи": "радость", "Ми": "красота",
        "На": "река", "Ри": "разум", "А": "ребенок"
    }
    
    syllable1, meaning1 = random.choice(list(meaningful_syllables.items()))
    syllable2, meaning2 = random.choice(list(meaningful_syllables.items()))
    
    return f"{surname} {syllable1}{syllable2} ({meaning1}-{meaning2})"