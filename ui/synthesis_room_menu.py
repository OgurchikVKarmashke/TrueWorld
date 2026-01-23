# synthesis_room_menu.py
# ui.synthesis_room_menu.py
from ui.ui_utils import print_header, press_enter_to_continue, loading_screen
from systems.party_system import PartySystem
from systems.hero_system import calculate_exp_requirement
from systems.synthesis_room_system import synthesize_heroes, get_available_heroes
from ui.visual_effects import VisualEffects 

def manage_synthesis(game_state):
    """
    Улучшенная комната синтеза - более логичное меню
    """
    # Очищаем мёртвых героев перед началом
    PartySystem(game_state).cleanup_dead_heroes()
    
    heroes = [hero for hero in game_state["heroes"] if hero.is_alive]  # Только живые герои
    
    if len(heroes) < 2:
        print_header("⚗️ КОМНАТА СИНТЕЗА")
        print("❌ Недостаточно героев для синтеза (нужно минимум 2)")
        press_enter_to_continue()
        return

    while True:
        print_header("⚗️ КОМНАТА СИНТЕЗА")
        print("Выберите действие:")
        print("═" * 40)
        print("1. 🎯 Выбрать основного героя для усиления")
        print("2. 📋 Показать всех доступных героев")
        print("0. ↩️ Вернуться назад")
        print("═" * 40)
        
        try:
            choice = input("🎯 Ваш выбор: ").strip()
            
            if choice == "0":
                return
            elif choice == "1":
                if select_base_hero_and_sacrifices(game_state, heroes):
                    return  # Возвращаемся после успешного синтеза
            elif choice == "2":
                show_all_available_heroes(heroes)
            else:
                print("❌ Неверный выбор!")
                press_enter_to_continue()
                
        except (ValueError, KeyboardInterrupt):
            print("\n❌ Операция отменена")
            press_enter_to_continue()

def select_base_hero_and_sacrifices(game_state, heroes):
    """Выбор основного героя и жертв для синтеза"""
    # Выбор основного героя
    base_hero = select_base_hero(heroes)
    if base_hero is None:
        return False
    
    # Выбор героев для жертвоприношения
    sacrifices = select_sacrifice_heroes(heroes, base_hero)
    if sacrifices is None:  # Пользователь отменил
        return False
    
    if not sacrifices:
        print("❌ Не выбрано героев для синтеза!")
        press_enter_to_continue()
        return False
    
    # Показываем предварительную информацию
    show_synthesis_preview(base_hero, sacrifices)
    
    # Подтверждение
    if confirm_synthesis():
        loading_screen(2, "🌀 Процесс синтеза")
        # Выполняем синтез
        result_message, stat_improved, stat_name = synthesize_heroes(game_state, base_hero, sacrifices)
        show_synthesis_result(result_message, stat_improved, stat_name, len(sacrifices))
        # Очищаем мёртвых героев после синтеза
        PartySystem(game_state).cleanup_dead_heroes()
        press_enter_to_continue()
        return True
    
    return False

def select_base_hero(heroes):
    """Выбор основного героя для усиления"""
    while True:
        print_header("🎯 ВЫБОР ОСНОВНОГО ГЕРОЯ")
        print("Выберите героя, которого хотите усилить:")
        print("═" * 40)
        
        # Кнопка 0 - отмена
        print("0. ↩️ Назад")
        
        # Сортируем героев по уровню и звездам для удобства
        sorted_heroes = sorted(heroes, key=lambda x: (x.star, x.level), reverse=True)
        
        for i, hero in enumerate(sorted_heroes, 1):
            star_display = VisualEffects.get_star_display(hero.star)
            # Фиксированная ширина для выравнивания
            name_padding = 20 - len(hero.name)
            print(f"{i}. {hero.name}{' ' * name_padding}{star_display} (Ур. {hero.level})")
        print()
        
        try:
            choice = input("🎯 Выбор героя: ").strip()
            
            if choice == "0":
                return None
                
            choice_num = int(choice)
            if 1 <= choice_num <= len(sorted_heroes):
                return sorted_heroes[choice_num - 1]
            else:
                print("❌ Неверный выбор!")
                press_enter_to_continue()
                
        except ValueError:
            print("❌ Введите число!")
            press_enter_to_continue()

def select_sacrifice_heroes(heroes, base_hero):
    """Выбор героев для жертвоприношения"""
    sacrifices = []
    
    while True:
        print_header("🔥 ВЫБОР ГЕРОЕВ ДЛЯ СИНТЕЗА")
        print(f"Основной герой: {base_hero.name} (Ур. {base_hero.level})")
        print(f"Выбрано жертв: {len(sacrifices)}")
        print("═" * 40)
        
        available_heroes = get_available_heroes(heroes, base_hero, sacrifices)
        
        if not available_heroes:
            print("❌ Все герои кончились, переходим к синтезу...")
            press_enter_to_continue()
            break
            
        print("Доступные герои:")
        print("-" * 40)
        
        # Сортируем доступных героев
        sorted_available = sorted(available_heroes, key=lambda x: (x.star, x.level), reverse=True)
        
        for i, hero in enumerate(sorted_available, 1):
            star_display = VisualEffects.get_star_display(hero.star)
            status = "✅" if hero in sacrifices else "  "
            # Фиксированная ширина для выравнивания
            name_padding = 18 - len(hero.name)
            print(f"{status} {i}. {hero.name}{' ' * name_padding}{star_display} (Ур. {hero.level})")
        
        print("═" * 40)
        print("Команды:")
        print("C - Очистить все выборы")
        print("F - Завершить выбор")
        print("0 - ↩️ Отмена")
        print("═" * 40)
        
        try:
            choice = input("🎯 Ваш выбор: ").strip().upper()
            
            if choice == "0":
                return None
            elif choice == "F":
                break
            elif choice == "C":
                sacrifices.clear()
                print("✅ Выборы очищены")
                continue
            elif choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(sorted_available):
                    selected_hero = sorted_available[choice_num - 1]
                    if selected_hero in sacrifices:
                        sacrifices.remove(selected_hero)
                        print(f"❌ Удален: {selected_hero.name}")
                    else:
                        sacrifices.append(selected_hero)
                        print(f"✅ Добавлен: {selected_hero.name}")
                else:
                    print("❌ Неверный номер!")
            else:
                print("❌ Неверная команда!")
                
            press_enter_to_continue()
            
        except ValueError:
            print("❌ Ошибка ввода!")
            press_enter_to_continue()
    
    return sacrifices

def show_all_available_heroes(heroes):
    """Показывает всех доступных героев с группировкой по звездам"""
    print_header("📋 ВСЕ ДОСТУПНЫЕ ГЕРОИ")
    print("Список всех живых героев:")
    print("═" * 50)
    
    if not heroes:
        print("❌ Нет доступных героев!")
        press_enter_to_continue()
        return
    
    # Группируем героев по количеству звезд
    heroes_by_stars = {}
    for hero in heroes:
        if hero.star not in heroes_by_stars:
            heroes_by_stars[hero.star] = []
        heroes_by_stars[hero.star].append(hero)
    
    # Сортируем группы по убыванию звезд
    sorted_stars = sorted(heroes_by_stars.keys(), reverse=True)
    
    for star_level in sorted_stars:
        star_group = heroes_by_stars[star_level]
        
        # Сортируем героев в группе по уровню
        sorted_heroes = sorted(star_group, key=lambda x: x.level, reverse=True)
        
        # Выводим заголовок для группы звезд
        star_display = VisualEffects.get_star_display(star_level)
        print(f"\n🌟 {star_display} Герои ({len(sorted_heroes)}):")
        print("-" * 40)
        
        for i, hero in enumerate(sorted_heroes, 1):
            # Форматируем строку с фиксированными отступами
            name_part = f"{hero.name:<15}"
            level_part = f"Ур. {hero.level:>2}"
            
            print(f"  {i:2d}. {name_part}{level_part}")
    
    print("═" * 50)
    press_enter_to_continue()

def show_synthesis_preview(base_hero, sacrifices):
    """Показывает предпросмотр синтеза"""
    print_header("⚗️ ПРЕДПРОСМОТР СИНТЕЗА")
    print(f"🎯 Основной герой: {base_hero.name} (Ур. {base_hero.level})")
    print(f"   Текущий опыт: {base_hero.experience}/{base_hero.exp_to_next_level}")
    print("🔥 Жертвы:")
    
    total_exp = 0
    for hero in sacrifices:
        # ТА ЖЕ ФОРМУЛА, ЧТО И В calculate_synthesis_bonuses
        star_multiplier = 1.0 + (hero.star - 1) * 0.5  # 50% за каждую звезду
        hero_exp = int((hero.level ** 2) * 50 * star_multiplier)
        total_exp += hero_exp
        print(f"   - {hero.name} (Ур. {hero.level}, ★{hero.star}) → {hero_exp} опыта")
    
    print("═" * 40)
    
    # Показываем точный расчет уровня
    current_exp = base_hero.experience
    exp_after = current_exp + total_exp
    level = base_hero.level
    exp_needed_for_next = base_hero.exp_to_next_level
    
    # Симулируем повышение уровней
    temp_exp = exp_after
    temp_level = level
    levels_gained = 0
    
    while temp_exp >= calculate_exp_requirement(temp_level) and temp_level < 120:  # 120 - максимальный уровень
        temp_exp -= calculate_exp_requirement(temp_level)
        temp_level += 1
        levels_gained += 1
    
    # Расчет бонусов (копируем из synthesis_room_system.py)
    base_chance = 0.1
    star_bonus = sum((hero.star - 1) * 0.05 for hero in sacrifices)
    stat_bonus_chance = base_chance * len(sacrifices) + star_bonus
    stat_bonus_chance = min(stat_bonus_chance, 0.8)
    
    print(f"📊 Общий опыт: {total_exp}")
    print(f"📈 Опыт после синтеза: {exp_after}")
    
    if levels_gained > 0:
        print(f"🎯 Новый уровень: {temp_level} (+{levels_gained})")
    else:
        exp_needed = calculate_exp_requirement(level) - exp_after
        print(f"🎯 До следующего уровня: {exp_needed} опыта")
    
    print(f"🎲 Шанс усиления характеристики: {stat_bonus_chance*100:.1f}%")
    print("═" * 40)

def confirm_synthesis():
    """Запрос подтверждения синтеза"""
    print("⚠️ ВНИМАНИЕ: Герои-жертвы будут удалены навсегда!")
    print("1. ✅ Подтвердить синтез")
    print("0. ❌ Отменить")
    print("═" * 40)
    
    try:
        confirm = input("🎯 Ваш выбор: ").strip()
        return confirm == "1"
    except (ValueError, KeyboardInterrupt):
        print("❌ Синтез отменён")
        return False

def show_synthesis_result(result_message, stat_improved, stat_name, sacrifices_count):
    """Показывает результат синтеза"""
    print_header("✨ РЕЗУЛЬТАТ СИНТЕЗА")
    
    # Разделяем сообщение на строки и выводим красиво
    lines = result_message.split('\n')
    for line in lines:
        if line.strip():  # Пропускаем пустые строки
            print(line)
    
    print(f"✅ Успешно синтезировано! Удалено героев: {sacrifices_count}")
    
    # Показываем улучшение характеристики только если оно было
    if stat_improved and stat_name:
        print(f"🎉 Получено дополнительное усиление: +1 к {stat_name}!")
    
    print("═" * 40)