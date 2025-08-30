# game_data/tower_rewards.py
from typing import Dict, List
from systems.items_system import ItemRarity

# Таблица наград за этажи башни
TOWER_FLOOR_REWARDS = {
    # Обычные этажи (1-4, 6-9, etc)
    **{floor: {
        "gold": floor * 25,
        "crystals": max(1, floor // 3),
        "items": {
            "iron_ore": (1, 3),  # item_id: (min_quantity, max_quantity)
        }
    } for floor in range(1, 100) if floor % 5 != 0},
    
    # Босс-этажи (каждый 5-й этаж)
    **{floor: {
        "gold": floor * 50,
        "crystals": max(3, floor // 2),
        "items": {
            "iron_ore": (2, 5),
            "steel_bar": (1, 2),
        }
    } for floor in range(5, 100, 5)},
    
    # Особые этажи (10, 20, 30...)
    **{floor: {
        "gold": floor * 75,
        "crystals": max(5, floor),
        "items": {
            "iron_ore": (3, 7),
            "steel_bar": (2, 4),
            "magic_crystal": (1, 2),
        }
    } for floor in range(10, 100, 10)},
    
    # Легендарные этажи (25, 50, 75, 100)
    **{floor: {
        "gold": floor * 100,
        "crystals": max(10, floor * 2),
        "items": {
            "iron_ore": (5, 10),
            "steel_bar": (3, 6),
            "magic_crystal": (2, 4),
            "iron_sword": (1, 1),  # Шанс получить готовое оружие
        }
    } for floor in [25, 50, 75, 100]},
}

# Дополнительные бонусные награды за определенные этажи
SPECIAL_REWARDS = {
    5: {"unlocks": ["steel_bar_recipe"]},
    10: {"unlocks": ["magic_crystal_recipe"]},
    15: {"unlocks": ["iron_sword_recipe"]},
    20: {"unlocks": ["steel_sword_recipe"]},
}

def get_floor_rewards(floor_number: int) -> Dict:
    """Возвращает награды для указанного этажа"""
    base_rewards = TOWER_FLOOR_REWARDS.get(floor_number, {
        "gold": floor_number * 20,
        "crystals": max(1, floor_number // 4),
        "items": {"iron_ore": (1, 2)}
    })
    
    # Добавляем специальные награды если есть
    if floor_number in SPECIAL_REWARDS:
        base_rewards.update(SPECIAL_REWARDS[floor_number])
    
    return base_rewards

def generate_item_rewards(items_dict: Dict) -> Dict:
    """Генерирует конкретные количества предметов"""
    rewards = {}
    for item_id, (min_qty, max_qty) in items_dict.items():
        quantity = random.randint(min_qty, max_qty)
        rewards[item_id] = quantity
    return rewards