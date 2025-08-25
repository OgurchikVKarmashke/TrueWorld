# summon_system.py
from ui.ui_utils import loading_screen, press_enter_to_continue, print_header
from systems.hero_system import Hero
import random

def summon_hero(game_state):
    """
    Система призыва героев за золото
    """
    # Получаем информацию о лимите героев
    dormitory = game_state["buildings"].get_building("dormitory")
    current_heroes = len(game_state["heroes"])
    max_heroes = dormitory.get_capacity()  # ✅ Используем get_capacity()
    
    # Проверяем достигнут ли лимит
    if current_heroes >= max_heroes:
        print_header("Призыв героя")
        print("Достигнут лимит героев!")
        print(f"Героев: {current_heroes}/{max_heroes}")
        print("Улучшите Общежитие, чтобы увеличить лимит")
        press_enter_to_continue()
        return
    
    cost = 50  # Фиксированная стоимость
    
    print_header("✨ Призыв героя")
    print(f"💰 Золото: {game_state['wallet'].gold}")
    print(f"💎 Кристаллы: {game_state['wallet'].crystals}")
    print(f"👥 Героев: {current_heroes}/{max_heroes}")
    print(f"💵 Стоимость призыва: {cost} золота")
    print()
    
    if game_state["wallet"].subtract_gold(cost):
        loading_screen(2, "🌀 Призыв героя")
        
        # НОВАЯ СИСТЕМА ЗВЁЗД
        star_level = calculate_star_chance()
        new_hero = Hero(star=star_level)
        game_state["heroes"].append(new_hero)
        
        print_header("🎉 Герой призван!")
        print(f"Герой {new_hero.name} присоединился к вашему отряду!")
        print(f"✨ Звёздность: {star_level}★")
        print(f"📈 Уровень: 1")
        print("🎭 Характер и характеристики скрыты")
        print(f"👥 Героев: {len(game_state['heroes'])}/{max_heroes}")
        
    else:
        print("❌ Недостаточно золота для призыва!")
    
    press_enter_to_continue()
    game_state["save_system"].save_game(game_state, 1)

def calculate_star_chance():
    """
    Система шансов звёзд:
    1★ - 70% (обычный)
    2★ - 25% (необычный) 
    3★ - 4.9% (редкий)
    4★ - 0.1% (эпический)
    """
    roll = random.random() * 100  # 0-100
    
    if roll < 70:
        return 1
    elif roll < 95:  # 70 + 25 = 95
        return 2
    elif roll < 99.9:  # 95 + 4.9 = 99.9
        return 3
    else:
        return 4

def summon_crystal_hero(game_state):
    """
    Премиум призыв за кристаллы (для высоких звёзд)
    """
    # Будет реализовано позже
    print_header("Призыв за кристаллы")
    print("Система в разработке...")
    print("Здесь будут доступны герои 5-7★")
    press_enter_to_continue()