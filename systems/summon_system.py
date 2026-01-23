# systems.summon_system.py
from ui.ui_utils import loading_screen, press_enter_to_continue, print_header
from systems.hero_system import Hero
from ui.visual_effects import VisualEffects
import random

def summon_hero(game_state):
    """
    Система призыва героев за золото
    Возвращает данные о призванном герое
    """
    cost = 500
    if not game_state["wallet"].subtract_gold(cost):
        return None
    
    star_level = calculate_star_chance()
    new_hero = Hero(star=star_level)
    game_state["heroes"].append(new_hero)
    
    # АВТОСОХРАНЕНИЕ
    if "save_system" in game_state:
        try:
            game_state["save_system"].save_game(game_state, 1)
        except Exception:
            pass  # Игнорируем ошибки сохранения
    
    return {
        'name': new_hero.name,
        'star': star_level,
        'level': 1
    }

def summon_crystal_hero(game_state):
    """
    Премиум призыв за кристаллы
    Возвращает данные о призванном герое
    """
    crystal_cost = 300
    if not game_state["wallet"].subtract_crystals(crystal_cost):
        return None
    
    star_level = calculate_premium_star_chance()
    new_hero = Hero(star=star_level)
    game_state["heroes"].append(new_hero)
    
    # АВТОСОХРАНЕНИЕ
    if "save_system" in game_state:
        try:
            game_state["save_system"].save_game(game_state, 1)
        except Exception:
            pass  # Игнорируем ошибки сохранения
    
    return {
        'name': new_hero.name,
        'star': star_level,
        'level': 1
    }
    
def calculate_star_chance():
    """
    Система шансов звёзд для обычного призыва:
    1★ - 80% (обычный)
    2★ - 17% (необычный) 
    3★ - 2.999% (редкий)
    4★ - 0.001% (эпический)
    """
    chances = {
        1: 80.0,    # 80%
        2: 17.0,    # 17%
        3: 2.999,   # 2.999%
        4: 0.001    # 0.001%
    }
    
    return weighted_random_selection(chances)

def calculate_premium_star_chance():
    """
    Система шансов звёзд для премиум призыва:
    3★ - 92% (редкий)
    4★ - 5% (эпический)
    5★ - 2.9999% (легендарный)
    6★ - 0.0001% (мифический)
    """
    chances = {
        3: 92.0,     # 92%
        4: 5.0,      # 5%
        5: 2.9999,   # 2.9999%
        6: 0.0001    # 0.0001%
    }
    
    return weighted_random_selection(chances)

def weighted_random_selection(chances_dict):
    """
    Универсальная функция для взвешенного случайного выбора
    chances_dict: словарь {значение: вероятность в процентах}
    """
    total = sum(chances_dict.values())
    if abs(total - 100.0) > 0.001:
        # Нормализуем вероятности, если они не суммируются в 100%
        normalized_chances = {}
        for key, value in chances_dict.items():
            normalized_chances[key] = (value / total) * 100
        chances_dict = normalized_chances
    
    roll = random.uniform(0, 100)
    cumulative = 0
    
    for value, probability in chances_dict.items():
        cumulative += probability
        if roll <= cumulative:
            return value
    
    # На всякий случай возвращаем последнее значение
    return list(chances_dict.keys())[-1]