# monsters_data.py
MONSTER_BASE_STATS = {
    "Гоблин": {
        "health_per_level": 8,
        "attack_per_level": 2,
        "defense_per_level": 1,
        "exp_per_level": 10,
        "description": "Мелкий и противный человечек"
    },
    "Скелет": {
        "health_per_level": 7,
        "attack_per_level": 3,
        "defense_per_level": 2,
        "exp_per_level": 12,
        "description": "Восставший мертвец"
    },
    "Орк": {
        "health_per_level": 12,
        "attack_per_level": 4,
        "defense_per_level": 1,
        "exp_per_level": 15,
        "description": "Большой и сильный"
    },
    "Паук": {
        "health_per_level": 6,
        "attack_per_level": 3,
        "defense_per_level": 0,
        "exp_per_level": 8,
        "description": "Ядовитое насекомое"
    },
    "Волк": {
        "health_per_level": 9,
        "attack_per_level": 3,
        "defense_per_level": 1,
        "exp_per_level": 11,
        "description": "Быстрый хищник"
    }
}

# Боссы
BOSS_STATS = {
    "Древний Дракон": {
        "health_multiplier": 3.0,
        "attack_multiplier": 2.5,
        "defense_multiplier": 2.0,
        "exp_multiplier": 5.0,
        "min_level": 10
    },
    "Повелитель Теней": {
        "health_multiplier": 2.8,
        "attack_multiplier": 2.7,
        "defense_multiplier": 1.8,
        "exp_multiplier": 4.5,
        "min_level": 15
    },
    "Король Лич": {
        "health_multiplier": 2.5,
        "attack_multiplier": 2.3,
        "defense_multiplier": 2.2,
        "exp_multiplier": 4.0,
        "min_level": 20
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
    1: (1, 2),    # мин, макс
    2: (1, 3),
    3: (2, 3),
    4: (2, 4),
    5: (3, 4),
    6: (3, 5),
    7: (4, 5),
    8: (4, 6),
    9: (5, 6),
    10: (1, 1)    # босс
}