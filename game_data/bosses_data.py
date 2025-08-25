# bosses_data.py
BOSS_ABILITIES = {
    "Древний Дракон": {
        "Огненное дыхание": {
            "chance": 0.3,
            "damage_multiplier": 1.8,
            "description": "Сжигает всех героев"
        },
        "Хвостовой удар": {
            "chance": 0.2,
            "damage_multiplier": 1.5,
            "stun_chance": 0.4,
            "description": "Оглушает цель"
        }
    },
    "Повелитель Теней": {
        "Теневой клинок": {
            "chance": 0.4,
            "damage_multiplier": 1.6,
            "description": "Проходит сквозь защиту"
        },
        "Призыв теней": {
            "chance": 0.25,
            "summon_count": 2,
            "description": "Призывает помощников"
        }
    }
}