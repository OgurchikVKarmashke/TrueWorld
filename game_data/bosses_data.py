# bosses_data.py
"""
Данные боссов с новыми характеристиками.
"""

BOSS_STATS = {
    "Древний Дракон": {
        "base_stats": {
            "strength": 30,
            "dexterity": 10,
            "constitution": 25,
            "intelligence": 20
        },
        "growth_per_level": {
            "strength": 2.5,
            "dexterity": 0.8,
            "constitution": 2.0,
            "intelligence": 1.5
        },
        "exp_multiplier": 5.0,
        "min_level": 10,
        "description": "Древнее могущественное существо"
    },
    "Повелитель Теней": {
        "base_stats": {
            "strength": 22,
            "dexterity": 18,
            "constitution": 20,
            "intelligence": 25
        },
        "growth_per_level": {
            "strength": 1.8,
            "dexterity": 1.5,
            "constitution": 1.6,
            "intelligence": 2.0
        },
        "exp_multiplier": 4.5,
        "min_level": 15,
        "description": "Владыка темных сил"
    },
    "Король Лич": {
        "base_stats": {
            "strength": 18,
            "dexterity": 12,
            "constitution": 22,
            "intelligence": 28
        },
        "growth_per_level": {
            "strength": 1.5,
            "dexterity": 1.0,
            "constitution": 1.8,
            "intelligence": 2.2
        },
        "exp_multiplier": 4.0,
        "min_level": 20,
        "description": "Бессмертный владыка нежити"
    }
}

# Теперь способности описаны в отдельном файле
# BOSS_ABILITIES перенесен в skills/boss_skills.py