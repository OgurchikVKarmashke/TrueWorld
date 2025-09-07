# game_data.tower_rewards.py
from systems.items_system import ItemRarity
from typing import Dict, List
import random

# Таблица наград за этажи башни
TOWER_FLOOR_REWARDS = {
    # Обычные этажи (1-4, 6-9, etc)
    **{floor: {
        "gold": floor * 80,  # Было 25, стало 80
        "crystals": max(1, floor // 2),  # Было //3, стало //2
        "items": {
            "iron_ore": (1, 3),
        }
    } for floor in range(1, 100) if floor % 5 != 0},
    
    # Босс-этажи (каждый 5-й этаж)
    **{floor: {
        "gold": floor * 150,  # Было 50, стало 150
        "crystals": max(3, floor),  # Было //2, стало просто floor
        "items": {
            "iron_ore": (2, 5),
            "steel_bar": (1, 2),
        }
    } for floor in range(5, 100, 5)},
    
    # Особые этажи (10, 20, 30...)
    **{floor: {
        "gold": floor * 250,  # Было 75, стало 250
        "crystals": max(5, floor * 2),  # Было floor, стало floor*2
        "items": {
            "iron_ore": (3, 7),
            "steel_bar": (2, 4),
            "magic_crystal": (1, 2),
        }
    } for floor in range(10, 100, 10)},
    
    # Легендарные этажи (25, 50, 75, 100)
    **{floor: {
        "gold": floor * 400,  # Было 100, стало 400
        "crystals": max(10, floor * 3),  # Было *2, стало *3
        "items": {
            "iron_ore": (5, 10),
            "steel_bar": (3, 6),
            "magic_crystal": (2, 4),
            "iron_sword": (1, 1),
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