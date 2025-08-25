#game_data.synthesis_room.py
from ui.ui_utils import print_header, press_enter_to_continue, loading_screen
import random

def manage_synthesis(game_state):
    """
    Улучшенная комната синтеза
    """
    heroes = game_state["heroes"]
    if len(heroes) < 2:
        print_header("⚗️ КОМНАТА СИНТЕЗА")
        print("❌ Недостаточно героев для синтеза (нужно минимум 2)")
        press_enter_to_continue()
        return

    while True:
        print_header("⚗️ КОМНАТА СИНТЕЗА")
        print("Выберите основного героя для усиления:")
        print("═" * 40)
        
        for i, hero in enumerate(heroes, 1):
            star_symbol = "★" * hero.star
            print(f"{i}. {hero.name} {star_symbol} (Ур. {hero.level})")
        print("0. ↩️ Назад")
        print()
        
        try:
            choice = int(input("🎯 Выбор основного героя: "))
        except ValueError:
            continue
            
        if choice == 0:
            return
        if 1 <= choice <= len(heroes):
            base_hero = heroes[choice - 1]
            break
        else:
            print("❌ Неверный выбор!")
            press_enter_to_continue()
    
    # Выбор героев для жертвоприношения
    sacrifices = []
    while True:
        print_header("⚗️ КОМНАТА СИНТЕЗА")
        print(f"Основной герой: {base_hero.name} (Ур. {base_hero.level})")
        print("Выберите героев для синтеза (через запятую):")
        print("═" * 40)
        
        available_heroes = [h for h in heroes if h != base_hero and h not in sacrifices]
        
        if not available_heroes:
            print("❌ Нет доступных героев для синтеза!")
            press_enter_to_continue()
            break
            
        for i, hero in enumerate(available_heroes, 1):
            star_symbol = "★" * hero.star
            print(f"{i}. {hero.name} {star_symbol} (Ур. {hero.level})")
        
        print("9. ✅ Завершить выбор")
        print("0. ↩️ Отмена")
        print()
        
        try:
            choice = input("🎯 Выбор героев: ")
            if choice == "0":
                return
            elif choice == "9":
                break
            else:
                indices = [int(idx.strip()) for idx in choice.split(",") if idx.strip().isdigit()]
                for idx in indices:
                    if 1 <= idx <= len(available_heroes):
                        sacrifice = available_heroes[idx - 1]
                        if sacrifice not in sacrifices:
                            sacrifices.append(sacrifice)
                            print(f"✅ Добавлен: {sacrifice.name}")
        except ValueError:
            continue
    
    if not sacrifices:
        print("❌ Не выбрано героев для синтеза!")
        press_enter_to_continue()
        return
    
    # Процесс синтеза
    print_header("⚗️ ПРОЦЕСС СИНТЕЗА")
    print(f"Основной герой: {base_hero.name}")
    print("Жертвы:")
    for hero in sacrifices:
        print(f"   - {hero.name} (Ур. {hero.level})")
    print()
    
    # Расчет бонусов
    total_exp = sum(hero.level * 50 for hero in sacrifices)
    stat_bonus_chance = 0.1 * len(sacrifices)  # 10% за каждого героя
    
    print(f"📈 Получено опыта: {total_exp}")
    print(f"🎲 Шанс усиления характеристик: {stat_bonus_chance*100:.1f}%")
    print()
    
    # Единая система подтверждения как везде
    print("1. ✅ Подтвердить синтез")
    print("2. ❌ Отменить")
    print()
    
    try:
        confirm = int(input("🎯 Ваш выбор: "))
    except ValueError:
        print("❌ Синтез отменён")
        press_enter_to_continue()
        return
    
    if confirm != 1:
        print("❌ Синтез отменён")
        press_enter_to_continue()
        return
    
    loading_screen(2, "🌀 Процесс синтеза")
    
    # Применяем опыт
    result = base_hero.add_experience(total_exp)
    if result:
        print(result)
    
    # Проверяем усиление характеристик
    stat_improved = False
    if random.random() < stat_bonus_chance:
        stats = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
        chosen_stat = random.choice(stats)
        current_value = getattr(base_hero, chosen_stat)
        setattr(base_hero, chosen_stat, current_value + 1)
        
        stat_names = {
            'strength': 'Сила', 'dexterity': 'Ловкость', 
            'constitution': 'Выносливость', 'intelligence': 'Интеллект',
            'wisdom': 'Мудрость', 'charisma': 'Харизма'
        }
        
        print(f"✨ {base_hero.name} получает +1 к {stat_names[chosen_stat]}!")
        stat_improved = True
    
    # Удаляем жертвенных героев
    for hero in sacrifices:
        if hero in game_state["heroes"]:
            game_state["heroes"].remove(hero)
    
    print(f"✅ Синтез завершён! Удалено героев: {len(sacrifices)}")
    if stat_improved:
        print("🎉 Получено дополнительное усиление характеристики!")
    
    press_enter_to_continue()