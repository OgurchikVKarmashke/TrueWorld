# synthesis_room_menu.py
# ui.synthesis_room_menu.py
from ui.ui_utils import print_header, press_enter_to_continue, loading_screen
from systems.synthesis_room_system import synthesize_heroes, get_available_heroes

def manage_synthesis(game_state):
    """
    Улучшенная комната синтеза - визуальная часть
    """
    heroes = game_state["heroes"]
    if len(heroes) < 2:
        print_header("⚗️ КОМНАТА СИНТЕЗА")
        print("❌ Недостаточно героев для синтеза (нужно минимум 2)")
        press_enter_to_continue()
        return

    while True:
        print_header("⚗️ КОМНАТА СИНТЕЗA")
        print("Выберите основного героя для усиления:")
        print("═" * 40)
        
        # Кнопка 0 - отмена
        print("0. ↩️ Назад")
        
        # Герои начинаются с 2
        for i, hero in enumerate(heroes, 2):
            star_symbol = "★" * hero.star
            print(f"{i}. {hero.name} {star_symbol} (Ур. {hero.level})")
        print()
        
        try:
            choice = int(input("🎯 Выбор основного героя: "))
        except ValueError:
            continue
            
        if choice == 0:
            return
        if 2 <= choice <= len(heroes) + 1:
            base_hero = heroes[choice - 2]  # Корректируем индекс
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
        
        available_heroes = get_available_heroes(heroes, base_hero, sacrifices)
        
        if not available_heroes:
            print("❌ Нет доступных героев для синтеза!")
            press_enter_to_continue()
            break
            
        # Кнопка 0 - отмена, 1 - завершить
        print("0. ↩️ Отмена")
        print("1. ✅ Завершить выбор")
        
        # Герои начинаются с 2
        for i, hero in enumerate(available_heroes, 2):
            star_symbol = "★" * hero.star
            print(f"{i}. {hero.name} {star_symbol} (Ур. {hero.level})")
        print()
        
        try:
            choice = input("🎯 Выбор героев: ")
            if choice == "0":
                return
            elif choice == "1":
                break
            else:
                indices = [int(idx.strip()) for idx in choice.split(",") if idx.strip().isdigit()]
                for idx in indices:
                    if idx >= 2:  # Только герои (начиная с 2)
                        adjusted_idx = idx - 2  # Корректируем индекс
                        if 0 <= adjusted_idx < len(available_heroes):
                            sacrifice = available_heroes[adjusted_idx]
                            if sacrifice not in sacrifices:
                                sacrifices.append(sacrifice)
                                print(f"✅ Добавлен: {sacrifice.name}")
        except ValueError:
            continue
    
    if not sacrifices:
        print("❌ Не выбрано героев для синтеза!")
        press_enter_to_continue()
        return
    
    # Показываем предварительную информацию
    show_synthesis_preview(base_hero, sacrifices)
    
    # Подтверждение
    if confirm_synthesis():
        loading_screen(2, "🌀 Процесс синтеза")
        # Выполняем синтез
        result_message, stat_improved = synthesize_heroes(game_state, base_hero, sacrifices)
        show_synthesis_result(result_message, stat_improved, len(sacrifices))
    
    press_enter_to_continue()

def show_synthesis_preview(base_hero, sacrifices):
    """Показывает предпросмотр синтеза"""
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

def confirm_synthesis():
    """Запрос подтверждения синтеза"""
    print("1. ✅ Подтвердить синтез")
    print("0. ❌ Отменить")
    print()
    
    try:
        confirm = int(input("🎯 Ваш выбор: "))
        return confirm == 1
    except ValueError:
        print("❌ Синтез отменён")
        return False

def show_synthesis_result(result_message, stat_improved, sacrifices_count):
    """Показывает результат синтеза"""
    print(result_message)
    print(f"✅ Синтез завершён! Удалено героев: {sacrifices_count}")
    if stat_improved:
        print("🎉 Получено дополнительное усиление характеристики!")