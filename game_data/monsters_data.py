# monsters_data.py

"""
Данные обычных монстров с новыми характеристиками (сила, ловкость, выносливость, интеллект)
"""

# Базовые характеристики монстров на 1 уровне
MONSTER_BASE_STATS = {
    "Гоблин": {
        "base_stats": {
            "strength": 8,
            "dexterity": 12,
            "constitution": 6,
            "intelligence": 4
        },
        "growth_per_level": {
            "strength": 0.8,
            "dexterity": 1.2,
            "constitution": 0.6,
            "intelligence": 0.4
        },
        "description": "Мелкий, зелёный и противный"
    },
    "Скелет": {
        "base_stats": {
            "strength": 7,
            "dexterity": 10,
            "constitution": 8,
            "intelligence": 3
        },
        "growth_per_level": {
            "strength": 0.7,
            "dexterity": 1.0,
            "constitution": 0.8,
            "intelligence": 0.3
        },
        "description": "Восставший мертвец"
    },
    "Орк": {
        "base_stats": {
            "strength": 15,
            "dexterity": 6,
            "constitution": 12,
            "intelligence": 2
        },
        "growth_per_level": {
            "strength": 1.5,
            "dexterity": 0.6,
            "constitution": 1.2,
            "intelligence": 0.2
        },
        "description": "Большой и сильный"
    },
    "Паук": {
        "base_stats": {
            "strength": 5,
            "dexterity": 15,
            "constitution": 5,
            "intelligence": 1
        },
        "growth_per_level": {
            "strength": 0.5,
            "dexterity": 1.5,
            "constitution": 0.5,
            "intelligence": 0.1
        },
        "description": "Ядовитое насекомое"
    },
    "Волк": {
        "base_stats": {
            "strength": 9,
            "dexterity": 14,
            "constitution": 8,
            "intelligence": 2
        },
        "growth_per_level": {
            "strength": 0.9,
            "dexterity": 1.4,
            "constitution": 0.8,
            "intelligence": 0.2
        },
        "description": "Быстрый хищник"
    }
}

# Вероятности появления монстров на разных этажах
MONSTER_SPAWN_CHANCES = {
    1: {"Гоблин": 70, "Скелет": 30},
    2: {"Гоблин": 50, "Скелет": 40, "Волк": 10},
    3: {"Гоблин": 30, "Скелет": 40, "Волк": 20, "Паук": 10},
    4: {"Скелет": 30, "Орк": 30, "Волк": 20, "Паук": 20},
    5: {"Орк": 40, "Скелет": 30, "Волк": 20, "Паук": 10}
}

# Количество монстров на этаже
MONSTER_COUNT_BY_FLOOR = {
    1: (1, 2),
    2: (1, 3),
    3: (2, 3),
    4: (2, 4),
    5: (3, 4),
    6: (3, 5),
    7: (4, 5),
    8: (4, 6),
    9: (5, 6),
    10: (1, 1)  # босс
}