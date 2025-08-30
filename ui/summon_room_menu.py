# ui.summon_room_menu.py
from ui.ui_utils import print_header, press_enter_to_continue, loading_screen
from systems.summon_system import summon_hero, summon_crystal_hero, calculate_star_chance, calculate_premium_star_chance
from ui.visual_effects import VisualEffects
import random

def manage_summon(game_state):
    """
    Улучшенная комната призыва героев
    """
    while True:
        # Считаем только живых героев
        living_heroes = [h for h in game_state["heroes"] if h.is_alive]
        current_heroes = len(living_heroes)
        
        dormitory = game_state["buildings"].get_building("dormitory")
        max_heroes = dormitory.get_capacity() if dormitory else 10  # Значение по умолчанию
        
        print_header("✨ ЗАЛ ПРИЗЫВА ГЕРОЕВ")
        print("Выберите тип призыва:")
        print("═" * 40)
        
        # Статистика ресурсов и героев
        print(f"💰 Золото: {game_state['wallet'].gold:>8}")
        print(f"💎 Кристаллы: {game_state['wallet'].crystals:>5}")
        print(f"👥 Героев: {current_heroes:>2}/{max_heroes:>2}")
        print("═" * 40)
        
        # Опции призыва
        print("1. 👥 Обычный призыв")
        print("   💰 500 золота")
        print()
        
        print("2. 👥 Премиум призыв")
        print("   💎 300 кристаллов")
        print()

        print("3. 📊 Просмотр шансов")
        print("0. ❌ Назад")
        print("═" * 40)

        try:
            choice = input("🎯 Ваш выбор: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                summon_gold_option(game_state)
            elif choice == "2":
                summon_crystal_option(game_state)
            elif choice == "3":
                show_chances_info()
            else:
                print("❌ Неверный выбор!")
                press_enter_to_continue()
                
        except (ValueError, KeyboardInterrupt):
            print("\n❌ Операция отменена")
            press_enter_to_continue()

def show_chances_info():
    """Показывает подробную информацию о шансах"""
    print_header("📊 ИНФОРМАЦИЯ О ШАНСАХ")
    
    print("🎯 Обычный призыв (500 золота):")
    print_chances_table(calculate_star_chance, {
        1: "★ Обычный (80%)",
        2: "★★ Необычный (17%)", 
        3: "★★★ Редкий (2.999%)",
        4: "★★★★ Эпический (0.001%)"
    })
    
    print("\n💎 Премиум призыв (300 кристаллов):")
    print_chances_table(calculate_premium_star_chance, {
        3: "★★★ Редкий (92%)",
        4: "★★★★ Эпический (5%)",
        5: "★★★★★ Легендарный (2.9999%)",
        6: "★★★★★★ Мифический (0.0001%)"
    })
    
    press_enter_to_continue()

def print_chances_table(calculate_func, rarity_names):
    """Печатает таблицу шансов без цветного форматирования"""
    print("┌────────────┬───────────────┐")
    print("│  Звёзды    │   Вероятность │")
    print("├────────────┼───────────────┤")
    
    if calculate_func == calculate_star_chance:
        chances = {1: 80.0, 2: 17.0, 3: 2.999, 4: 0.001}
        star_displays = {
            1: "★",
            2: "★★", 
            3: "★★★",
            4: "★★★★"
        }
    else:
        chances = {3: 92.0, 4: 5.0, 5: 2.9999, 6: 0.0001}
        star_displays = {
            3: "★★★",
            4: "★★★★",
            5: "★★★★★",
            6: "★★★★★★"
        }
    
    for stars, prob in chances.items():
        star_display = star_displays[stars].ljust(10)
        
        if prob < 1:
            prob_str = f"{prob:>12.4f}%"
        else:
            prob_str = f"{prob:>12.1f}%"
        
        print(f"│ {star_display} │ {prob_str} │")
    
    print("└────────────┴───────────────┘")

def summon_gold_option(game_state):
    """Обычный призыв за золото"""
    # Проверяем лимит героев
    living_heroes = [h for h in game_state["heroes"] if h.is_alive]
    current_heroes = len(living_heroes)
    dormitory = game_state["buildings"].get_building("dormitory")
    max_heroes = dormitory.get_capacity() if dormitory else 10
    
    if current_heroes >= max_heroes:
        print_header("❌ ЛИМИТ ГЕРОЕВ")
        print(f"Достигнут максимальный лимит героев: {current_heroes}/{max_heroes}")
        print("Улучшите Общежитие, чтобы увеличить вместимость")
        press_enter_to_continue()
        return
    
    cost = 500
    if game_state["wallet"].gold < cost:
        print_header("❌ НЕДОСТАТОЧНО ЗОЛОТА")
        print(f"Требуется: {cost} золота")
        print(f"Доступно: {game_state['wallet'].gold} золота")
        press_enter_to_continue()
        return
    
    # Подтверждение призыва
    if not confirm_summon("Обычный призыв", f"{cost} золота", "gold"):
        return
    
    # Выполняем призыв
    loading_screen(3, "🌀 Призыв героя...")
    result = summon_hero(game_state)
    
    if result:
        show_summon_result(result)
    else:
        print("❌ Ошибка при призыве героя")
    
    press_enter_to_continue()

def summon_crystal_option(game_state):
    """Премиум призыв за кристаллы"""
    # Проверяем уровень башни
    if game_state.get("tower_level", 0) < 5:
        print_header("🔒 НЕДОСТУПНО")
        print("Премиум призыв доступен с 5 уровня башни")
        print(f"Текущий уровень башни: {game_state.get('tower_level', 0)}")
        press_enter_to_continue()
        return
    
    crystal_cost = 300
    if game_state["wallet"].crystals < crystal_cost:
        print_header("❌ НЕДОСТАТОЧНО КРИСТАЛЛОВ")
        print(f"Требуется: {crystal_cost} кристаллов")
        print(f"Доступно: {game_state['wallet'].crystals} кристаллов")
        press_enter_to_continue()
        return
    
    # Проверяем лимит героев
    living_heroes = [h for h in game_state["heroes"] if h.is_alive]
    current_heroes = len(living_heroes)
    dormitory = game_state["buildings"].get_building("dormitory")
    max_heroes = dormitory.get_capacity() if dormitory else 10
    
    if current_heroes >= max_heroes:
        print_header("❌ ЛИМИТ ГЕРОЕВ")
        print(f"Достигнут максимальный лимит героев: {current_heroes}/{max_heroes}")
        press_enter_to_continue()
        return
    
    # Подтверждение призыва
    if not confirm_summon("Премиум призыв", f"{crystal_cost} кристаллов", "crystal"):
        return
    
    # Выполняем премиум призыв
    loading_screen(4, "🌀 Премиум призыв...")
    result = summon_crystal_hero(game_state)
    
    if result:
        show_summon_result(result)
    else:
        print("❌ Ошибка при премиум призыве")
    
    press_enter_to_continue()

def confirm_summon(summon_type, cost, currency_type):
    """Универсальная функция подтверждения призыва"""
    print_header(f"🎯 ПОДТВЕРЖДЕНИЕ {summon_type.upper()}")
    print(f"Стоимость: {cost}")
    
    if currency_type == "gold":
        print("Шансы получения:")
        print("★ - 80% (Обычный)")
        print("★★ - 17% (Необычный)")
        print("★★★ - 2.999% (Редкий)")
        print("★★★★ - 0.001% (Эпический)")
    else:
        print("Шансы получения:")
        print("★★★ - 92% (Редкий)")
        print("★★★★ - 5% (Эпический)")
        print("★★★★★ - 2.9999% (Легендарный)")
        print("★★★★★★ - 0.0001% (Мифический)")
    
    print("═" * 40)
    print("1. ✅ Подтвердить призыв")
    print("0. ❌ Отменить")
    print("═" * 40)
    
    try:
        confirm = input("🎯 Ваш выбор: ").strip()
        if confirm != "1":
            print("❌ Призыв отменён")
            press_enter_to_continue()
            return False
        return True
    except (ValueError, KeyboardInterrupt):
        print("❌ Призыв отменён")
        press_enter_to_continue()
        return False

def show_summon_result(hero_data):
    """Показывает результат призыва"""
    print_header("🎉 ГЕРОЙ ПРИЗВАН!")
    print(f"Герой {hero_data['name']} присоединился к отряду!")
    
    # Отображаем звезды
    star_display = VisualEffects.get_star_display(hero_data['star'])
    print(f"✨ Звёздность: {star_display}")
    
    # Редкость в зависимости от звезд
    rarity = get_rarity_name(hero_data['star'])
    print(f"🏆 Редкость: {rarity}")
    
    # Специальное сообщение для высоких редкостей
    if hero_data['star'] >= 4:
        print("⚡ ВАУ! Вы получили редкого героя!")
    
    print("═" * 50)
    print("Для просмотра характеристик изучите технологию:")
    print("Понимание героев")
    print("═" * 50)

def get_rarity_name(star_level):
    """Возвращает название редкости по уровню звезд"""
    rarity_names = {
        1: "Обычный",
        2: "Необычный", 
        3: "Редкий",
        4: "Эпический",
        5: "Легендарный",
        6: "Мифический",
        7: "Божественный"
    }
    return rarity_names.get(star_level, "Неизвестно")